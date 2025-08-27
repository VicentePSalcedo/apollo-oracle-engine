# from src.logger import log_error, log_info
from src.db import get_db_connection

if __name__ == "__main__":
    connection = get_db_connection()
