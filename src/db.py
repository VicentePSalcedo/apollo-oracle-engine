from datetime import datetime, timezone
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

def get_uncontacted_corps(conn):
    uncontacted_corporations = []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql_query = "SELECT companies.corporation_number, corporation_name, category, email, facebook_url, phone_number, contacted, unsubscribed FROM companies WHERE contacted = %s;"
        cur.execute(sql_query, (False,))
        uncontacted_corporations = cur.fetchall()
        return uncontacted_corporations

def has_file_processed(conn,filename):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS(SELECT 1 FROM processed_files WHERE filename = %s AND status = 'completed');",
            (filename,)
        )
        return cur.fetchone()[0]

def mark_corp_contacted(conn, corp_number, has_been_contacted):
    sql = "UPDATE companies SET contacted = %s WHERE corporation_number = %s;"
    
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (has_been_contacted, corp_number))
            if cur.rowcount == 0:
                log_info(f"No company found with corp_number: {corp_number}. No update performed.")
            else:
                log_info(f"Set 'contacted' to {has_been_contacted} for company: {corp_number}")

            conn.commit()
    except psycopg2.Error as e:
        log_error(f"Error updating contact status for {corp_number}: {e}")
        conn.rollback()

def update_file_status(conn, filename, status):
    query = sql.SQL("""
        INSERT INTO processed_files (filename, status, processed_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (filename) DO UPDATE SET
            status = EXCLUDED.status,
            processed_at = EXCLUDED.processed_at
    """)
    with conn.cursor() as cur:
        processed_time = datetime.now(timezone.utc)
        cur.execute(query, (filename, status, processed_time))
        conn.commit()
    log_info(f"Recorded '{filename}' with status '{status}'.")

def insert_company(conn, data):
    """Inserts a new company into the table."""
    sql = """
        INSERT INTO companies (corporation_number, corporation_name, category, email, facebook_url, phone_number, contacted, unsubscribed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (corporation_number) DO NOTHING;
    """
    try:
        cur = conn.cursor()
        cur.execute(sql, (
            data['corp_number'],
            data['name'],
            data['category'],
            data['email'],
            data['facebook'],
            data['phone'],
            data['contacted'],
            data['unsubscribed']
        ))
        conn.commit()
        log_info(f"Inserted or ignored company: {data['name']}")
        cur.close()
    except psycopg2.Error as e:
        log_error(f"Error inserting data: {e}")
        conn.rollback()

def get_uncategorized_corps(conn):
    uncategorized_corporations = []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        # Selects companies where the category column is NULL
        sql_query = """
            SELECT 
                corporation_number, 
                corporation_name, 
                category, 
                email, 
                facebook_url, 
                phone_number, 
                contacted, 
                unsubscribed 
            FROM 
                companies 
            WHERE 
                category IS NULL;
        """
        cur.execute(sql_query)
        uncategorized_corporations = cur.fetchall()
        return uncategorized_corporations

def update_company_category(conn, corporation_number, new_category):
    sql_query = """
        UPDATE companies
        SET category = %s
        WHERE corporation_number = %s;
    """
    updated_rows = 0
    try:
        with conn.cursor() as cur:
            cur.execute(sql_query, (new_category, corporation_number))
            updated_rows = cur.rowcount
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        log_error(f"Error updating database: {error}")
        conn.rollback()

    return updated_rows > 0

import psycopg2.extras

def get_listed_corporations(conn):
    listed_corporations = []
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        sql_query = """
            SELECT 
                corporation_number, 
                corporation_name, 
                category, 
                email, 
                facebook_url, 
                phone_number, 
                contacted, 
                unsubscribed 
            FROM 
                companies 
            WHERE 
                category IS NOT NULL AND category <> %s;
        """
        cur.execute(sql_query, ('Unlisted',))
        listed_corporations = cur.fetchall()
        return listed_corporations
