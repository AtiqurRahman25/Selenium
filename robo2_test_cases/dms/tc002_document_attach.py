""""
DMS-TC002	
Document Attach	
"1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/
2. Attach documents (PDF, PNG, JPG, JPEG, SVG, GIF, MP3, MP4, DOC, DOCX, XLS, XLSX, CSV, PPT, PPTX, MSG, EML, TXT) less than 20 mb"	
System should allow to attach documents (media or office file)
"""
import os
from datetime import datetime

import openpyxl
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()

# config (from .env)
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("DMS_USERNAME")
PASSWORD = os.getenv("DMS_PASSWORD")
EXCEL_PATH = os.getenv("EXCEL_PATH", r"D:\Selenium\robo2_test_cases\Robo2mation_26Q1_Sanity_Test_Case_Doc.xlsx")
SAMPLE_DIR = os.getenv("SAMPLE_DIR", "test_files")  
TESTER_NAME = os.getenv("TESTER_NAME", "Sharar")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")  
EVIDENCE_LINK = os.getenv("EVIDENCE_LINK")                    
EVIDENCE_HEADER = os.getenv("EVIDENCE_HEADER", "remark").lower()  

SHEET_NAME = "DMS"
HEADER_ROW = 4
TEST_CASE_ID = "DMS-TC002"
UPLOAD_URL = BASE_URL + "/dms/document/upload/standard_upload/"
EXTENSIONS = ["pdf", "png", "jpg", "jpeg", "svg", "gif", "mp3", "mp4", "doc", "docx",
              "xls", "xlsx", "csv", "ppt", "pptx", "msg", "eml", "txt"]

# locators (adjust if the page differs)
LOGIN_USER = (By.XPATH, "//input[contains(@placeholder, 'Username')]")
LOGIN_PASS = (By.XPATH, "//input[contains(@placeholder, 'Password')]")
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
NEXT_BTN = (By.XPATH, "//button[normalize-space()='Next']")

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs("debug", exist_ok=True)  # page HTML of failures (local only)


def login(driver, wait):
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located(LOGIN_USER)).send_keys(USERNAME)
    driver.find_element(*LOGIN_PASS).send_keys(PASSWORD, Keys.ENTER)  # Enter = green arrow button
    wait.until(EC.invisibility_of_element_located(LOGIN_USER))


def next_is_ready(driver):
    """The Next button is light green (disabled) until a file is attached."""
    try:
        btn = driver.find_element(*NEXT_BTN)
        return btn.is_enabled() and "disabled" not in (btn.get_attribute("class") or "").lower()
    except Exception:
        return False


def save_shot(driver, ext, result):
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{TEST_CASE_ID}_{ext}_{result}.png"))


def attach_file(driver, wait, ext):
    """Attach a file of this type from SAMPLE_DIR. Returns (True/False, message)."""
    # use any file in SAMPLE_DIR that ends with .<ext> (any name)
    names = [n for n in os.listdir(SAMPLE_DIR) if n.lower().endswith("." + ext)]
    if not names:
        return False, "sample file missing"
    file_name = names[0]
    path = os.path.abspath(os.path.join(SAMPLE_DIR, file_name))

    driver.get(UPLOAD_URL)
    wait.until(EC.presence_of_element_located(FILE_INPUT))
    next_was_ready = next_is_ready(driver)  # if already "ready" before attaching, it can't prove anything

    # Pass if the file name / preview shows on the page, or the Next button becomes active
    def attached(d):
        text = d.find_element(By.TAG_NAME, "body").text
        return (file_name in text
                or d.find_elements(By.CSS_SELECTOR, ".dz-preview, .dz-filename")
                or (not next_was_ready and next_is_ready(d)))

    # try every file input on the page (the dropzone input may not be the first one)
    for file_input in driver.find_elements(*FILE_INPUT):
        driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", file_input)
        try:
            file_input.send_keys(path)
            WebDriverWait(driver, 6).until(attached)
            save_shot(driver, ext, "PASS")
            return True, "attached"
        except Exception:
            continue

    # failed: show where the browser is, and keep a screenshot and the page HTML so we can see what the page showed
    print("   page after attach:", driver.current_url, "| file inputs:", len(driver.find_elements(*FILE_INPUT)))
    save_shot(driver, ext, "FAIL")
    with open(f"debug/{TEST_CASE_ID}_{ext}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    return False, "file not shown after attach"


def find_row_and_columns(ws):
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

    columns = {"actual": col_of("actual"), "status": col_of("status"), "evidence": col_of(EVIDENCE_HEADER), "date": col_of("date"), "tester": col_of("tester")}

    row = None
    for r in range(HEADER_ROW + 1, ws.max_row + 1):
        if str(ws.cell(r, 1).value or "").strip() == TEST_CASE_ID:
            row = r
            break
    return row, columns


def write_result(actual, status):
    wb = openpyxl.load_workbook(EXCEL_PATH)
    ws = wb[SHEET_NAME]
    row, columns = find_row_and_columns(ws)
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


def main():
    # check the Excel row first, so we stop before opening the browser
    ws = openpyxl.load_workbook(EXCEL_PATH)[SHEET_NAME]
    row, columns = find_row_and_columns(ws)
    if row is None:
        raise SystemExit(f"{TEST_CASE_ID} not found in column A of sheet '{SHEET_NAME}'")
    missing = [k for k, v in columns.items() if v is None]
    print(f"Row {row} found. Columns not found in header row {HEADER_ROW}: {missing or 'none'}")

    # Excel must be closed, otherwise saving fails at the end
    try:
        open(EXCEL_PATH, "ab").close()
    except PermissionError:
        raise SystemExit("Close the Excel file first, then run again.")

    # list missing sample files before opening the browser
    have = [e for e in EXTENSIONS if any(n.lower().endswith("." + e) for n in os.listdir(SAMPLE_DIR))]
    print("Files missing in", SAMPLE_DIR, ":", [e for e in EXTENSIONS if e not in have] or "none")

    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    passed, failed = [], []

    try:
        login(driver, wait)
        for ext in EXTENSIONS:
            ok, msg = attach_file(driver, wait, ext)
            print(f"{ext:5} -> {'PASS' if ok else 'FAIL'} ({msg})")
            (passed if ok else failed).append(ext if ok else f"{ext} ({msg})")
    finally:
        driver.quit()

    if failed:
        status = "Fail"
        actual = f"Attached {len(passed)}/{len(EXTENSIONS)} file types. Could not attach: " + ", ".join(failed)
    else:
        status = "Pass"
        actual = f"All {len(EXTENSIONS)} file types were attached successfully"

    write_result(actual, status)
    print(f"\n{TEST_CASE_ID}: {status}")


if __name__ == "__main__":
    main()