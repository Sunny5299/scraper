# Cricket Match Scraper

A Python-based web scraping project that collects upcoming cricket match links and live match scores using Selenium, BeautifulSoup, and MongoDB.

This project automates the process of collecting cricket match data from a cricket website. The application works in two stages:

1. Scrapes and stores links of upcoming matches in MongoDB.
2. Fetches stored match links from MongoDB, scrapes live score data, and stores the results in a separate collection.

This architecture improves efficiency by avoiding repeated scraping of the schedule page and allows live score updates independently.

## Tech Stack

* Python
* Selenium
* BeautifulSoup (BS4)
* MongoDB
* PyMongo
* ChromeDriver
## Project Workflow

### Step 1: Scrape Upcoming Match Links

The scraper visits the cricket schedule page and extracts links for upcoming matches.

Process:
* Open the schedule page using Selenium.
* Extract upcoming match URLs.
* Store match links in MongoDB.

### MongoDB Collection: `match_links`

Example Document:

```json
{
  "_id": "12345",
  "match_name": "India vs Australia",
  "match_link": "https://example.com/match/123",
  "status": "upcoming"
}
```

---

### Step 2: Scrape Live Match Scores

The score scraper retrieves match links from MongoDB and extracts live score information.

**Process:**

* Fetch match links from the `match_links` collection.
* Open each match page using Selenium.
* Parse page content using BeautifulSoup.
* Extract score information.
* Store score data in MongoDB.

### MongoDB Collection: match_scores

Example Document:

```json
{
  "_id": "12345",
  "match_name": "India vs Australia",
  "score": "250/4",
  "overs": "42.3",
  "last_updated": "2026-06-01 10:30:00"
}
```

---

## Project Structure

```text
project/
│
├── database/
│   └── mongo.py
│
├── models/
│   └── match_schema.py
│
├── scrapers/
│   ├── allmatch.py
│   └── match_scrapper.py
│
├── requirements.txt
│
└── README.md

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate the environment:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` is not available:

```bash
pip install selenium
pip install beautifulsoup4
pip install pymongo
pip install webdriver-manager
```

---

## MongoDB Setup

Make sure MongoDB is installed and running on your system.

Example connection:

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["cricket_db"]
```

---

## How to Run the Project

### Start MongoDB

```bash
mongod
```

---

### Run Match Link Scraper

This script scrapes upcoming match links and stores them in MongoDB.

```bash
python match_link_scraper.py
```

Expected Output:

```text
Scraping upcoming matches...
Match links saved successfully.
```

---

### Run Live Score Scraper

This script fetches match links from MongoDB and scrapes live scores.

```bash
python live_score_scraper.py
```

Expected Output:

```text
Fetching match links...
Scraping live scores...
Scores saved successfully.
```

---

## Database Collections

| Collection Name | Description                  |
| --------------- | ---------------------------- |
| match_links     | Stores upcoming match links  |
| match_scores    | Stores live match score data |

---

## Features

* Scrapes upcoming cricket match links.
* Stores match URLs in MongoDB.
* Fetches links directly from the database.
* Scrapes live match scores.
* Stores live score data in a separate collection.
* Modular and scalable architecture.
* Easy integration with APIs or frontend applications.

---

## Future Improvements

* Schedule automatic scraping using Cron Jobs or Task Scheduler.
* Add support for scorecards and player statistics.
* Create REST APIs using Flask or FastAPI.
* Build a frontend dashboard for real-time score visualization.
* Add logging and error handling.
* Support multiple cricket data sources.

---

## How It Works

```text
Schedule Page
      │
      ▼
allmatch
      │
      ▼
MongoDB (match_links)
      │
      ▼
match_scrapper
      │
      ▼
MongoDB (match_scores)
```

The Match Link Scraper first collects and stores upcoming match URLs. The Live Score Scraper then reads those URLs from MongoDB, scrapes live match scores, and stores the results in a separate collection. This separation makes the scraping process efficient, maintainable, and scalable.

