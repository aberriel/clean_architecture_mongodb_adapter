"""Top-level package for Clean Architecture Framework MongoDB Adapter."""
from clean_architecture_mongodb_adapter.basic_mongodb_adapter import (
    BasicMongodbAdapter,
    NotExistsException)

__author__ = """Anselmo Lira"""
__version__ = '0.1.3'
__all__ = ['BasicMongodbAdapter', 'NotExistsException']
