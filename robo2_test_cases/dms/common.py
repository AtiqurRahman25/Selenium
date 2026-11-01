import os
from datetime import datetime

import openpyxl
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()

# ---------- config (from .env) ----------
BASE_URL = os.getenv("BASE_URL", "https://ecmv6.robo2mation.com")
USERNAME = os.getenv("DMS_USERNAME")
PASSWORD = os.getenv("DMS_PASSWORD")
EXCEL_PATH = os.getenv("EXCEL_PATH", r"D:\Selenium\robo2_test_cases\Robo2mation_26Q1_Sanity_Test_Case_Doc.xlsx")
SAMPLE_DIR = os.getenv("SAMPLE_DIR", "test_files")
TESTER_NAME = os.getenv("TESTER_NAME", "Sharar")
SHEET_NAME = os.getenv("SHEET_NAME", "DMS")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
EVIDENCE_LINK = os.getenv("EVIDENCE_LINK")
EVIDENCE_HEADER = os.getenv("EVIDENCE_HEADER", "remark").lower()  # column that holds the "Evidence Doc" link
HEADER_ROW = 4

EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "svg", "gif", "mp3", "mp4", "doc", "docx",
              "xls", "xlsx", "csv", "ppt", "pptx", "msg", "eml", "txt"]

LOGIN_USER = (By.XPATH, "//input[contains(@placeholder, 'Username')]")
LOGIN_PASS = (By.XPATH, "//input[contains(@placeholder, 'Password')]")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs("debug", exist_ok=True)  # page HTML of failures (local only)


def login(driver, wait):
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located(LOGIN_USER)).send_keys(USERNAME)
    driver.find_element(*LOGIN_PASS).send_keys(PASSWORD, Keys.ENTER)  # Enter = green arrow button
    wait.until(EC.invisibility_of_element_located(LOGIN_USER))


def save_shot(driver, test_case_id, ext, result):
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{test_case_id}_{ext}_{result}.png"))


def find_row_and_columns(ws, test_case_id):
    """Find the test case row (column A) and the result columns by header name."""
    headers = {}
    for col in range(1, ws.max_column + 1):
        text = str(ws.cell(HEADER_ROW, col).value or "").strip().lower()
        if text:
            headers[col] = text

    def col_of(keyword):
        for col, text in headers.items():
            if keyword in text:
                return col
        return None

    columns = {"actual": col_of("actual"), "status": col_of("status"), "evidence": col_of(EVIDENCE_HEADER),
               "date": col_of("date"), "tester": col_of("tester")}

    row = None
    for r in range(HEADER_ROW + 1, ws.max_row + 1):
        if str(ws.cell(r, 1).value or "").strip() == test_case_id:
            row = r
            break
    return row, columns


def check_excel_ready(test_case_id):
    """Run before opening the browser: row exists and the Excel file is closed."""
    ws = openpyxl.load_workbook(EXCEL_PATH)[SHEET_NAME]
    row, columns = find_row_and_columns(ws, test_case_id)
    if row is None:
        raise SystemExit(f"{test_case_id} not found in column A of sheet '{SHEET_NAME}'")
    missing = [k for k, v in columns.items() if v is None]
    print(f"Row {row} found. Columns not found in header row {HEADER_ROW}: {missing or 'none'}")
    try:
        open(EXCEL_PATH, "ab").close()
    except PermissionError:
        raise SystemExit("Close the Excel file first, then run again.")


def write_result(test_case_id, actual, status):
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb[SHEET_NAME]
    row, columns = find_row_and_columns(ws, test_case_id)
    values = {"actual": actual, "status": status, "evidence": "Evidence Doc",
              "date": datetime.now().strftime("%d-%b-%Y"), "tester": TESTER_NAME}
    for key, col in columns.items():
        if col:
            ws.cell(row, col).value = values[key]
    if columns["evidence"] and EVIDENCE_LINK:
        cell = ws.cell(row, columns["evidence"])
        cell.hyperlink = EVIDENCE_LINK  # clicking "Evidence Doc" opens the OneDrive folder
        cell.style = "Hyperlink"
    wb.save(EXCEL_PATH)
    print(f"Saved to: {os.path.abspath(EXCEL_PATH)}  (sheet '{ws.title}')")
    check = openpyxl.load_workbook(EXCEL_PATH)[SHEET_NAME]  # read back to confirm
    for key, col in columns.items():
        if col:
            cell = check.cell(row, col)
            print(f"  {cell.coordinate} [{check.cell(HEADER_ROW, col).value}] = {cell.value!r}")