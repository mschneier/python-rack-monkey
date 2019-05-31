"""Set up PostgreSQL connection."""
import gc
import os
from psycopg2 import connect


class SqlConnect:
    """Connect to pass grass database."""

    def __init__(self):
        """Initialize."""
        gc.enable()
        pass

    @staticmethod
    def query_connection():
        """Connect to database for queries."""
        con = connect(
            database="rack_monkey", user="query_tables", host="127.0.0.1",
            password=os.environ["PSQL_QUERY_USER_PASS"]
        )
        return con

    @staticmethod
    def update_connection():
        """Connect to database for updating info."""
        con = connect(
            database="rack_monkey", user="update_tables", host="127.0.0.1",
            password=os.environ["PSQL_UPDATE_USER_PASS"]
        )
        return con

    @staticmethod
    def delete_connection():
        """Connect to database for deleting entries."""
        con = connect(
            database="rack_monkey", user="delete_entries", host="127.0.0.1",
            password=os.environ["PSQL_DELETE_USER_PASS"]
        )
        return con

    @staticmethod
    def logging_connection():
        """Connect to database for logging changes."""
        con = connect(
            database="rack_monkey", user="logging", host="127.0.0.1",
            password=os.environ["PSQL_LOGGING_USER_PASS"]
        )
        return con

    @staticmethod
    def insert_connection():
        """Connect to database for inserting entries."""
        con = connect(
            database="rack_monkey", user="insert_entries", host="127.0.0.1",
            password=os.environ["PSQL_INSERT_USER_PASS"]
        )
        return con

    @staticmethod
    def search_connection():
        """Connection for device searches."""
        con = connect(
            database="rack_monkey", user="search_devices", host="127.0.0.1",
            password=os.environ["PSQL_SEARCH_USER_PASS"]
        )
        return con
