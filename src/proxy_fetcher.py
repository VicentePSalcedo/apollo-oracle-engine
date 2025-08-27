from os import path
from concurrent.futures import ThreadPoolExecutor, as_completed

from requests import get, exceptions
from bs4 import BeautifulSoup

from .logger import log_info, log_error

PROXY_FILE = ".proxies.txt"
MAX_VALIDATION_WORKERS = 20

def validate_proxy(proxy):
    """
    Validates a single proxy by attempting to connect to a test URL.
    Returns True if the proxy is valid, False otherwise.
    """
    test_url = "http://httpbin.org/ip"
    try:
        response = get(test_url, proxies={'https': proxy}, timeout=5) # 5 second timeout for validation
        return response.status_code == 200
    except exceptions.RequestException as e:
        log_error(f"Proxy validation failed for {proxy}: {e}")
        return False

def get_valid_proxies(proxies_list):
    """
    Validates a list of proxies in parallel and returns only the valid ones.
    """
    valid_proxies = []
    log_info(f"Validating {len(proxies_list)} proxies in parallel...")
    
    with ThreadPoolExecutor(max_workers=MAX_VALIDATION_WORKERS) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxies_list}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    valid_proxies.append(proxy)
            except Exception as exc:
                log_error(f'{proxy} generated an exception: {exc}')

    log_info(f"Found {len(valid_proxies)} valid proxies.")
    return valid_proxies

def load_proxies():
    """
    Loads proxies from the PROXY_FILE and validates them.
    """
    proxies = []
    if path.exists(PROXY_FILE):
        with open(PROXY_FILE, 'r') as f:
            for line in f:
                proxies.append(line.strip())
    
    if proxies:
        return get_valid_proxies(proxies)
    return []

def save_proxies(proxies):
    """
    Saves a list of proxies to the PROXY_FILE.
    """
    with open(PROXY_FILE, 'w') as f:
        for proxy in proxies:
            f.write(proxy + '\n')

def fetch_proxies():
    """
    Fetches a list of HTTPS proxies from freeproxy.world, validates them, and saves them to PROXY_FILE.
    """
    fetched_proxies = []
    url = "https://www.freeproxy.world/?type=https&anonymity=4&country=US&speed=&port=&page=1"
    try:
        response = get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        table = soup.find('table', class_='layui-table')
        if not table:
            log_info("Could not find the proxy table on the page.")
            return []

        tbody = table.find('tbody')
        if not tbody:
            log_info("Could not find the proxy table body on the page.")
            return []

        for row in tbody.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 2:
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                fetched_proxies.append(f"https://{ip}:{port}")
        
        if fetched_proxies:
            valid_proxies = get_valid_proxies(fetched_proxies)
            if valid_proxies:
                save_proxies(valid_proxies)
                log_info(f"Successfully fetched and saved {len(valid_proxies)} valid proxies to {PROXY_FILE}")
                return valid_proxies

    except exceptions.RequestException as e:
        log_error(f"Error fetching proxies: {e}")
    
    return []
