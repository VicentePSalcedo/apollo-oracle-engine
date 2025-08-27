from os import getenv, path
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from time import sleep

from src.logger import log_error, log_info
from src.db import get_db_connection, has_file_processed, mark_corp_contacted, setup_db_tables, get_uncontacted_corps, update_file_status
from src.sunbiz_fetcher import download_sunbiz_file
from src.sunbiz_parser import parse_sunbiz_file
from src.corporation_categorizer import categorize_corporations
from src.lead_qualifier import qualify_leads_sequentially

load_dotenv()

def main_workflow(conn, input_file_path):
    log_info(f"Running main workflow with input: {input_file_path}")

    log_info(f"Parsing raw Sunbiz data from {path.basename(input_file_path)}.")
    parse_sunbiz_file(conn, input_file_path)

    log_info(f"Categorizing parsed corporations.")
    categorize_corporations(conn)

    log_info("Qualifying new categorized leads.")
    qualify_leads_sequentially(conn)
    
    log_info(f"{input_file_path} processed")
    return

if __name__ == "__main__":
    conn = get_db_connection()
    setup_db_tables(conn)

    YEAR = getenv("YEAR")
    MONTH = getenv("MONTH")
    DAY = getenv("DAY")
    if not YEAR or not MONTH or not DAY:
        log_error("Missing one or more required environment variables: YEAR, MONTH, DAY")
        exit(1)

    current_date = datetime(int(YEAR), int(MONTH), int(DAY)).date()
    today = date.today()
    emails_sent = 0

    TARGET = getenv("TARGET")
    if not TARGET:
        log_error("Missing TARGET environment variable.")
        exit(1)

    TEST_EMAIL = getenv("TEST_EMAIL")
    if not TEST_EMAIL:
        log_info("TEST_EMAIL IS NOT SET. RUNNING IN PRODUCTION")

    while emails_sent < int(TARGET) and current_date <= today:
        uncontacted_corps = get_uncontacted_corps(conn)

        for corp in uncontacted_corps:
            if TEST_EMAIL:
                # send_single_email()
                emails_sent += 1
                mark_corp_contacted(conn, corp['corporation_number'], True)
            else:
                # send_single_email()
                emails_sent += 1
                mark_corp_contacted(conn, corp['corporation_number'], True)
            if emails_sent >= int(TARGET):
                break
        if emails_sent >= int(TARGET):
            break

        date_str = current_date.strftime("%Y%m%d")
        expected_local_filepath = path.join("/app/raw_data", f"{date_str}c.txt")

        if has_file_processed(conn, expected_local_filepath):
            log_info(f"File {path.basename(expected_local_filepath)} already processed. Skipping workflow for this date.")
            current_date += timedelta(days=1)
            continue

        log_info(f"Attempting to fetch data for {current_date.strftime("%Y-%m-%d")}")

        input_file_path = download_sunbiz_file(current_date, "/app/raw_data")

        if input_file_path:
            log_info(f"Processing file: {input_file_path}")
            main_workflow(conn, input_file_path)
            update_file_status(conn, input_file_path, "completed")
            current_date += timedelta(days=1)
        else:
            log_info(f"No new date for {current_date.strftime("%Y-%m-%d")}. Trying next day...")
            update_file_status(conn, expected_local_filepath, "completed")
            current_date += timedelta(days=1)

            
