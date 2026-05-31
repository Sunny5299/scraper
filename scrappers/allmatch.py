import json
import time
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["cricket_db"]      # Database name
matches = db["match_list"]        # Collection name

print("Connected successfully")

SCHEDULE_URL = "https://crex.com/schedule"


def create_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.set_capability(
        "goog:loggingPrefs",
        {"performance": "ALL"}
    )

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    driver.execute_cdp_cmd("Network.enable", {})

    return driver


def get_network_json(driver):
    """
    Extract JSON API responses from Chrome DevTools.
    """

    api_data = []

    logs = driver.get_log("performance")

    for entry in logs:
        try:
            message = json.loads(entry["message"])["message"]

            if message["method"] != "Network.responseReceived":
                continue

            response = message["params"]["response"]

            mime_type = response.get("mimeType", "")
            request_id = message["params"]["requestId"]

            if "json" not in mime_type.lower():
                continue

            try:
                body = driver.execute_cdp_cmd(
                    "Network.getResponseBody",
                    {"requestId": request_id}
                )

                api_data.append({
                    "url": response["url"],
                    "status": response["status"],
                    "body": body.get("body", "")
                })

            except Exception:
                pass

        except Exception:
            pass

    return api_data


def find_match_links(driver):
    """
    Extract match URLs from schedule page.
    """

    driver.get(SCHEDULE_URL)

    time.sleep(8)

    links = driver.execute_script("""
        return [...document.querySelectorAll('a')]
            .map(a => a.href)
            .filter(x =>
                x.includes('/match-details/') ||
                x.includes('/cricket-live-score/')
            );
    """)

    return list(set(links))


def scrape_match(driver, url):

    print(f"\nOpening {url}")
    
    driver.get(url)

    time.sleep(8)

    api_data = get_network_json(driver)

    html = driver.page_source

    title = driver.title

    return {
        "url": url,
        "title": title,
    }


def main():
    driver = create_driver()

    try:
        print("Loading schedule page...")
        match_links = find_match_links(driver)
        print(f"Found {len(match_links)} matches")

        for i, link in enumerate(match_links, start=1):
            print(f"\n[{i}/{len(match_links)}]")

            try:
                # 1. Scrape the data first
                result = scrape_match(driver, link)

                # 2. Add an execution timestamp (Good practice for DB tracking)
                result["scraped_at"] = time.time()

                # 3. Insert the dictionary directly into MongoDB
                inserted_meta = matches.insert_one(result)
                print(f"✅ Successfully saved match to DB with ID: {inserted_meta.inserted_id}")

                time.sleep(2)

            except Exception as e:
                print(f"❌ Error scraping {link}: {e}")
                # Optional: log failures to a fallback table or error collection
                
    finally:
        driver.quit()

if __name__ == "__main__":
    main()