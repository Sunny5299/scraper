import json
import time
import re  # ✅ Moved to top
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["cricket_db"]      # Database name
matches = db["matches"]        # Collection name

print("Connected successfully")


def fetch_and_parse_scorecard(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table, .scorecard, .innings"))
        )
        time.sleep(2)
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # --- Extract match result ---
        result_text = ""
        result_elem = soup.find(string=lambda t: t and ("won by" in t or "match tied" in t or "no result" in t))
        if result_elem:
            result_text = result_elem.strip()
        
        # --- Teams and scores ---
        header_match = re.search(r'([A-Z]{2,4})\s+(\d+)-(\d+)\s*\((\d+\.\d+)\)\s+([A-Z]{2,4})\s+(\d+)-(\d+)\s*\((\d+\.\d+)\)', driver.page_source)
        teams = {}
        if header_match:
            teams = {
                "team1": {"name": header_match.group(1), "runs": int(header_match.group(2)), "wickets": int(header_match.group(3)), "overs": float(header_match.group(4))},
                "team2": {"name": header_match.group(5), "runs": int(header_match.group(6)), "wickets": int(header_match.group(7)), "overs": float(header_match.group(8))}
            }
        
        # --- Extract batting and bowling for both innings ---
        innings_data = []
        all_tables = soup.find_all("table")
        batting_tables = [] 
        bowling_tables = []
        for tbl in all_tables:
            tbl_text = tbl.get_text().lower()[:100]
            if "batter" in tbl_text or "batsman" in tbl_text or "runs" in tbl_text:
                batting_tables.append(tbl)
            elif "bowler" in tbl_text or "overs" in tbl_text:
                bowling_tables.append(tbl)
        
        # Pair them sequentially (first batting with first bowling)
        for i in range(min(len(batting_tables), len(bowling_tables))):
            innings_data.append({
                "innings_no": i+1,
                "batting": parse_batting_table(batting_tables[i]),
                "bowling": parse_bowling_table(bowling_tables[i])
            })
        
        # --- Fall of wickets ---
        fall_of_wickets = []
        fow_section = soup.find(string=re.compile(r"Fall of wickets", re.I))
        if fow_section:
            parent = fow_section.find_parent()
            fow_text = parent.get_text() if parent else fow_section
            fow_matches = re.findall(r'(\d+)-(\d+)\s*\(([\d.]+)\)', fow_text)
            for w in fow_matches:
                fall_of_wickets.append({
                    "wicket": int(w[1]),
                    "total": int(w[0]),
                    "over": float(w[2])
                })
        
        # --- Extras ---
        extras = {}
        extras_text = soup.find(string=re.compile(r"Extras", re.I))
        if extras_text:
            parent = extras_text.find_parent()
            extras_str = parent.get_text() if parent else extras_text
            match = re.search(r'Extras:\s*(\d+)\s*\(b\s*(\d+),\s*lb\s*(\d+),\s*w\s*(\d+),\s*nb\s*(\d+)\)', extras_str, re.I)
            if match:
                extras = {
                    "total": int(match.group(1)),
                    "byes": int(match.group(2)),
                    "leg_byes": int(match.group(3)),
                    "wides": int(match.group(4)),
                    "no_balls": int(match.group(5))
                }
        
        match_data = {
            "url": url,
            "result": result_text,
            "teams": teams,
            "innings": innings_data,
            "fall_of_wickets": fall_of_wickets,
            "extras": extras
        }
        return match_data
        
    finally:
        driver.quit()

def parse_batting_table(table):
    batting = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 6:
            name_cell = cells[0].get_text(strip=True)
            dismissal_cell = cells[1].get_text(strip=True) if len(cells) > 1 else ""
            runs = cells[2].get_text(strip=True) if len(cells) > 2 else "0"
            balls = cells[3].get_text(strip=True) if len(cells) > 3 else "0"
            fours = cells[4].get_text(strip=True) if len(cells) > 4 else "0"
            sixes = cells[5].get_text(strip=True) if len(cells) > 5 else "0"
            sr_raw = cells[6].get_text(strip=True) if len(cells) > 6 else "0"
            
            # Clean strike rate: keep only digits and dot
            import re
            sr_clean = re.sub(r'[^0-9.]', '', sr_raw)  # removes *, spaces, letters, etc.
            if sr_clean == "":
                sr_clean = "0"
            
            if name_cell and name_cell.lower() not in ["batter", "player", "batsman"]:
                batting.append({
                    "name": name_cell,
                    "dismissal": dismissal_cell,
                    "runs": int(runs) if runs.isdigit() else 0,
                    "balls": int(balls) if balls.isdigit() else 0,
                    "fours": int(fours) if fours.isdigit() else 0,
                    "sixes": int(sixes) if sixes.isdigit() else 0,
                    "strike_rate": float(sr_clean)
                })
    return batting
def parse_bowling_table(table):
    bowling = []
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if len(cells) >= 6:
            name = cells[0].get_text(strip=True)
            overs = cells[1].get_text(strip=True)
            maidens = cells[2].get_text(strip=True)
            runs = cells[3].get_text(strip=True)
            wickets = cells[4].get_text(strip=True)
            economy = cells[5].get_text(strip=True) if len(cells) > 5 else "0"
            
            if name and name.lower() not in ["bowler", "player"]:
                bowling.append({
                    "name": name,
                    "overs": float(overs) if overs.replace('.', '').isdigit() else 0.0,
                    "maidens": int(maidens) if maidens.isdigit() else 0,
                    "runs_conceded": int(runs) if runs.isdigit() else 0,
                    "wickets": int(wickets) if wickets.isdigit() else 0,
                    "economy": float(economy) if economy.replace('.', '').isdigit() else 0.0
                })
    return bowling

def save_to_mongo(data):

    if isinstance(data, list):
        if len(data) > 0:
            result = matches.insert_many(data)
            print("Inserted many:", len(result.inserted_ids))
        else:
            print("Empty list - nothing inserted")

    elif isinstance(data, dict):
        result = matches.insert_one(data)
        print("Inserted one:", result.inserted_id)

    else:
        print("Invalid data type:", type(data))

def main():
    url = "https://crex.com/cricket-live-score/dur-w-vs-tbz-17th-match-t20-blast-women-2026-match-updates-ZSU/match-scorecard"
    print("Fetching complete scorecard data...")
    data = fetch_and_parse_scorecard(url)
    print(data)
    """matches.insert_many(data)"""
    save_to_mongo(data)
    

if __name__ == "__main__":
    main()