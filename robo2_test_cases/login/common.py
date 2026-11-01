import os
from datetime import datetime
from dotenv import load_dotenv
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

load_dotenv()

EXCEL_FILE = os.getenv("EXCEL_FILE")
URL = os.getenv("SITE_URL")
VALID_USER = os.getenv("VALID_USER")
VALID_PASS = os.getenv("VALID_PASS")
INVALID_USER = os.getenv("INVALID_USER", "wrong_user")
INVALID_PASS = os.getenv("INVALID_PASS", "wrong_pass")
TESTER_NAME = os.getenv("TESTER_NAME")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")

STATUS_PASS = "Pass"   # must match your dropdown values
STATUS_FAIL = "Fail"

USERNAME_BOX = (By.XPATH, "//input[@placeholder='Username/Email']")
PASSWORD_BOX = (By.XPATH, "//input[@placeholder='Password']")
ERROR_MSG = (By.CSS_SELECTOR,
             "[role='alert'], .error, .alert-danger, .toast, .snackbar, "
             ".mat-mdc-snack-bar-label, .mat-snack-bar-container, .swal2-popup")

COL_ID, COL_ACTUAL, COL_STATUS, COL_EVIDENCE, COL_DATE, COL_TESTER = 1, 5, 6, 7, 8, 9
FIRST_DATA_ROW = 5

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def short_error(e):
    if isinstance(e, NoSuchElementException):
        return "Element not found on the page (locator issue)"
    if isinstance(e, TimeoutException):
        return "Timed out waiting for the page/element"
    return "Error: " + str(e).splitlines()[0]


def login(driver, username, password):
    driver.get(URL)
    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located(USERNAME_BOX)
    ).send_keys(username)
    pwd = driver.find_element(*PASSWORD_BOX)
    pwd.send_keys(password)
    pwd.send_keys(Keys.ENTER)


def write_excel(tc_id, ok, actual, shot):
    wb = load_workbook(EXCEL_FILE)
    ws = wb.active

    row = FIRST_DATA_ROW
    found = False
    while ws.cell(row=row, column=COL_ID).value:
        if str(ws.cell(row=row, column=COL_ID).value).strip() == tc_id:
            ws.cell(row=row, column=COL_ACTUAL).value = actual
            ws.cell(row=row, column=COL_STATUS).value = STATUS_PASS if ok else STATUS_FAIL
            ws.cell(row=row, column=COL_EVIDENCE).value = shot
            ws.cell(row=row, column=COL_DATE).value = datetime.now().strftime("%d-%b-%y")
            ws.cell(row=row, column=COL_TESTER).value = TESTER_NAME
            found = True
            break
        row += 1

    if not found:
        print(f"{tc_id} not found in Excel")
        return

    # Recount totals from the Status column (works across separate runs)
    passed = failed = 0
    r = FIRST_DATA_ROW
    while ws.cell(row=r, column=COL_ID).value:
        status = ws.cell(row=r, column=COL_STATUS).value
        passed += status == STATUS_PASS
        failed += status == STATUS_FAIL
        r += 1

    ws["D2"] = passed + failed
    ws["F2"] = passed
    ws["H2"] = failed
    wb.save(EXCEL_FILE)


def run_test(tc_id, test_func):
    driver = webdriver.Chrome()
    driver.maximize_window()
    try:
        result = test_func(driver)
        if result is None:
            ok, actual = False, "Test returned no result (missing return)"
        else:
            ok, actual = result
    except Exception as e:
        ok, actual = False, short_error(e)

    shot = os.path.join(SCREENSHOT_DIR, f"{tc_id}.png")
    driver.save_screenshot(shot)
    driver.quit()

    write_excel(tc_id, ok, actual, shot)
    print(f"{tc_id}: {'PASS' if ok else 'FAIL'} - {actual}")