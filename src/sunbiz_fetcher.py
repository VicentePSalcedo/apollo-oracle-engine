from pysftp import CnOpts, Connection
from os import getenv, path, makedirs
from dotenv import load_dotenv
from urllib.parse import urlparse

from .logger import log_info, log_error

load_dotenv()

SUNBIZ_SFTP_HOST = getenv("SUNBIZ_SFTP_HOST")
SUNBIZ_SFTP_USER = getenv("SUNBIZ_SFTP_USER")
SUNBIZ_SFTP_PASS = getenv("SUNBIZ_SFTP_PASS")

if SUNBIZ_SFTP_HOST:
    # Clean up the hostname to handle cases where a user might include a protocol like 'https://'
    parsed_url = urlparse(SUNBIZ_SFTP_HOST)
    hostname = parsed_url.netloc or parsed_url.path
    SUNBIZ_SFTP_HOST = hostname.strip('/')

if not all([SUNBIZ_SFTP_HOST, SUNBIZ_SFTP_USER, SUNBIZ_SFTP_PASS]):
    log_error("Missing one or more required environment variables: SUNBIZ_SFTP_HOST, SUNBIZ_SFTP_USER, SUNBIZ_SFTP_PASS")
    raise ValueError("Missing one or more required environment variables: SUNBIZ_SFTP_HOST, SUNBIZ_SFTP_USER, SUNBIZ_SFTP_PASS")


def download_file_from_sftp(remote_filepath, local_filepath):
    """
    Downloads a file from the SFTP server.
    """
    cnopts = CnOpts()
    cnopts.hostkeys = None # Disable host key checking

    try:
        if SUNBIZ_SFTP_HOST == None:
            return False
        with Connection(SUNBIZ_SFTP_HOST, username=SUNBIZ_SFTP_USER, password=SUNBIZ_SFTP_PASS, cnopts=cnopts) as sftp:
            log_info(f"Attempting to download {remote_filepath} to {local_filepath}...")
            if sftp.exists(remote_filepath):
                sftp.get(remote_filepath, local_filepath)
                log_info("Download complete.")
                return True
            else:
                log_info(f"File {remote_filepath} not found on the server.")
                return False

    except Exception as e:
        log_error(f"An error occurred during download: {e}")
        return False
    
def download_sunbiz_file(target_date, data_dir):
    """
    Downloads the Sunbiz data file for a specific target_date.
    """
    date_str = target_date.strftime('%Y%m%d')
    target_filename = f"{date_str}c.txt"
    remote_filepath = f'doc/cor/{target_filename}'
    local_filepath = path.join(data_dir, target_filename)

    makedirs(data_dir, exist_ok=True)    

    if path.exists(local_filepath):
        log_info(f"File {path.basename(target_filename)}) already exists locally. Skipping download.")
        return local_filepath
    else:
        log_info(f"Attempting to download {remote_filepath} to {local_filepath}...")
        if download_file_from_sftp(remote_filepath, local_filepath):
            return local_filepath
        else:
            log_info(f"Could not download {target_filename}.")
            return None
