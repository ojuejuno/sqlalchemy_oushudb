from sqlalchemy.dialects import postgresql
from sqlalchemy.testing import fixtures
from sqlalchemy.testing import assert_raises

import pytest

from sqlalchemy_oushudb.partition import format_partition_value
from sqlalchemy_oushudb.point import Point
from sqlalchemy_oushudb.point import SQLAlchemyOushuDBException


class TestFormatPartitionValue(fixtures.TestBase):
    def test_integer(self):
        result = format_partition_value(postgresql.INTEGER(), 1)
        assert result == '1'

    def test_numeric(self):
        result = format_partition_value(postgresql.NUMERIC(), 1)
        assert result == '1'

    def test_boolean(self):
        result = format_partition_value(postgresql.BOOLEAN(), 'f')
        assert result == 'FALSE'

        result = format_partition_value(postgresql.BOOLEAN(), 'true')
        assert result == 'TRUE'

    def test_real(self):
        result = format_partition_value(postgresql.REAL(), '1.1')
        assert result == '1.1'

    def test_float(self):
        result = format_partition_value(postgresql.FLOAT(), '1.1')
        assert result == '1.1'

    def test_enum(self):
        result = format_partition_value(postgresql.ENUM(name='test'), '1.1')
        assert result == '\'1.1\''

    def test_varchar(self):
        result = format_partition_value(postgresql.VARCHAR(), 'something')
        assert result == '\'something\''

    def test_text(self):
        result = format_partition_value(postgresql.TEXT(), 'something')
        assert result == '\'something\''

    def test_char(self):
        result = format_partition_value(postgresql.CHAR(), 's')
        assert result == '\'s\''

    def test_escape_string(self):
        result = format_partition_value(postgresql.CHAR(), '\'s\'')
        assert result == '$$\'s\'$$'


class TestPointSQLConversion(fixtures.TestBase):
    def test_string_to_tuple_correct(self):
        func = Point.result_processor(1, 2, 3)
        assert func('(99,100)') == (99, 100)

    def test_string_to_tuple_incorrect(self):
        func = Point.result_processor(1, 2, 3)
        assert_raises(SQLAlchemyOushuDBException, func, '(99,)')

    def test_string_to_tuple_incorrect_2(self):
        func = Point.result_processor(1, 2, 3)
        assert_raises(SQLAlchemyOushuDBException, func, '(,99)')

    def test_string_to_tuple_incorrect_3(self):
        func = Point.result_processor(1, 2, 3)
        assert_raises(SQLAlchemyOushuDBException, func, '(,)')

    def test_string_to_tuple_incorrect_4(self):
        func = Point.result_processor(1, 2, 3)
        assert_raises(SQLAlchemyOushuDBException, func, '(a,b)')

    def test_none_to_none_result(self):
        func = Point.result_processor(1, 2, 3)
        assert func(None) is None

    def test_none_to_none_bind(self):
        func = Point.bind_processor(1, 2)
        assert func((None, None)) is None

    def test_none_to_none_bind_2(self):
        func = Point.bind_processor(1, 2)
        assert func(None) is None

    def test_tuple_to_string(self):
        func = Point.bind_processor(1, 2)
        assert func((1, 2)) == '(1, 2)'

    def test_tuple_to_string_incorrect(self):
        func = Point.bind_processor(1, 2)
        assert_raises(SQLAlchemyOushuDBException, func, (None, 2))

    def test_tuple_to_string_incorrect_2(self):
        func = Point.bind_processor(1, 2)
        assert_raises(SQLAlchemyOushuDBException, func, (2, None))
