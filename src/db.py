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

def setup_db_tables(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                corporation_number TEXT PRIMARY KEY,
                corporation_name VARCHAR(255) NOT NULL,
                category VARCHAR(100),
                email VARCHAR(255),
                facebook_url VARCHAR(255),
                phone_number VARCHAR(20),
                contacted BOOLEAN DEFAULT FALSE,
                unsubscribed BOOLEAN DEFAULT FALSE
            );
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_files (
                filename TEXT PRIMARY KEY,
                status VARCHAR(20) NOT NULL,
                processed_at TIMESTAMPTZ NOT NULL
            );
        """)
        conn.commit()
    log_info("All database tables are ready.")
