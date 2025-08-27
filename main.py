# from src.logger import log_error, log_info
from src.db import get_db_connection, setup_db_tables

if __name__ == "__main__":
    conn = get_db_connection()
    setup_db_tables(conn)
