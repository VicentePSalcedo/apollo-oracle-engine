import asyncio
from os import getenv
from random import choice
from urllib.parse import quote
from re import compile

from .sendgrid_util import clean_company_name

from .db import get_unqualified_corporations, update_company_async
from .logger import log_info, log_error

from playwright.async_api import async_playwright, Playwright, Error as PlaywrightError, TimeoutError
from playwright_stealth import Stealth


def load_proxies_from_env(file_path='Webshare 100 proxies.txt') -> list[str]:
    formatted_proxies = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                clean_line = line.strip()
                if clean_line:
                    parts = clean_line.split(':')
                    if len(parts) >= 2:
                        ip_address = parts[0]
                        port = parts[1]
                        formatted_proxies.append(f"http://{ip_address}:{port}")
    except FileNotFoundError:
        print(f"Error: The file at '{file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return formatted_proxies

proxies_list = load_proxies_from_env() 
MAX_RETRIES = 5

async def qualify_leads_sequentially(conn):
    listed_corporations = get_unqualified_corporations(conn)
    for corp in listed_corporations:
        async with Stealth().use_async(async_playwright()) as p:
            await qualify_lead_playwright(corp, p)
    return

async def worker(corp, semaphore):
    async with semaphore:
        async with Stealth().use_async(async_playwright()) as p:
            await qualify_lead_playwright(corp, p)

async def qualify_leads_in_parallel(conn):
    max_workers = 3
    delay_between_tasks = 2
    semaphore = asyncio.Semaphore(max_workers)
    listed_corporations = get_unqualified_corporations(conn)
    tasks = []
    for corp in listed_corporations:
        task = asyncio.create_task(worker(corp, semaphore))
        tasks.append(task)
        await asyncio.sleep(delay_between_tasks)
    await asyncio.gather(*tasks)
    log_info("\nAll leads have been qualified at a paced rate.")
    return

async def extract_email_from_facebook_page(corp, url, page):
    corp_name = corp['corporation_name']
    corp_num = corp['corporation_number']
    email_regex = compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') 

    for _ in range(MAX_RETRIES):
        await page.goto(url, timeout=30000)
        email_locator = page.get_by_text(email_regex)

        await asyncio.sleep(2)

        
        if await email_locator.count() > 0:
            email_address = await email_locator.first.inner_text()

            log_info(f"Email for {corp_name} is: {email_address}")

            await update_company_async(
                corp_num,
                email=email_address,
                facebook_url=url,
                contacted=False,
                unsubscribed=False
            )
            return
        else:
            log_info(f"Page loaded, but no email found for '{corp_name}'.")
            return

def choose_proxy():
    current_proxy = choice(proxies_list)
    log_info(f"Connecting via {current_proxy}.")
    return current_proxy

async def qualify_lead_playwright(corp: dict, p: Playwright) -> None:
    corp_name = corp['corporation_name']

    log_info(f"Processing {clean_company_name(corp_name)}")

    query = f"{corp_name} Florida"
    search_url = f"https://duckduckgo.com/?q={quote(query)}"
    browser = None
    current_proxy = choose_proxy()

    WEBSHARE_USERNAME = getenv("WEBSHARE_USERNAME")
    if not WEBSHARE_USERNAME:
        log_error("Missing WEBSHARE_USERNAME environment variable.")
        exit(0)

    WEBSHARE_PASSWORD = getenv("WEBSHARE_PASSWORD")
    if not WEBSHARE_PASSWORD :
        log_error("Missing WEBSHARE_PASSWORD environment variable.")
        exit(0)

    for _ in range(MAX_RETRIES):
        page = None

        try:
            browser = await p.chromium.launch(
                headless=True,
                proxy={
                    "server": current_proxy,
                    "username": WEBSHARE_USERNAME,
                    "password": WEBSHARE_PASSWORD
                }
            )
            page = await browser.new_page()
            await page.goto(search_url, timeout=30000)

            title_locator = await page.locator('h2').all()
            for title in title_locator:
                link_locator = title.locator('a')
                await link_locator.wait_for()
                href = await link_locator.get_attribute('href')
                if not href:
                    continue

                if "facebook.com" in href:
                    if "/posts/" in href or "/videos/" in href or "/photos/" in href or "/story.php" in href:
                        log_info(f"Skipping Facebook post link: {href}")
                        continue
        
                    facebook_url = href.rstrip('/')
                    if "/about" in facebook_url or "?sk=about" in facebook_url:
                        about_url = facebook_url
                    else:
                        if "/people/" in facebook_url or "/groups/" in facebook_url:
                            about_url = facebook_url + "/?sk=about"
                        else:
                            about_url = facebook_url + "/about"
        
                    log_info(f"Using About page URL: {about_url}")

                    await extract_email_from_facebook_page(corp, about_url, page)
                    break
            break 
        except TimeoutError as e:
            log_error(f"Timeout error on {corp_name}: {e}. Selecting a new proxy and trying again...")
            current_proxy = choose_proxy()
        except PlaywrightError as e:
            log_error(f"Proxy or navigation error with {current_proxy} for {corp_name}: {e}. Selecting a new proxy and trying again...")
            current_proxy = choose_proxy()
        except Exception as e:
            log_error(f"An unexpected error occurred while processing {corp_name}: {e}. Selecting a new proxy and trying agian...")
            current_proxy = choose_proxy()
        finally:
            if browser:
                await browser.close()

