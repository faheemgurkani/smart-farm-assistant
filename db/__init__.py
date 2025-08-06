# Database package initialization
# This makes the db directory a Python package and exposes the logger functionality

from .logger import log_entry, get_db_connection

__all__ = ['log_entry', 'get_db_connection'] 