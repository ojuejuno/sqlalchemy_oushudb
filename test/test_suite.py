"""
Stub for sqlalchemy's unit tests.
Imports and modifies some test subsuites.

Disables tests of sqlalchemy functionality that OushuDB dialect does not support.
"""
from sqlalchemy import testing
from sqlalchemy.testing.suite import *

# imports where some tests will be skipped by being given
# additional requirements
from sqlalchemy.testing.suite import SimpleUpdateDeleteTest as _SimpleUpdateDeleteTest
from sqlalchemy.testing.suite import TableDDLTest as _TableDDLTest
from sqlalchemy.testing.suite import ServerSideCursorsTest as _ServerSideCursorsTest
from sqlalchemy.testing.suite import RowCountTest as _RowCountTest
from sqlalchemy.testing.suite import DistinctOnTest as _DistinctOnTest
from sqlalchemy.testing.suite import ArgSignatureTest as _ArgSignatureTest
from sqlalchemy.testing.suite import UnicodeSchemaTest as _UnicodeSchemaTest
from sqlalchemy.testing.suite import TableNoColumnsTest as _TableNoColumnsTest
from sqlalchemy.testing.suite import PercentSchemaNamesTest as _PercentSchemaNamesTest
from sqlalchemy.testing.suite import SequenceTest as _SequenceTest
from sqlalchemy.testing.suite import IdentityAutoincrementTest as _IdentityAutoincrementTest
from sqlalchemy.testing.suite import IdentityColumnTest as _IdentityColumnTest
from sqlalchemy.testing.suite import IdentityReflectionTest as _IdentityReflectionTest
from sqlalchemy.testing.suite import IsolationLevelTest as _IsolationLevelTest
from sqlalchemy.testing.suite import LongNameBlowoutTest as _LongNameBlowoutTest
from sqlalchemy.testing.suite import NormalizedNameTest as _NormalizedNameTest
from sqlalchemy.testing.suite import CTETest as _CTETest


# imports where the whole test suite will be skipped
from sqlalchemy.testing.suite import (
    FutureWeCanSetDefaultSchemaWEventsTest,
    WeCanSetDefaultSchemaWEventsTest,
    QuotedNameArgumentTest,
    JSONLegacyStringCastIndexTest,
    ComputedColumnTest,
    ComputedReflectionTest,
    NativeUUIDTest,
    HasIndexTest,
    ComponentReflectionTest,
    CompositeKeyReflectionTest,
    ComponentReflectionTestExtra,
    UuidTest,
    ReturningGuardsTest,
    ReturningTest,
    JSONTest,
    TableNoColumnsTest,
)

# TODO: OushuDB tests
del HasIndexTest  # hawq doesn't have indexes
del ComputedColumnTest, ComputedReflectionTest  # hawq doesn't support computed columns
del UuidTest, NativeUUIDTest  # hawq doesn't support the uuid data type
del ReturningGuardsTest, ReturningTest  # hawq doesn't support insert/update/delete returning
del JSONTest, JSONLegacyStringCastIndexTest  # hawq doesn't support the json data type
del TableNoColumnsTest  # hawq doesn't support creating views/tables with no columns

del QuotedNameArgumentTest  # all tests rely on pk constraint, which hawq doesn't support

# all tests require indexes which hawq doesn't support
del ComponentReflectionTest, CompositeKeyReflectionTest, ComponentReflectionTestExtra

# hawq doesn't support setting the default schema
del FutureWeCanSetDefaultSchemaWEventsTest, WeCanSetDefaultSchemaWEventsTest


class ArgSignatureTest(_ArgSignatureTest):
    @testing.requires.indexing
    def test_all_visit_methods_accept_kw(self, all_subclasses):
        _ArgSignatureTest.test_all_visit_methods_accept_kw(self, all_subclasses)


class CTETest(_CTETest):
    @testing.requires.delete_row
    def test_delete_scalar_subq_round_trip(self, connection):
        _CTETest.test_delete_scalar_subq_round_trip(self, connection)

    @testing.requires.with_recursive
    def test_select_recursive_round_trip(self, connection):
        _CTETest.test_select_recursive_round_trip(self, connection)

    @testing.requires.with_recursive
    def test_insert_from_select_round_trip(self, connection):
        _CTETest.test_select_recursive_round_trip(self, connection)


class DistinctOnTest(_DistinctOnTest):
    @testing.requires.supports_distinct_on
    def test_distinct_on(self):
        _DistinctOnTest.test_distinct_on(self)


class IdentityAutoincrementTest(_IdentityAutoincrementTest):
    @testing.requires.insert_returning
    def test_autoincrement_with_identity(self):
        _IdentityAutoincrementTest.test_autoincrement_with_identity(self)


class IdentityColumnTest(_IdentityColumnTest):
    @testing.requires.identity_columns
    def test_select_all(self):
        _IdentityColumnTest.test_select_all(self)

    @testing.requires.identity_columns
    def test_select_columns(self):
        _IdentityColumnTest.test_select_columns(self)


class IdentityReflectionTest(_IdentityReflectionTest):
    @testing.requires.pg_enum_exists
    def test_reflect_identity(self):
        _IdentityReflectionTest.test_reflect_identity(self)

    @testing.requires.pg_enum_exists
    def test_reflect_identity_schema(self):
        _IdentityReflectionTest.test_reflect_identity_schema(self)


class LongNameBlowoutTest(_LongNameBlowoutTest):
    @testing.requires.indexing
    def test_long_convention_name(self):
        _LongNameBlowoutTest.test_long_convention_name(self, type_, metadata, connection)


class NormalizedNameTest(_NormalizedNameTest):
    @testing.requires.pg_relpersistence_exists
    def test_get_table_names(self):
        _NormalizedNameTest.test_get_table_names(self)

    @testing.requires.pg_enum_exists
    def test_reflect_lowercase_forced_tables(self):
        _NormalizedNameTest.test_reflect_lowercase_forced_tables(self)


class PercentSchemaNamesTest(_PercentSchemaNamesTest):
    @testing.requires.insert_returning
    def test_executemany_returning_roundtrip(self, connection):
        _PercentSchemaNamesTest.test_executemany_returning_roundtrip(self, connection)

    @testing.requires.update
    def test_executemany_roundtrip(self, connection):
        _PercentSchemaNamesTest.test_executemany_roundtrip(self, connection)

    @testing.requires.update
    def test_single_roundtrip(self, connection):
        _PercentSchemaNamesTest.test_single_roundtrip(self, connection)


class RowCountTest(_RowCountTest):
    @testing.requires.update
    def test_update_rowcount1(self, connection):
        _RowCountTest.test_update_rowcount1(self, connection)

    @testing.requires.update
    def test_update_rowcount2(self, connection):
        _RowCountTest.test_update_rowcount2(self, connection)

    @testing.requires.update
    def test_update_rowcount_return_defaults(self, connection):
        _RowCountTest.test_update_rowcount_return_defaults(self, connection)

    @testing.requires.update
    def test_text_rowcount(self, connection):
        _RowCountTest.test_text_rowcount(self, connection)

    @testing.requires.update
    def test_raw_sql_rowcount(self, connection):
        _RowCountTest.test_raw_sql_rowcount(self, connection)

    @testing.requires.update
    def test_multi_update_rowcount(self, connection):
        _RowCountTest.test_multi_update_rowcount(self, connection)

    @testing.requires.delete_row
    def test_multi_delete_rowcount(self, connection):
        _RowCountTest.test_multi_delete_rowcount(self, connection)

    @testing.requires.delete_row
    def test_delete_rowcount(self, connection):
        _RowCountTest.test_delete_rowcount(self, connection)


class SequenceTest(_SequenceTest):
    @testing.requires.insert_returning
    def test_insert_lastrowid(self):
        _SequenceTest.test_insert_lastrowid(self)

    @testing.requires.insert_returning
    def test_insert_roundtrip(self):
        _SequenceTest.test_insert_roundtrip(self)

    @testing.requires.insert_returning
    def test_insert_roundtrip_translate(self):
        _SequenceTest.test_insert_roundtrip_translate(self)

    @testing.requires.insert_returning
    def test_optional_seq(self):
        _SequenceTest.test_optional_seq(self)


class ServerSideCursorsTest(_ServerSideCursorsTest):
    def tearDown(self):  # noqa
        """
        Overrides parent teardown method to prevent calling dispose
        on engine that does not exist if test is skipped.
        """
        engines.testing_reaper.close_all()
        if 'engine' in dir(self):
            self.engine.dispose()

    @testing.requires.insert_returning
    def test_roundtrip_fetchall(self):
        _ServerSideCursorsTest.test_roundtrip_fetchall(self)

    @testing.requires.update
    def test_roundtrip_fetchall(self):
        _ServerSideCursorsTest.test_roundtrip_fetchall(self)

    @testing.requires.update
    def test_ss_cursor_status(self):
        _ServerSideCursorsTest.test_ss_cursor_status(self)


class SimpleUpdateDeleteTest(_SimpleUpdateDeleteTest):
    @testing.requires.delete_row
    def test_delete(self, connection):
        _SimpleUpdateDeleteTest.test_delete(self, connection)

    @testing.requires.update
    def test_update(self, connection):
        _SimpleUpdateDeleteTest.test_update(self, connection)


class TableDDLTest(_TableDDLTest):
    @testing.requires.test_schema_exists
    def test_create_table_schema(self):
        _TableDDLTest.test_create_table_schema(self)


class UnicodeSchemaTest(_UnicodeSchemaTest):
    @testing.requires.pg_enum_exists
    def test_reflect(self, connection):
        _UnicodeSchemaTest.test_reflect(self, connection)
