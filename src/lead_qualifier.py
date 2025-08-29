import concurrent.futures
from time import sleep
from random import choice
from urllib.parse import quote

from .db import get_listed_corporations
from .logger import log_info, log_error

from playwright.async_api import async_playwright, Playwright, Error as PlaywrightError
from playwright_stealth import Stealth

proxies_list = [
    "http://23.95.150.145:6114/",
    "http://23.95.150.145:6114",
    "http://198.23.239.134:6540",
    "http://45.38.107.97:6014",
    "http://107.172.163.27:6543",
    "http://64.137.96.74:6641",
    "http://45.43.186.39:6257",
    "http://154.203.43.247:5536",
    "http://216.10.27.159:6837",
    "http://136.0.207.84:6661",
    "http://142.147.128.93:6593",
]

async def qualify_leads_sequentially(conn):
    listed_corporations = get_listed_corporations(conn)
    for corp in listed_corporations:
        async with Stealth().use_async(async_playwright()) as p:
            await qualify_lead_playwright(corp, p)
        sleep(10)
    return

def qualfiy_leads_in_parallel(conn):
    listed_corporations = get_listed_corporations(conn)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(proxies_list)) as executor:
        executor.map(qualify_lead_playwright, listed_corporations)

async def qualify_lead_playwright(corp: dict, p: Playwright):
    corp_name = corp['corporation_name']
    log_info(f"Processing {corp_name} with Playwright")

    query = f"{corp_name} Florida"
    search_url = f"https://duckduckgo.com/?q={quote(query)}"
    browser = None

    while True:
        current_proxy = choice(proxies_list)
        log_info(f"Attempting connection with proxy: {current_proxy}")

        page = None

        try:
            browser = await p.chromium.launch(
                headless=True,
                # proxy={
                #     "server": current_proxy,
                #     "username": "sintrasensei",
                #     "password": "eexpc14rdl7u",
                # },
            )
            page = await browser.new_page()
            await page.goto(search_url, timeout=30000) # 30-second timeout
            log_info(f"Page visted: {page}")
            web_content_wrapper_locator = page.locator('#react-layout > div > div > div')
            await web_content_wrapper_locator.wait_for()
            section_locator = web_content_wrapper_locator.locator('section:nth-child(1)')
            await section_locator.wait_for()
            log_info(await section_locator.inner_text())
            link_locator = await section_locator.locator('a').all()

            for link in link_locator:
                href = await link.get_attribute('href')
                if not href:
                    continue

                log_info(f" ---> {href}")
                if "facebook.com" in href:
                    log_info(f"Facebook link found: {href}")
                    
                    facebook_url = href.rstrip('/')
                    log_info(f"Cleaned up facebook url: {facebook_url}")
                    
                    if "/people/" in facebook_url or "/groups/" in facebook_url:
                        about_url = facebook_url + "/?sk=about"
                    else:
                        about_url = facebook_url + "/about"
                    
                    log_info(f"Constructed About page URL: {about_url}")
            break 
        except PlaywrightError as e:
            log_error(f"Proxy or navigation error with {current_proxy} for {corp_name}: {e}")
            if page:
                screenshot_path = f"error_{corp_name.replace(' ', '_')}.png"
                await page.screenshot(path=screenshot_path)
                log_error(f"Screenshot saved to {screenshot_path}")
                exit(0)
        except Exception as e:
            log_error(f"An unexpected error occurred while processing {corp_name}: {e}")
            break 
        finally:
            if browser:
                await browser.close()
