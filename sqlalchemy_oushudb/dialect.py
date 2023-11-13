""" Customizes the postgresql.psycopg2 dialect to work with OushuDB. """

from sqlalchemy.dialects.postgresql import pg_catalog, psycopg2
from sqlalchemy.dialects.postgresql.array import array as _array
from sqlalchemy import schema, select, bindparam, sql, util
from sqlalchemy.types import TEXT
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.expression import Delete
from sqlalchemy.sql.schema import Table

from functools import lru_cache
from .ddl import OushuDBDDLCompiler


class OushuDBDialect(psycopg2.PGDialect_psycopg2):
    '''
    Main dialect class. Used by the engine to compile sql
    '''

    construct_arguments = [
        (
            schema.Table,
            {
                'partition_by': None,
                'inherits': None,
                'distributed_by': None,
                'bucketnum': None,
                'appendonly': None,
                'orientation': None,
                'compresstype': None,
                'compresslevel': None,
                'on_commit': None,
                'tablespace': None,
            },
        )
    ]
    ddl_compiler = OushuDBDDLCompiler
    name = 'oushudb'
    supports_statement_cache = False

    def initialize(self, connection):
        """
        Override implicit_returning = True of postgresql dialect
        """
        super().initialize(connection)

        self.implicit_returning = False
        self.supports_native_uuid = False
        self.update_returning = False
        self.delete_returning = False
        self.insert_returning = False
        self.update_returning_multifrom = False
        self.delete_returning_multifrom = False

    @compiles(Delete, 'oushu')
    def visit_delete_statement(element, compiler, **kwargs):  # pylint: disable=no-self-argument
        """
        Allows a version of the delete statement to get compiled - the version
        that is effectively the same as truncate.

        Any filters on the delete statement result in an Exception.
        """
        delete_stmt_table = compiler.process(element.table, asfrom=True, **kwargs)
        filters_tuple = element.get_children()
        if not filters_tuple:
            return 'TRUNCATE TABLE {}'.format(delete_stmt_table)
        items = [item for item in element.get_children()]

        # check if filters_tuple contains only one item, and it's the table
        if (
            len(items) == 1
            and isinstance(items[0], Table)
            and compiler.process(items[0], asfrom=True, **kwargs) == delete_stmt_table
        ):
            return 'TRUNCATE TABLE {}'.format(delete_stmt_table)

        # TODO：OushuDB Delete statement
        raise NotImplementedError('Delete statement with filter clauses not implemented')

    def get_isolation_level_values(self, dbapi_conn):
        # note the generic dialect doesn't have AUTOCOMMIT, however
        # all postgresql dialects should include AUTOCOMMIT.
        return (
            "AUTOCOMMIT",
            "SERIALIZABLE",
            "REPEATABLE READ",
            "READ UNCOMMITTED",
            "READ COMMITTED",
        )
    
    def _pg_class_filter_scope_schema(
        self, query, schema, scope, pg_class_table=None
    ):
        # GP/OushuDB: column pg_class.relpersistence not exist
        if pg_class_table is None:
            pg_class_table = pg_catalog.pg_class
        query = query.join(
            pg_catalog.pg_namespace,
            pg_catalog.pg_namespace.c.oid == pg_class_table.c.relnamespace,
        )

        # if scope is ObjectScope.DEFAULT:
        #     query = query.where(pg_class_table.c.relpersistence != "t")
        # elif scope is ObjectScope.TEMPORARY:
        #     query = query.where(pg_class_table.c.relpersistence == "t")

        if schema is None:
            query = query.where(
                pg_catalog.pg_table_is_visible(pg_class_table.c.oid),
                # ignore pg_catalog schema
                pg_catalog.pg_namespace.c.nspname != "pg_catalog",
            )
        else:
            query = query.where(pg_catalog.pg_namespace.c.nspname == schema)
        return query
    
    @lru_cache()
    def _enum_query(self, schema):
        # GP/OushuDB: column pg_enum.enumtypid not exist
        
        # lbl_agg_sq = (
        #     select(
        #         pg_catalog.pg_enum.c.enumtypid,
        #         sql.func.array_agg(
        #             aggregate_order_by(
        #                 # NOTE: cast since some postgresql derivatives may
        #                 # not support array_agg on the name type
        #                 pg_catalog.pg_enum.c.enumlabel.cast(TEXT),
        #                 pg_catalog.pg_enum.c.enumsortorder,
        #             )
        #         ).label("labels"),
        #     )
        #     .group_by(pg_catalog.pg_enum.c.enumtypid)
        #     .subquery("lbl_agg")
        # )

        query = (
            select(
                pg_catalog.pg_type.c.typname.label("name"),
                pg_catalog.pg_type_is_visible(pg_catalog.pg_type.c.oid).label(
                    "visible"
                ),
                pg_catalog.pg_namespace.c.nspname.label("schema"),
                # lbl_agg_sq.c.labels.label("labels"),
                pg_catalog.pg_type.c.typname.label("labels"),
            )
            .join(
                pg_catalog.pg_namespace,
                pg_catalog.pg_namespace.c.oid
                == pg_catalog.pg_type.c.typnamespace,
            )
            # .outerjoin(
            #     lbl_agg_sq, pg_catalog.pg_type.c.oid == lbl_agg_sq.c.enumtypid
            # )
            .where(pg_catalog.pg_type.c.typtype == "e")
            .order_by(
                pg_catalog.pg_namespace.c.nspname, pg_catalog.pg_type.c.typname
            )
        )

        return self._pg_type_filter_schema(query, schema)
    
    @util.memoized_property
    def _index_query(self):
        # GP/OushuDB: function generate_subscripts(anyarray, integer) not exists
        # GP/OushuDB: column pg_index.indoption not exists
        pg_class_index = pg_catalog.pg_class.alias("cls_idx")
        # NOTE: repeating oids clause improve query performance

        # subquery to get the columns
        idx_sq = (
            select(
                pg_catalog.pg_index.c.indexrelid,
                pg_catalog.pg_index.c.indrelid,
                sql.func.unnest(pg_catalog.pg_index.c.indkey).label("attnum"),
                # sql.func.generate_subscripts_array(
                #     pg_catalog.pg_index.c.indkey, 1
                # ).label("ord"),
            )
            .where(
                ~pg_catalog.pg_index.c.indisprimary,
                pg_catalog.pg_index.c.indrelid.in_(bindparam("oids")),
            )
            .subquery("idx")
        )

        attr_sq = (
            select(
                idx_sq.c.indexrelid,
                idx_sq.c.indrelid,
                # idx_sq.c.ord,
                # NOTE: always using pg_get_indexdef is too slow so just
                # invoke when the element is an expression
                # sql.case(
                #     (
                #         idx_sq.c.attnum == 0,
                #         pg_catalog.pg_get_indexdef(
                #             idx_sq.c.indexrelid, idx_sq.c.ord + 1, True
                #         ),
                #     ),
                #     # NOTE: need to cast this since attname is of type "name"
                #     # that's limited to 63 bytes, while pg_get_indexdef
                #     # returns "text" so its output may get cut
                #     else_=pg_catalog.pg_attribute.c.attname.cast(TEXT),
                # ).label("element"),
                pg_catalog.pg_attribute.c.attname.cast(TEXT).label("element"),
                (idx_sq.c.attnum == 0).label("is_expr"),
            )
            .select_from(idx_sq)
            .outerjoin(
                # do not remove rows where idx_sq.c.attnum is 0
                pg_catalog.pg_attribute,
                sql.and_(
                    pg_catalog.pg_attribute.c.attnum == idx_sq.c.attnum,
                    pg_catalog.pg_attribute.c.attrelid == idx_sq.c.indrelid,
                ),
            )
            .where(idx_sq.c.indrelid.in_(bindparam("oids")))
            .subquery("idx_attr")
        )

        cols_sq = (
            select(
                attr_sq.c.indexrelid,
                sql.func.min(attr_sq.c.indrelid),
                sql.func.array_agg(
                    # aggregate_order_by(attr_sq.c.element, attr_sq.c.ord)
                    attr_sq.c.element
                ).label("elements"),
                sql.func.array_agg(
                    # aggregate_order_by(attr_sq.c.is_expr, attr_sq.c.ord)
                    attr_sq.c.is_expr
                ).label("elements_is_expr"),
            )
            .group_by(attr_sq.c.indexrelid)
            .subquery("idx_cols")
        )

        if self.server_version_info >= (11, 0):
            indnkeyatts = pg_catalog.pg_index.c.indnkeyatts
        else:
            indnkeyatts = sql.null().label("indnkeyatts")

        if self.server_version_info >= (15,):
            nulls_not_distinct = pg_catalog.pg_index.c.indnullsnotdistinct
        else:
            nulls_not_distinct = sql.false().label("indnullsnotdistinct")

        return (
            select(
                pg_catalog.pg_index.c.indrelid,
                pg_class_index.c.relname.label("relname_index"),
                pg_catalog.pg_index.c.indisunique,
                pg_catalog.pg_constraint.c.conrelid.is_not(None).label(
                    "has_constraint"
                ),
                # pg_catalog.pg_index.c.indoption,
                pg_catalog.pg_index.c.indclass.label("indoption"),
                pg_class_index.c.reloptions,
                pg_catalog.pg_am.c.amname,
                # NOTE: pg_get_expr is very fast so this case has almost no
                # performance impact
                sql.case(
                    (
                        pg_catalog.pg_index.c.indpred.is_not(None),
                        pg_catalog.pg_get_expr(
                            pg_catalog.pg_index.c.indpred,
                            pg_catalog.pg_index.c.indrelid,
                        ),
                    ),
                    else_=None,
                ).label("filter_definition"),
                indnkeyatts,
                nulls_not_distinct,
                cols_sq.c.elements,
                cols_sq.c.elements_is_expr,
            )
            .select_from(pg_catalog.pg_index)
            .where(
                pg_catalog.pg_index.c.indrelid.in_(bindparam("oids")),
                ~pg_catalog.pg_index.c.indisprimary,
            )
            .join(
                pg_class_index,
                pg_catalog.pg_index.c.indexrelid == pg_class_index.c.oid,
            )
            .join(
                pg_catalog.pg_am,
                pg_class_index.c.relam == pg_catalog.pg_am.c.oid,
            )
            .outerjoin(
                cols_sq,
                pg_catalog.pg_index.c.indexrelid == cols_sq.c.indexrelid,
            )
            .outerjoin(
                pg_catalog.pg_constraint,
                sql.and_(
                    pg_catalog.pg_index.c.indrelid
                    == pg_catalog.pg_constraint.c.conrelid,
                    # pg_catalog.pg_index.c.indexrelid
                    # == pg_catalog.pg_constraint.c.conindid,
                    pg_catalog.pg_constraint.c.contype
                    == sql.any_(_array(("p", "u", "x"))),
                ),
            )
            .order_by(pg_catalog.pg_index.c.indrelid, pg_class_index.c.relname)
        )
    
    @lru_cache()
    def _constraint_query(self, is_unique):
        # GP/OushuDB: function generate_subscripts(anyarray, integer) not exists
        # GP/OushuDB: column pg_constraint.conindid not exists
        con_sq = (
            select(
                pg_catalog.pg_constraint.c.conrelid,
                pg_catalog.pg_constraint.c.conname,
                sql.literal(1).label("conindid"),
                sql.func.unnest(pg_catalog.pg_constraint.c.conkey).label(
                    "attnum"
                ),
                # sql.func.generate_subscripts_array(
                #     pg_catalog.pg_constraint.c.conkey, 1
                # ).label("ord"),
                pg_catalog.pg_description.c.description,
            )
            .outerjoin(
                pg_catalog.pg_description,
                pg_catalog.pg_description.c.objoid
                == pg_catalog.pg_constraint.c.oid,
            )
            .where(
                pg_catalog.pg_constraint.c.contype == bindparam("contype"),
                pg_catalog.pg_constraint.c.conrelid.in_(bindparam("oids")),
            )
            .subquery("con")
        )

        attr_sq = (
            select(
                con_sq.c.conrelid,
                con_sq.c.conname,
                con_sq.c.conindid,
                con_sq.c.description,
                # con_sq.c.ord,
                pg_catalog.pg_attribute.c.attname,
            )
            .select_from(pg_catalog.pg_attribute)
            .join(
                con_sq,
                sql.and_(
                    pg_catalog.pg_attribute.c.attnum == con_sq.c.attnum,
                    pg_catalog.pg_attribute.c.attrelid == con_sq.c.conrelid,
                ),
            )
            .where(
                # NOTE: restate the condition here, since pg15 otherwise
                # seems to get confused on pscopg2 sometimes, doing
                # a sequential scan of pg_attribute.
                # The condition in the con_sq subquery is not actually needed
                # in pg15, but it may be needed in older versions. Keeping it
                # does not seems to have any inpact in any case.
                con_sq.c.conrelid.in_(bindparam("oids"))
            )
            .subquery("attr")
        )

        constraint_query = (
            select(
                attr_sq.c.conrelid,
                sql.func.array_agg(
                    # NOTE: cast since some postgresql derivatives may
                    # not support array_agg on the name type
                    # aggregate_order_by(
                    #     attr_sq.c.attname.cast(TEXT), attr_sq.c.ord
                    # )
                    attr_sq.c.attname.cast(TEXT)
                ).label("cols"),
                attr_sq.c.conname,
                sql.func.min(attr_sq.c.description).label("description"),
            )
            .group_by(attr_sq.c.conrelid, attr_sq.c.conname)
            .order_by(attr_sq.c.conrelid, attr_sq.c.conname)
        )

        if is_unique:
            # if self.server_version_info >= (15,):
            #     constraint_query = constraint_query.join(
            #         pg_catalog.pg_index,
            #         attr_sq.c.conindid == pg_catalog.pg_index.c.indexrelid,
            #     ).add_columns(
            #         sql.func.bool_and(
            #             pg_catalog.pg_index.c.indnullsnotdistinct
            #         ).label("indnullsnotdistinct")
            #     )
            # else:
            constraint_query = constraint_query.add_columns(
                sql.false().label("indnullsnotdistinct")
            )
        else:
            constraint_query = constraint_query.add_columns(
                sql.null().label("extra")
            )
        return constraint_query