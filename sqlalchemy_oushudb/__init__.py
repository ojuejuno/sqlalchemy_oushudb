"""
Extends postgres dialect to support OushuDB db dialects.
"""

from sqlalchemy.dialects import registry as _registry
import pkg_resources


_registry.register('oushudb', 'sqlalchemy_oushudb.dialect', 'OushuDBDialect')
_registry.register('oushudb.psycopg2', 'sqlalchemy_oushudb.dialect', 'OushuDBDialect')


__version__ = pkg_resources.require('sqlalchemy_oushudb')[0].version
