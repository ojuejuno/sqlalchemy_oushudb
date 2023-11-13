"""
Imports and modifies SQLAlchemy's Requirements class.

Markers from this class can be used to switch marked tests
on and off, so that only the functionality the dialect
supports is tested.
"""
from sqlalchemy.testing.requirements import SuiteRequirements
from sqlalchemy.testing import exclusions


class Requirements(SuiteRequirements):
    """
    Changes the settings of some requirements to work with Hawq.
    Adds some requirements specific to Hawq.
    """
    #  TODO： oushudb specifications
    
    @property
    def cross_schema_fk_reflection(self):
        """
        Requested by sqla test suite for ComponentReflectionTest,
        even though ComponentReflectionTests are disabled.
        """
        return exclusions.closed()

    @property
    def order_by_col_from_union(self):
        """
        Requested by sqla test for CompoundSelectTest
        """
        return exclusions.open()

    @property
    def duplicate_key_raises_integrity_error(self):
        """
        Hawq does not enforce primary key uniquing
        """
        return exclusions.closed()

    @property
    def uuid_data_type(self):
        """
        Hawq doesn't have a native uuid data type
        """
        return exclusions.closed()

    @property
    def array_type(self):
        """
        Hawq doesn't have this version of the postgresql array type
        """
        return exclusions.closed()

    @property
    def json_type(self):
        """
        Hawq doesn't have this version of the postgresql json type
        """
        return exclusions.closed()

    @property
    def reflect_indexes_with_ascdesc(self):
        """
        Hawq doesn't have indexes
        """
        return exclusions.closed()

    @property
    def identity_columns(self):
        """
        Hawq doesn't have identity columns
        """
        return exclusions.closed()

    @property
    def index_ddl_if_exists(self):
        """
        Hawq doesn't support indexes
        """
        return exclusions.closed()

    @property
    def autoincrement_without_sequence(self):
        """
        Hawq doesn't support autoincrement
        """
        return exclusions.closed()

    @property
    def default_schema_name_switch(self):
        """
        Hawq doesn't support default schema name switch
        """
        return exclusions.closed()

    @property
    def unique_constraint_reflection(self):
        """
        Hawq doesn't support unique constraints
        """
        return exclusions.closed()

    ### ------- HAWQ-SPECIFIC PROPERTIES -------- ###

    @property
    def indexing(self):
        """
        Hawq doesn't support indexes
        """
        return exclusions.closed()

    @property
    def update(self):
        """
        Hawq doesn't support row update
        """
        return exclusions.closed()

    @property
    def delete_row(self):
        """
        ProgrammingError('(psycopg2.ProgrammingError)
        Delete append-only table statement not supported yet')
        """
        return exclusions.closed()

    @property
    def test_schema_exists(self):
        """
        Depends on user to create test_schema in the target db.
        """
        return exclusions.open()

    @property
    def pg_enum_exists(self):
        """
        pg_catalog.pg_enum is required by this test but Hawq does not have it.
        """
        return exclusions.closed()

    @property
    def pg_relpersistence_exists(self):
        """
        pg_class.relpersistence is required by this test but Hawq doesn't have it.
        """
        return exclusions.closed()

    @property
    def with_recursive(self):
        """
        sqlalchemy.exc.NotSupportedError: (psycopg2.NotSupportedError)
        RECURSIVE option in WITH clause is not supported
        """
        return exclusions.closed()
