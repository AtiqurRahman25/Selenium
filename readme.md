# Selenium Test Automation Suite.

A professional Selenium automation portfolio demonstrating real-world QA engineering skills — including web scraping, login validation, and document management system (DMS) testing — with clean, maintainable Python code and automated Excel test reporting.

---

## 📋 Table of Contents
- [What This Repository Demonstrates](#-what-this-repository-demonstrates)
- [Repository Structure](#-repository-structure)
- [Projects](#-projects)
  - [1. Login & Data Scraper](#1-login--data-scraper)
  - [2. Login Sanity Tests](#2-login-sanity-tests-robo2mation)
  - [3. DMS Document Attachment Tests](#3-dms-document-attachment-tests-robo2mation)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Key Engineering Practices](#-key-engineering-practices)

---

## 🎯 What This Repository Demonstrates

| Skill | Where to See It |
|---|---|
| Selenium WebDriver (explicit waits, locators) | `scraper.py`, `common.py`, `document_attach.py` |
| Structured test case execution with Excel reporting | `common.py` → `write_excel()` |
| Multi-format file upload automation (18 file types) | `dms/document_attach.py` |
| Credential & secret management via `.env` | All scripts, no hardcoded credentials |
| Screenshot capture on pass & fail | `run_test()`, `attach_file()` |
| Headless browser support | `scraper.py` → `HEADLESS` env flag |
| Data extraction → CSV & JSON export | `scraper.py` → `save_results()` |
| Logging to file and console simultaneously | `scraper.py` |
| Clean project structure and `.gitignore` hygiene | Root `.gitignore` |

---

## 📁 Repository Structure

```
Selenium/
│
├── login-and-scrape-automation/     # Web scraper: login → extract → export
│   ├── scraper.py                   # Main script
│   ├── .env.example                 # Environment variable template
│   ├── requirements.txt
│   └── output/                      # CSV, JSON, screenshots (git-ignored)
│
├── robo2_test_cases/                # Sanity test suite for Robo2mation ECM
│   ├── .env.example                 # Environment variable template
│   │
│   ├── login/                       # Login test cases
│   │   ├── common.py                # Shared helpers: login(), write_excel(), run_test()
│   │   ├── login_valid.py           # COR-TC001: valid login → dashboard
│   │   └── login_invalid.py        # COR-TC002: invalid login → error message
│   │
│   └── dms/                        # DMS (Document Management System) test cases
│       ├── document_attach.py       # DMS-TC002: attach 18 file types and write results
│       ├── .env.example             # Environment variable template
│       └── test_files/              # Sample files for upload tests (git-ignored)
│
├── .gitignore
└── readme.md
```

---

## 📦 Projects

### 1. Login & Data Scraper

**Location:** [`login-and-scrape-automation/`](login-and-scrape-automation/)

A self-contained automation script that logs into a web application, extracts product data, and exports results to CSV and JSON — all without hardcoding credentials.

**What it does:**
1. Reads credentials from `.env`
2. Opens the browser (headless optional), logs in with explicit waits
3. Scrapes all inventory items (name + price)
4. Saves timestamped `.csv` and `.json` to `output/`
5. Takes a screenshot on success; saves an error screenshot on failure
6. Writes a `run.log` for every execution

**Demo target:** [saucedemo.com](https://www.saucedemo.com) — a public practice site, no sign-up needed.

**Run it:**
```bash
cd login-and-scrape-automation
pip install -r requirements.txt
copy .env.example .env        # Windows
# cp .env.example .env        # Mac/Linux
# Fill in your credentials in .env
python scraper.py
```

**Sample output (`output/items_<timestamp>.json`):**
```json
[
  { "name": "Sauce Labs Backpack", "price": "$29.99", "scraped_at": "2026-10-29T09:58:07" },
  { "name": "Sauce Labs Bike Light", "price": "$9.99",  "scraped_at": "2026-10-29T09:58:07" }
]
```

---

### 2. Login Sanity Tests (Robo2mation)

**Location:** [`robo2_test_cases/login/`](robo2_test_cases/login/)

Selenium-driven test cases that validate the login flow of the Robo2mation ECM platform, with results written back to a structured Excel test case tracker.

| Test ID | File | Scenario | Expected Result |
|---|---|---|---|
| `COR-TC001` | `login_valid.py` | Login with valid credentials | Redirected to dashboard |
| `COR-TC002` | `login_invalid.py` | Login with invalid credentials | Error message displayed |

**Architecture highlights (`common.py`):**
- `login(driver, username, password)` — navigates and authenticates
- `write_excel(tc_id, ok, actual, shot)` — updates Status, Actual Result, Evidence, Date & Tester columns in the tracker
- `run_test(tc_id, test_func)` — bootstraps Chrome, runs the test, closes the browser, writes results

**Run a test:**
```bash
cd robo2_test_cases/login
copy ..\\.env.example .env    # Windows
# Fill in SITE_URL, VALID_USER, VALID_PASS, EXCEL_FILE, TESTER_NAME
python login_valid.py
python login_invalid.py
```

---

### 3. DMS Document Attachment Tests (Robo2mation)

**Location:** [`robo2_test_cases/dms/`](robo2_test_cases/dms/)

Automates uploading **18 different file types** to the Robo2mation Document Management System and writes a consolidated Pass/Fail result to the Excel tracker, with optional OneDrive evidence link.

**File types tested:**
`pdf`, `png`, `jpg`, `jpeg`, `svg`, `gif`, `mp3`, `mp4`, `doc`, `docx`, `xls`, `xlsx`, `csv`, `ppt`, `pptx`, `msg`, `eml`, `txt`

**How it works:**
1. Validates the Excel row and columns exist before touching the browser
2. Checks that sample files are present in `test_files/` for each extension
3. Logs in, then iterates through every extension
4. For each: navigates to the upload page, attaches the file, detects success (file preview, filename in DOM, or Next button activation)
5. Saves a screenshot tagged `PASS` or `FAIL` per file type
6. Writes a single summary result to the Excel tracker with an optional OneDrive hyperlink for evidence

**Run it:**
```bash
cd robo2_test_cases/dms
copy .env.example .env
# Fill in BASE_URL, DMS_USERNAME, DMS_PASSWORD, EXCEL_PATH, TESTER_NAME
# Add one sample file per extension into the test_files/ folder
python document_attach.py
```

**Console output example:**
```
Row 7 found. Columns not found in header row 4: none
Files missing in test_files : none
pdf   -> PASS (attached)
png   -> PASS (attached)
mp3   -> FAIL (file not shown after attach)
...
DMS-TC002: Fail
```

---

## 🛠 Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.10+ | Core language |
| Selenium | 4.x | Browser automation |
| python-dotenv | latest | Credential & config management |
| openpyxl | latest | Excel test tracker read/write |
| ChromeDriver | (auto via Selenium Manager) | Chrome browser driver |

---

## ⚡ Quick Start

> **Prerequisites:** Python 3.10+, Google Chrome installed.

```bash
# 1. Clone the repo
git clone https://github.com/ays19/Selenium.git
cd Selenium

# 2. Choose a project and install its dependencies
cd login-and-scrape-automation
pip install -r requirements.txt

# 3. Copy and fill in the .env
copy .env.example .env

# 4. Run
python scraper.py
```

For the Robo2mation test suites, there is no shared `requirements.txt` yet — install directly:
```bash
pip install selenium python-dotenv openpyxl
```

---

## ✅ Key Engineering Practices

- **No hardcoded secrets** — every credential and path lives in `.env` (excluded from git via `.gitignore`)
- **Explicit waits only** — `WebDriverWait` + `expected_conditions` throughout; no `time.sleep` for synchronization
- **Centralized selectors** — locators defined in one place for easy site adaptation
- **Graceful error handling** — screenshots and debug HTML saved on failure; browser always closed via `finally`
- **Excel-integrated reporting** — results written programmatically to the test case tracker; no manual copy-paste
- **Gitignore hygiene** — `screenshots/`, `output/`, `test_files/`, `debug/`, `__pycache__/`, `.env`, and Office lock files (`~$*`) are all excluded
