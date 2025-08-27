from time import sleep

from .db import get_listed_corporations
from .logger import log_info, log_error
from .proxy_fetcher import load_proxies, fetch_proxies

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:90.0) Gecko/20100101 Firefox/90.0',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)'
]

ACCEPT_HEADERS = [
    'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'application/xml,application/xhtml+xml,text/html;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
]

ACCEPT_LANGUAGE_HEADERS = [
    'en-US,en;q=0.5',
    'en-GB,en;q=0.5',
    'en-CA,en;q=0.5',
    'fr-FR,fr;q=0.8',
    'es-ES,es;q=0.8',
]

ACCEPT_ENCODING_HEADERS = [
    'gzip, deflate, br',
    'gzip, deflate',
    'br',
]

_cached_proxies = []

class FacebookRequestError(Exception):
    pass

def qualify_leads_sequentially(conn):
    global _cached_proxies

    _cached_proxies = load_proxies()

    while not _cached_proxies:
        _cached_proxies = fetch_proxies()
        log_info("Could not fetch or load any proxies. Retrying in 10 seconds...")
        sleep(10)
 
    listed_corporations = get_listed_corporations(conn)
    for corp in listed_corporations:
        qualify_lead(corp)
    return
   
def qualify_lead(corp):
   global _cached_proxies

   log_info(f"{corp['corporation_name']} processing")
