from os import getenv
import psycopg2
import psycopg2.extras
from psycopg2 import sql

from .logger import log_info, log_error

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="sunbiz-db",
            database=getenv("POSTGRES_DB"),
            user=getenv("POSTGRES_USER"),
            password=getenv("POSTGRES_PASSWORD")
        )
        log_info("Database connection successful!")
        return conn
    except psycopg2.OperationalError as e:
        log_error(f"Could not connect to the databse: {e}")
        return None
