"""
Shared helpers for all DMS test scripts (config from .env, login, Excel, screenshots,
open a document, click by label, popups, messages, second user, run a test case).
Keep this file in the same folder as the test scripts.
"""
import os
import re
import shutil
import time
import traceback
import uuid
from collections import Counter
from datetime import datetime

import openpyxl
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

load_dotenv()

# config (from .env)
BASE_URL = os.getenv("BASE_URL")
USERNAME = os.getenv("DMS_USERNAME")
PASSWORD = os.getenv("DMS_PASSWORD")
OTHER_USERNAME = os.getenv("OTHER_USERNAME")
OTHER_PASSWORD = os.getenv("OTHER_PASSWORD")
EXCEL_PATH = os.getenv("EXCEL_PATH")
SAMPLE_DIR = os.getenv("SAMPLE_DIR")
TESTER_NAME = os.getenv("TESTER_NAME")
SHEET_NAME = os.getenv("SHEET_NAME", "DMS")
SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "screenshots")
DOWNLOAD_DIR = os.path.abspath(os.getenv("DOWNLOAD_DIR", "downloads"))
DEBUG_DIR = os.path.abspath(os.getenv("DEBUG_DIR"))    
EVIDENCE_LINK = os.getenv("EVIDENCE_LINK")
EVIDENCE_HEADER = os.getenv("EVIDENCE_HEADER", "remark").lower()
HEADER_ROW = 4

EXTENSIONS = [
    "pdf", "png", "jpg", "jpeg", "svg", "gif", "mp3", "mp4", "doc", "docx",
    "xls", "xlsx", "csv", "ppt", "pptx", "msg", "eml", "txt",
]

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(DEBUG_DIR, exist_ok=True)

# URLs
EXPLORER_URL = BASE_URL + "/dms/document/explorer/"
ROOT_URL = BASE_URL + "/dms/document/root"
DELETED_ROOT_URL = BASE_URL + "/dms/document/deleted-root"
RESTORE_URL = BASE_URL + "/dms/restore/"
CHECKOUT_URL = BASE_URL + "/dms/document/checkout/"
BULK_URL = BASE_URL + "/dms/document/upload/bulk-upload/"
REVIEW_URL = BASE_URL + "/dms/document/pending-for-review/"
MASTER_TABLE_URL = BASE_URL + "/dms/document/settings/master-table-method/"
ATTACH_URL = BASE_URL + "/dms/document/upload/standard_upload/"
PENDING_URL = BASE_URL + "/dms/document/upload/standard_upload/filesave/pendingmetalist/"
REQUESTED_DOWNLOAD_URL = BASE_URL + "/requested_downloads/view/"

# locators
LOGIN_USER = (By.XPATH, "//input[contains(@placeholder, 'Username')]")
LOGIN_PASS = (By.XPATH, "//input[contains(@placeholder, 'Password')]")
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
DOC_TYPE_BOX = (By.CSS_SELECTOR, "span.select2-selection[aria-labelledby='select2-DocumentType-container']")
DOC_TYPE_RESULTS = "#select2-DocumentType-results"
DOC_TYPE_SEARCH_BOX = (
    By.XPATH,
    "//ul[@id='select2-DocumentType-results']/ancestor::span[contains(@class, 'select2-dropdown')]"
    "//input[contains(@class, 'select2-search__field')]",
)
DOC_TYPE_OPTION = DOC_TYPE_RESULTS + " li.select2-results__option"
DOC_TYPE_SEARCH_TERMS = (
    [os.getenv("DOC_TYPE")]
    if os.getenv("DOC_TYPE")
    else ["1 FC Test updated/aa", "aa", "doc", "inv", "rep", "con", "ent", "ion", "ing"]
)
METADATA_PANEL = (By.ID, "add_meta_data")
UPLOAD_BTN = (By.ID, "submit_meta_data")
SEARCH_BOX = (By.ID, "search_text")
SEARCH_RESULTS = (By.ID, "search_result_list_group")
FILTER_BTN = (By.CSS_SELECTOR, "button.filter-btn")

MESSAGE_BOX = (
    ".toast, .alert, .swal2-popup, [role='alert'], .snackbar, .Toastify__toast, "
    ".mat-snack-bar-container, .ant-message, .growl-animated, [data-notify], [data-growl='container']"
)
SUCCESS_WORDS = [
    "success", "uploaded", "saved", "archived", "restored", "deleted", "created",
    "updated", "checked", "linked", "unlinked", "shared", "sent", "added", "removed",
    "published", "assigned", "cloned", "enabled", "disabled", "approved", "rejected", "downloaded",
]
ERROR_WORDS = ["error", "failed", "required", "already exists", "invalid"]

LOWER = "translate({0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ-_', 'abcdefghijklmnopqrstuvwxyz  ')"
MODAL = (
    "//div[contains(concat(' ', normalize-space(@class), ' '), ' modal ') "
    "and (contains(concat(' ', normalize-space(@class), ' '), ' in ') or contains(@class, 'show'))]"
)
CLICKABLE = "self::a or self::button or self::i or self::span or self::li or self::label or self::td or self::div"
FIELD_XPATH = (
    "following::*[(self::input or self::textarea or self::select) "
    "and not(ancestor::*[contains(@class, 'bs-searchbox')]) "
    "and not(contains(@class, 'select2-search__field'))][1]"
)


class SetupError(Exception):
    """Raised when test data could not be prepared; nothing is written to Excel."""


# login & session
def login(driver, wait):
    driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located(LOGIN_USER)).send_keys(USERNAME)
    driver.find_element(*LOGIN_PASS).send_keys(PASSWORD, Keys.ENTER)
    wait.until(EC.invisibility_of_element_located(LOGIN_USER))


def login_page_shown(driver, seconds=5):
    try:
        WebDriverWait(driver, seconds).until(EC.visibility_of_element_located(LOGIN_USER))
        return True
    except Exception:
        return False


def clear_session(driver):
    try:
        driver.delete_all_cookies()
    except Exception:
        pass
    try:
        driver.execute_script("window.localStorage.clear(); window.sessionStorage.clear();")
    except Exception:
        pass


def login_as(driver, wait, username, password):
    driver.get(BASE_URL)
    if not login_page_shown(driver, 5):
        clear_session(driver)
        driver.get(BASE_URL)
    wait.until(EC.visibility_of_element_located(LOGIN_USER)).send_keys(username)
    driver.find_element(*LOGIN_PASS).send_keys(password, Keys.ENTER)
    try:
        wait.until(EC.invisibility_of_element_located(LOGIN_USER))
    except Exception:
        raise SetupError(
            f"login as '{username}' did not work (still on the login page). "
            f"Check the user name and password in .env. Page said: {popup_text(driver) or 'nothing'}"
        )


def logout(driver):
    driver.get(BASE_URL + "/login/logout/")
    if not login_page_shown(driver, 5):
        clear_session(driver)
        driver.get(BASE_URL)


def as_other_user(driver, wait, function):
    """Log in as the second user, run function(), and log back in as the main user."""
    logout(driver)
    login_as(driver, wait, OTHER_USERNAME, OTHER_PASSWORD)
    try:
        return function()
    finally:
        logout(driver)
        login_as(driver, wait, USERNAME, PASSWORD)


def need_other_user():
    if not (OTHER_USERNAME and OTHER_PASSWORD):
        raise SystemExit("Set OTHER_USERNAME and OTHER_PASSWORD in .env (a second permitted general user), then run again.")


def need_env(name, hint=""):
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Set {name} in .env {hint}, then run again.")
    return value


# files, screenshots & Excel
def find_sample_file(ext):
    """Return (file name, full path) of any file in SAMPLE_DIR ending with .<ext>, or None."""
    for name in os.listdir(SAMPLE_DIR):
        if name.lower().endswith("." + ext):
            return name, os.path.abspath(os.path.join(SAMPLE_DIR, name))
    return None


def save_shot(driver, test_case_id, ext, result):
    driver.save_screenshot(os.path.join(SCREENSHOT_DIR, f"{test_case_id}_{ext}_{result}.png"))


def fail(driver, test_case_id, slug, message):
    """Save failure screenshot and page HTML; return (False, message)."""
    shown = popup_text(driver)
    if shown and shown.lower() not in message.lower():
        message += f" - page said: {shown}"
    save_shot(driver, test_case_id, slug, "FAIL")
    with open(os.path.join("debug", f"{test_case_id}_{slug}.html"), "w", encoding="utf-8") as file:
        file.write(driver.page_source)
    return False, message


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

    columns = {
        "actual": col_of("actual"),
        "status": col_of("status"),
        "evidence": col_of(EVIDENCE_HEADER),
        "date": col_of("date"),
        "tester": col_of("tester"),
    }

    row = None
    for r in range(HEADER_ROW + 1, ws.max_row + 1):
        if str(ws.cell(r, 1).value or "").strip() == test_case_id:
            row = r
            break
    return row, columns


def check_excel_ready(test_case_id):
    """Ensure the test case row exists in Excel and the workbook is not locked."""
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
    values = {
        "actual": actual,
        "status": status,
        "evidence": "Evidence Doc",
        "date": datetime.now().strftime("%d-%b-%Y"),
        "tester": TESTER_NAME,
    }
    for key, col in columns.items():
        if col:
            ws.cell(row, col).value = values[key]
    if columns["evidence"] and EVIDENCE_LINK:
        cell = ws.cell(row, columns["evidence"])
        cell.hyperlink = EVIDENCE_LINK
        cell.style = "Hyperlink"
    wb.save(EXCEL_PATH)
    print(f"Saved to: {os.path.abspath(EXCEL_PATH)}  (sheet '{ws.title}')")
    check = openpyxl.load_workbook(EXCEL_PATH)[SHEET_NAME]
    for key, col in columns.items():
        if col:
            cell = check.cell(row, col)
            print(f"  {cell.coordinate} [{check.cell(HEADER_ROW, col).value}] = {cell.value!r}")


# text & error helpers
def xpath_text(text):
    """Safely quote text for an XPath expression, including strings containing apostrophes."""
    text = str(text)
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    parts = text.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text.lower()


def clean(text):
    return re.sub(r"[*:]", "", text or "").strip().lower()


def visible(driver, css):
    return [e for e in driver.find_elements(By.CSS_SELECTOR, css) if e.is_displayed()]


def short(error):
    """Concise error summary; includes call location when the exception message is empty."""
    lines = str(error).splitlines()
    first = lines[0].strip()[:120] if lines else ""
    if not first:
        try:
            frames = [
                f for f in traceback.extract_tb(error.__traceback__)
                if "site-packages" not in f.filename and f.name not in ("run", "<module>", "<lambda>")
            ]
            if frames:
                first = "no message, happened in " + " > ".join(f.name for f in frames) + f" (line {frames[-1].lineno})"
        except Exception:
            pass
    return f"{type(error).__name__}: {first}"


# messages & notifications
def popup_text(driver):
    boxes = [
        e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, MESSAGE_BOX)
        if e.is_displayed() and e.text.strip()
    ]
    return " | ".join(boxes)


def wait_for_message(driver, text_before, seconds=20):
    """Wait for a new success/error message. Returns (is_success, message)."""
    def new_message(d):
        boxes = [
            e.text.strip() for e in d.find_elements(By.CSS_SELECTOR, MESSAGE_BOX)
            if e.is_displayed() and e.text.strip()
        ]
        try:
            saved = d.execute_script("return sessionStorage.getItem('__last_notify_msg') || '';")
        except Exception:
            saved = ""
        if saved and saved not in boxes:
            boxes.append(saved)
        for text in [b.lower() for b in boxes] + [body_text(d)]:
            for word in SUCCESS_WORDS + ERROR_WORDS:
                if word in text and word not in text_before:
                    return word, (boxes[0] if boxes else word)
        return None

    word, msg = WebDriverWait(driver, seconds).until(new_message)
    try:
        driver.execute_script("sessionStorage.removeItem('__last_notify_msg');")
    except Exception:
        pass
    return word in SUCCESS_WORDS, msg


def message_after(driver, action):
    """Run action() and wait for the confirmation or error message. Returns (True/False, message)."""
    try:
        WebDriverWait(driver, 6).until(lambda d: not visible(d, MESSAGE_BOX))
    except Exception:
        pass
    try:
        driver.execute_script("""
            sessionStorage.removeItem('__last_notify_msg');
            if (typeof window.notify === 'function' && !window.__notify_wrapped) {
                var orig = window.notify;
                window.notify = function(title, message) {
                    var full = [title, message].filter(Boolean).join(' ').trim();
                    if (full) { sessionStorage.setItem('__last_notify_msg', full); }
                    return orig.apply(this, arguments);
                };
                window.__notify_wrapped = true;
            }
        """)
    except Exception:
        pass
    text_before = body_text(driver)
    action()
    ok, message = wait_for_message(driver, text_before)
    message = re.sub(r"^[×x]?\s*close\s*", "", " ".join(message.split()), flags=re.I)
    return ok, message


def wait_text(driver, text, seconds=8):
    """True if text appears on the page within the given seconds."""
    try:
        WebDriverWait(driver, seconds).until(lambda d: text.lower() in body_text(d))
        return True
    except Exception:
        return False


# find and click
def predicate(label, exact):
    """XPath predicate matching text, title, aria-label, or value (case-insensitive, '-' and '_' treated as spaces)."""
    text = label.lower().replace("-", " ").replace("_", " ")
    fields = [
        LOWER.format("normalize-space(.)"),
        LOWER.format("normalize-space(@title)"),
        LOWER.format("normalize-space(@data-original-title)"),
        LOWER.format("normalize-space(@aria-label)"),
        LOWER.format("normalize-space(@value)"),
    ]
    if exact:
        return "[" + " or ".join(f"{f} = {xpath_text(text)}" for f in fields) + "]"
    return "[" + " or ".join(f"contains({f}, {xpath_text(text)})" for f in fields) + "]"


def find_by_label(driver, label, root=None, slack=25):
    """Find the first visible button, icon, or link matching label. Checks open modals first."""
    if root is None:
        low = label.lower()
        if low in ("save changes", "save"):
            update_btns = visible(driver, "#editMeta button[data-type='updateMeta']")
            if update_btns:
                return update_btns[0]
        if low == "download":
            dl_btns = [
                b for b in visible(driver, "#search_modal button.search_result_download")
                if b.is_enabled()
            ]
            if dl_btns:
                return dl_btns[0]
            if visible(driver, "#requested_downloads"):
                links = visible(driver, "#requested_downloads tbody a[href]")
                return links[0] if links else None
        if visible(driver, "#search_modal"):
            rows = driver.find_elements(By.XPATH, f"//div[@id='search_modal']//tr[contains(., {xpath_text(label)})]")
            for r in rows:
                if r.is_displayed():
                    open_icons = [
                        el for el in r.find_elements(
                            By.XPATH,
                            ".//*[contains(@class, 'openInNew') or contains(@title, 'Open') or contains(@data-original-title, 'Open')] | "
                            ".//td[last()]//*[self::a or self::button or self::i]"
                        )
                        if el.is_displayed()
                    ]
                    if open_icons:
                        return open_icons[-1]
        three_dot = visible(driver, "#three-dot > li.dropdown > a")
        menu = driver.find_elements(By.CSS_SELECTOR, "#three-dot ul.dropdown-menu")
        if three_dot and menu:
            items = menu[0].find_elements(By.XPATH, f".//a{predicate(label, False)}")
            if items:
                if not menu[0].is_displayed():
                    click(driver, three_dot[0])
                    time.sleep(0.5)
                visible_items = [e for e in items if e.is_displayed()]
                if visible_items:
                    return visible_items[0]

    scopes = [None] if root is not None else [MODAL, ""]
    for scope in scopes:
        for exact in (True, False):
            if root is not None:
                found = root.find_elements(By.XPATH, f".//*[{CLICKABLE}]{predicate(label, exact)}")
            else:
                found = driver.find_elements(By.XPATH, f"{scope}//*[{CLICKABLE}]{predicate(label, exact)}")
            found = [e for e in found if e.is_displayed() and len(e.text.strip()) <= len(label) + slack]
            if found:
                return found[0]
    return None


def find_near(driver, anchor_text, label):
    """Find the button or icon `label` in the same row, card, or section as `anchor_text`."""
    anchor = find_by_label(driver, anchor_text, slack=300)
    if anchor is None:
        return None
    try:
        container = anchor.find_element(By.XPATH, f"ancestor::*[.//*[{CLICKABLE}]{predicate(label, False)}][1]")
    except NoSuchElementException:
        return None
    return find_by_label(driver, label, root=container)


def click(driver, element):
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
    try:
        element.click()
    except Exception:
        driver.execute_script("arguments[0].click();", element)


def click_label(driver, wait, label, slack=25):
    element = WebDriverWait(driver, 10).until(lambda d: find_by_label(d, label, slack=slack))
    action = element.get_attribute("data-action") or ""
    click(driver, element)
    if action == "editMeta":
        time.sleep(2)
    return element


def click_near(driver, wait, anchor_text, label):
    element = WebDriverWait(driver, 10).until(lambda d: find_near(d, anchor_text, label))
    click(driver, element)
    return element


def double_click_label(driver, wait, label):
    element = WebDriverWait(driver, 10).until(lambda d: find_by_label(d, label))
    ActionChains(driver).double_click(element).perform()


def confirm(driver, wait, label="yes", seconds=15):
    """Click the confirmation button in a SweetAlert or Bootstrap modal. Returns False if none appeared."""
    def shown_button(d):
        for b in d.find_elements(By.CSS_SELECTOR, ".swal2-confirm, .swal2-modal button, .modal.in button, .modal.show button"):
            if b.is_displayed() and (label in b.text.lower() or "swal2-confirm" in (b.get_attribute("class") or "")):
                return b
        return None

    def enabled_button(d):
        b = shown_button(d)
        if not (b and b.is_enabled() and "disabled" not in (b.get_attribute("class") or "").lower()):
            return None
        bars = [p for p in d.find_elements(By.ID, "progressBar") if p.is_displayed()]
        if bars and bars[0].get_attribute("value") != bars[0].get_attribute("max"):
            return None
        return b

    try:
        WebDriverWait(driver, min(seconds, 5)).until(shown_button)
        click(driver, WebDriverWait(driver, seconds).until(enabled_button))
        return True
    except Exception:
        return False


def confirm_any(driver, wait, labels=("yes", "ok", "submit", "reject")):
    for label in labels:
        if confirm(driver, wait, label, seconds=2):
            return True
    return False


def do(driver, wait, label, confirm_label=None):
    """Click a button/icon by label, confirm if requested, and return (True/False, message)."""
    def action():
        click_label(driver, wait, label)
        if confirm_label:
            confirm(driver, wait, confirm_label)
    return message_after(driver, action)


def do_near(driver, wait, anchor_text, label, confirm_label=None):
    """Click a button/icon near anchor_text, confirm if requested, and return (True/False, message)."""
    def action():
        click_near(driver, wait, anchor_text, label)
        if confirm_label:
            confirm(driver, wait, confirm_label)
    return message_after(driver, action)


# ---------- form fields & Select2 ----------
def find_field(driver, label_text):
    """Return the input, textarea, or select following the label with `label_text`."""
    wanted = label_text.lower()
    labels = [lb for lb in driver.find_elements(By.TAG_NAME, "label") if lb.is_displayed()]
    for matches in (lambda t: t == wanted, lambda t: t.startswith(wanted), lambda t: wanted in t):
        for label in labels:
            if matches(clean(label.text)):
                try:
                    return label.find_element(By.XPATH, FIELD_XPATH)
                except NoSuchElementException:
                    continue
    return None


def fill_field(driver, label_text, value):
    field = WebDriverWait(driver, 10).until(lambda d: find_field(d, label_text))
    field.clear()
    field.send_keys(value)


def pick_option(driver, label_text, option_text=None):
    """Choose an option from the dropdown following `label_text`."""
    field = WebDriverWait(driver, 10).until(lambda d: find_field(d, label_text))
    if field.tag_name == "select" and field.is_displayed():
        select = Select(field)
        for option in select.options:
            if option.get_attribute("value") and (not option_text or option_text.lower() in option.text.lower()):
                select.select_by_visible_text(option.text)
                return option.text
        raise Exception(f"no option '{option_text}' in '{label_text}'")
    button = field.find_element(
        By.XPATH, "following::*[contains(@class, 'dropdown-toggle') or contains(@class, 'select2-selection')][1]"
    )
    click(driver, button)
    time.sleep(1)
    options = [o for o in visible(driver, ".dropdown-menu.open li:not(.disabled) a, .select2-results__option") if o.text.strip()]
    if option_text:
        options = [o for o in options if option_text.lower() in o.text.lower()] or options
    text = options[0].text
    click(driver, options[0])
    return text


def select2_options(driver, css=DOC_TYPE_OPTION):
    """Visible Select2 options, excluding status messages ('Searching...', 'Please enter...', etc.)."""
    skip = ("please enter", "searching", "no result", "loading")
    try:
        return [
            o for o in driver.find_elements(By.CSS_SELECTOR, css)
            if o.is_displayed() and o.text.strip() and not any(w in o.text.lower() for w in skip)
        ]
    except StaleElementReferenceException:
        return []


def best_option_index(options, term):
    """Index of the option matching `term` (matches full path on `title` when `term` contains '/')."""
    wanted = term.strip().strip("/").lower()
    leaf = wanted.split("/")[-1]
    if "/" in wanted:
        for i, o in enumerate(options):
            title = (o.get_attribute("title") or o.text or "").strip().strip("/").lower()
            if title == wanted or title.endswith(wanted):
                return i
    for i, o in enumerate(options):
        title = (o.get_attribute("title") or o.text or "").strip().strip("/").lower()
        if title == leaf or title.split("/")[-1] == leaf:
            return i
    return 0

def pick_select2(driver, wait, term, nth=0):
    """Open the nth visible Select2 dropdown, type `term`, and pick the first result."""
    boxes = visible(driver, "span.select2-selection")
    click(driver, boxes[nth])
    search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))
    for letter in term:
        ActionChains(driver).send_keys(letter).perform()
        time.sleep(0.3)

    options = WebDriverWait(driver, 10).until(lambda d: select2_options(d, ".select2-results__option"))
    text = options[0].text.strip()
    search.send_keys(Keys.ENTER)
    return text


def pick_select2_by_id(driver, wait, select_id, term):
    """Open a Select2 dropdown by its underlying select ID, type `term`, and select the matching option."""
    box = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"span.select2-selection[aria-labelledby='select2-{select_id}-container']"))
    )
    click(driver, box)
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input.select2-search__field")))
    wanted = term.strip().strip("/").split("/")[-1]
    for letter in wanted[:5]:
        ActionChains(driver).send_keys(letter).perform()
        time.sleep(0.2)

    option_css = f"#select2-{select_id}-results .select2-results__option"
    WebDriverWait(driver, 10).until(lambda d: bool(select2_options(d, option_css)))
    time.sleep(1.5)

    def chosen():
        labels = driver.find_elements(By.ID, f"select2-{select_id}-container")
        if not labels:
            return True
        text = labels[0].text.replace("×", "").strip().lower()
        return bool(text) and "search for" not in text

    for _ in range(3):
        try:
            found = select2_options(driver, option_css)
            target = found[best_option_index(found, term)]
            driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", target)
            ActionChains(driver).move_to_element(target).click().perform()
            break
        except (StaleElementReferenceException, IndexError):
            time.sleep(1)
    time.sleep(1)
    if not chosen():
        ActionChains(driver).send_keys(Keys.ENTER).perform()
        time.sleep(1)
    if not chosen():
        raise SetupError(f"the value '{wanted}' could not be selected in the '{select_id}' drop-down")


def modal_text_input(driver):
    """First enabled, visible text input inside an open modal."""
    boxes = driver.find_elements(By.XPATH, f"{MODAL}//input[@type='text' or not(@type)]")
    boxes = [b for b in boxes if b.is_displayed() and b.is_enabled() and not b.get_attribute("readonly")]
    return boxes[0] if boxes else None


def attach_to_file_input(driver, wait, path):
    """Send a file path to the file input inside an open modal, or the page's main upload input."""
    modal_inputs = driver.find_elements(By.XPATH, f"{MODAL}//input[@type='file']")
    inputs = modal_inputs or [
        i for i in driver.find_elements(*FILE_INPUT)
        if i.get_attribute("id") != "signature_upload" and "swal2-file" not in (i.get_attribute("class") or "")
    ]
    file_input = inputs[-1]
    driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", file_input)
    file_input.send_keys(path)


# downloads
def wait_for_download(before, seconds=30):
    """Return the name of a newly finished file in DOWNLOAD_DIR, or None."""
    end = time.time() + seconds
    while time.time() < end:
        new = [n for n in set(os.listdir(DOWNLOAD_DIR)) - before if not n.endswith((".crdownload", ".tmp"))]
        if new:
            return new[0]
        time.sleep(1)
    return None


# document upload
def pending_row_icon(file_name):
    return (
        By.XPATH,
        f"//*[@id='list_view_container']//tr[@data-pending-doc-name={xpath_text(file_name)}]//i[contains(@class, 'add-item')]",
    )


def clear_selected_files(driver):
    xpath = "//*[@id='selected_file_div']//*[contains(@class, 'deselect-row')]//i[contains(@class, 'delete-item')]"
    for _ in range(20):
        icons = driver.find_elements(By.XPATH, xpath)
        if not icons:
            return
        driver.execute_script("arguments[0].click();", icons[0])
        time.sleep(1)


def selected_count(driver):
    return len(visible(driver, "#selected_file_div .deselect-row"))


def select_document_type(driver, wait, terms=None):
    wait.until(EC.element_to_be_clickable(DOC_TYPE_BOX)).click()
    search_box = wait.until(EC.visibility_of_element_located(DOC_TYPE_SEARCH_BOX))
    search_box.click()
    for term in terms or DOC_TYPE_SEARCH_TERMS:
        typed = term.strip().strip("/").split("/")[-1]
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
        for letter in typed:
            ActionChains(driver).send_keys(letter).perform()
            time.sleep(0.2)
        try:
            WebDriverWait(driver, 8).until(lambda d: bool(select2_options(d)))
        except Exception:
            continue
        time.sleep(1.5)
        options = select2_options(driver)
        if options:
            index = best_option_index(options, term)
            option = options[index]
            print(f"   doc-type: picked '{option.get_attribute('title')}' (result {index + 1} of {len(options)})")
            if index == 0:
                ActionChains(driver).send_keys(Keys.ENTER).perform()
            else:
                driver.execute_script("arguments[0].scrollIntoView({block: 'nearest'});", option)
                ActionChains(driver).move_to_element(option).click().perform()
            time.sleep(1)
            selected = driver.find_element(By.ID, "select2-DocumentType-container").text.strip()
            if selected and "search for a document type" not in selected.lower():
                time.sleep(2)
                return
            options = select2_options(driver)
            if options:
                ActionChains(driver).click(options[best_option_index(options, term)]).perform()
                time.sleep(2)
                return
    raise SetupError("document type could not be selected")


def fill_metadata_form(driver, wait, terms=None):
    """Select the document type and fill visible required metadata fields with unique values."""
    select_document_type(driver, wait, terms)
    run_id = datetime.now().strftime("%H%M%S%f")[:8]
    for attempt in range(3):
        try:
            panel = driver.find_element(*METADATA_PANEL)
            labels = panel.find_elements(By.XPATH, ".//label")
            for i, label in enumerate(labels):
                ltext = label.text.lower().strip()
                if not ltext or any(k in ltext for k in ("document type", "share with", "file name", "tag")):
                    continue
                is_required = "*" in label.text
                try:
                    field = label.find_element(By.XPATH, FIELD_XPATH)
                except NoSuchElementException:
                    continue

                if field.tag_name == "select":
                    if not is_required:
                        continue
                    driver.execute_script("""
                        var sel = arguments[0];
                        if (!sel.value) {
                            var valid = [];
                            for (var i = 0; i < sel.options.length; i++) {
                                var val = sel.options[i].value;
                                var txt = (sel.options[i].text || '').trim().toLowerCase();
                                if (val && !sel.options[i].disabled && txt !== 'none' && txt !== 'nothing selected') {
                                    valid.push(sel.options[i]);
                                }
                            }
                            if (sel.multiple && sel.getAttribute('data-parsley-unique_meta') === 'unique' && valid.length >= 4) {
                                var shuffled = valid.slice().sort(function() { return Math.random() - 0.5; });
                                var count = Math.min(valid.length, 4 + Math.floor(Math.random() * 3));
                                for (var j = 0; j < count; j++) {
                                    shuffled[j].selected = true;
                                }
                            } else if (valid.length > 0) {
                                valid[0].selected = true;
                                sel.value = valid[0].value;
                            }
                            if (window.$) {
                                $(sel).trigger('change');
                                if ($.fn.selectpicker) { $(sel).selectpicker('refresh'); }
                            }
                        }
                    """, field)
                    continue

                if not field.is_displayed() or field.get_attribute("value"):
                    continue

                field_id = (field.get_attribute("id") or "").lower()
                field_type = (field.get_attribute("type") or "").lower()
                outer_html = (field.get_attribute("outerHTML") or "").lower()

                if "date" in field_id or "expires" in field_id:
                    if is_required:
                        field.send_keys(datetime.now().strftime("%Y-%m-%d"))
                elif field_type == "number" or any(w in outer_html for w in ("digits", "number", "integer", "numeric")):
                    field.send_keys(str(int(run_id[-5:]) + i + 1))
                else:
                    field.send_keys(f"AUTO_{run_id}_{i}")
            return
        except StaleElementReferenceException:
            if attempt == 2:
                raise
            time.sleep(1)


def current_doc_type(driver):
    return driver.find_element(By.ID, "select2-DocumentType-container").text.replace("×", "").strip()


def unique_copy(path):
    """Create a copy of `path` with a unique filename and unique trailing bytes so checksum checks pass."""
    folder = os.path.join(DOWNLOAD_DIR, "upload_copies")
    os.makedirs(folder, exist_ok=True)
    name = datetime.now().strftime("AUTO%H%M%S%f")[:12] + "_" + os.path.basename(path)
    new_path = os.path.join(folder, name)
    shutil.copy2(path, new_path)
    with open(new_path, "ab") as f:
        f.write(("\n%unique " + uuid.uuid4().hex + "\n").encode())
    return name, new_path


def pending_names(driver):
    """Return all document names across pages in the Pending Files list."""
    names, seen = [], set()
    for _ in range(10):
        page = [
            r.get_attribute("data-pending-doc-name")
            for r in driver.find_elements(By.CSS_SELECTOR, "#list_view_container tr.pending-meta")
        ]
        if tuple(page) in seen:
            break
        seen.add(tuple(page))
        names += page
        more = [b for b in visible(driver, "#pagination button.next") if b.is_enabled()]
        if not more:
            break
        click(driver, more[0])
        time.sleep(1.5)
    return names


def open_pending_list(driver, wait):
    driver.get(PENDING_URL)
    wait.until(EC.presence_of_element_located((By.ID, "list_view_container")))
    time.sleep(2)


def click_pending_icon(driver, file_name):
    """Click the paperclip icon for `file_name` in the Pending Files list."""
    for _ in range(10):
        icons = [i for i in driver.find_elements(*pending_row_icon(file_name)) if i.is_displayed()]
        if icons:
            click(driver, icons[0])
            return True
        more = [b for b in visible(driver, "#pagination button.next") if b.is_enabled()]
        if not more:
            return False
        click(driver, more[0])
        time.sleep(1.5)
    return False


def attach_new_file(driver, wait, path):
    """Attach `path` via Dropzone on the Attach Documents page and return its Pending Files name."""
    open_pending_list(driver, wait)
    before = Counter(pending_names(driver))
    driver.get(ATTACH_URL)
    try:
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.dz-hidden-input"))
        )
    except Exception:
        raise SetupError(f"the Dropzone file input was not found on the Attach Documents page: {driver.current_url}")
    file_input.send_keys(path)
    try:
        WebDriverWait(driver, 60).until(
            lambda d: d.find_elements(By.CSS_SELECTOR, ".dz-preview.dz-success, .dz-preview.dz-error")
        )
    except Exception:
        pass
    errors = [
        e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, ".dz-preview.dz-error .dz-error-message")
        if e.text.strip()
    ]
    if errors:
        print(f"   Attach Documents page refused the file: {errors[0]}")
        return None
    for _ in range(6):
        time.sleep(3)
        open_pending_list(driver, wait)
        new = Counter(pending_names(driver)) - before
        if new:
            return next(iter(new))
    return None


def prepare_upload(driver, wait, ext="pdf", doc_type=None, fill=True):
    """Attach a sample file, select it in the Pending list, pick Document Type, and optionally fill required metadata."""
    sample = find_sample_file(ext)
    if not sample:
        raise SetupError(f"no .{ext} sample file in {SAMPLE_DIR}")
    try:
        _, copy_path = unique_copy(sample[1])
        pending_name = attach_new_file(driver, wait, copy_path) or attach_new_file(driver, wait, sample[1])
        if not pending_name:
            raise SetupError(
                f"the system did not add '{sample[0]}' to the Pending Files list, not even as a copy with new content. "
                f"Page said: {popup_text(driver) or 'nothing'}"
            )
        open_pending_list(driver, wait)
        clear_selected_files(driver)
        if selected_count(driver):
            raise SetupError("files from an earlier run are still selected in Pending Documents and could not be removed")
        if not click_pending_icon(driver, pending_name):
            raise SetupError(f"'{pending_name}' is in the Pending Files list but its paperclip icon could not be clicked")
        time.sleep(1)
        if selected_count(driver) != 1:
            raise SetupError(f"the file could not be selected for the meta-data panel. Page said: {popup_text(driver) or 'nothing'}")
        terms = [doc_type] if doc_type else DOC_TYPE_SEARCH_TERMS
        if fill:
            fill_metadata_form(driver, wait, terms)
            if os.getenv("CHECKER_NAME") and driver.find_element(By.ID, "checker-div").is_displayed():
                pick_option(driver, "checker", os.getenv("CHECKER_NAME"))
        else:
            select_document_type(driver, wait, terms)
            time.sleep(2)
    except SetupError:
        raise
    except Exception as error:
        raise SetupError(f"could not prepare the upload ({short(error)}) at {driver.current_url}")
    return pending_name


def set_document_name(driver, name):
    """Set the document name field and return its resulting value."""
    field = driver.find_element(By.ID, "file_name")
    try:
        field.clear()
        field.send_keys(name)
    except Exception:
        pass
    return field.get_attribute("value")


def field_value(driver, field_id):
    """Return the value of `#field_id`, retrying if the form redraws."""
    for _ in range(4):
        try:
            return driver.find_element(By.ID, field_id).get_attribute("value")
        except StaleElementReferenceException:
            time.sleep(1)
    return ""


def filled_values(driver):
    """Return (label, value) pairs of text fields filled with AUTO_ values in the metadata panel."""
    for _ in range(4):
        try:
            pairs = []
            panel = driver.find_element(*METADATA_PANEL)
            for field in panel.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number'], textarea"):
                value = field.get_attribute("value") or ""
                if field.is_displayed() and value.startswith("AUTO_") and field.get_attribute("id") != "file_name":
                    try:
                        label = field.find_element(By.XPATH, "preceding::label[1]").text
                    except NoSuchElementException:
                        label = ""
                    pairs.append((clean(label), value))
            return pairs
        except StaleElementReferenceException:
            time.sleep(1)
    return []


def select_share(driver, kind):
    """Pick an option in the Share With dropdown ('public', 'all users', 'groups', or 'users')."""
    script = """
        var s = document.getElementById('shared_docs'); var picked = '';
        var kind = arguments[0];
        if (kind == 'public') { var o = s.querySelector("option[value='all-1']"); o.selected = true; picked = o.text.trim(); }
        else if (kind == 'all users') { var o = s.querySelector("option[value='all-2']"); o.selected = true; picked = o.text.trim(); }
        else { s.querySelectorAll('optgroup').forEach(function(g) {
            if (g.label.toLowerCase() == kind && !picked) { var o = g.querySelector('option'); if (o) { o.selected = true; picked = o.text.trim(); } } }); }
        $(s).trigger('change');
        return picked;"""
    picked = driver.execute_script(script, kind)
    if not picked:
        raise Exception(f"no '{kind}' option in Share With")
    return picked


def upload_document(driver, wait, ext="pdf", doc_type=None, share=None):
    """Upload one test document with a unique name. Returns {'name', 'doc_type', 'values'}."""
    try:
        prepare_upload(driver, wait, ext, doc_type)
        info = {"doc_type": current_doc_type(driver), "values": filled_values(driver)}
        if share:
            info["shared_with"] = select_share(driver, share)
        info["name"] = set_document_name(driver, datetime.now().strftime("AUTO_%H%M%S"))
        text_before = body_text(driver)
        click(driver, driver.find_element(*UPLOAD_BTN))
        ok, message = wait_for_message(driver, text_before)
    except SetupError:
        raise
    except Exception as error:
        raise SetupError(f"test document did not upload ({short(error)})")
    if not ok:
        raise SetupError(f"test document did not upload ({message})")
    time.sleep(2)
    return info


# search and open
def search_finds(driver, wait, name, tries=1):
    """True if quick search lists `name`."""
    for _ in range(tries):
        driver.get(EXPLORER_URL)
        box = wait.until(EC.element_to_be_clickable(SEARCH_BOX))
        box.clear()
        box.send_keys(name)
        time.sleep(3)
        if name in driver.find_element(*SEARCH_RESULTS).text:
            return True
        time.sleep(3)
    return False


def switch_to_new_tab(driver, old_tabs):
    if len(driver.window_handles) > len(old_tabs):
        driver.switch_to.window(driver.window_handles[-1])


def open_document(driver, wait, name):
    """Find `name` via quick search and open its full document view in a new tab."""
    if not search_finds(driver, wait, name, tries=5):
        raise SetupError(f"document '{name}' not found in quick search")
    old_tabs = driver.window_handles
    row = driver.find_element(By.XPATH, f"//*[@id='search_result_list_group']//a[contains(., {xpath_text(name)})]")
    open_btns = row.find_elements(By.CSS_SELECTOR, ".openInNew")
    click(driver, open_btns[0] if open_btns else row)
    time.sleep(3)
    switch_to_new_tab(driver, old_tabs)


def new_document(driver, wait, ext="pdf", doc_type="1 FC Test updated/aa"):
    """Upload a fresh test document and open it in full view."""
    info = upload_document(driver, wait, ext, doc_type=doc_type)
    open_document(driver, wait, info["name"])
    return info


def fill_search_meta(driver, label_text, value):
    """Fill a metadata input in the advanced search form (labels there are plain text, not <label>)."""
    wanted = label_text.lower()

    def find(d):
        lines = d.find_elements(By.CSS_SELECTOR, "#dms_search_form .meta-data-wrap .fg-line")
        for match in (lambda t: t == wanted, lambda t: t.startswith(wanted)):
            for line in lines:
                if line.is_displayed() and match(clean(line.text)):
                    inputs = line.find_elements(By.CSS_SELECTOR, "input[id]:not([type='hidden'])")
                    if inputs:
                        return inputs[0]
        return None

    try:
        field = WebDriverWait(driver, 10).until(find)
    except TimeoutException:
        names = [clean(l.text) for l in driver.find_elements(By.CSS_SELECTOR, "#dms_search_form .meta-data-wrap .fg-line")]
        raise SetupError(f"search form has no metadata field '{label_text}'. Fields on page: {names}")
    field.clear()
    field.send_keys(value)


def advanced_search(driver, wait, name, include_archive=False, match_all=True, doc_type=None, extra=None, submit=True):
    """Fill the advanced search form and (unless submit=False) click Search."""
    if not visible(driver, "#dms_search_form"):
        click(driver, wait.until(EC.element_to_be_clickable(FILTER_BTN)))
    box = wait.until(EC.visibility_of_element_located((By.ID, "docname")))
    box.clear()
    box.send_keys(name or "")
    if doc_type:
        pick_select2_by_id(driver, wait, "documentType", doc_type)
    for field_label, value in (extra or []):
        fill_search_meta(driver, field_label, value)
    for checkbox_id, wanted in (("include_archive", include_archive), ("match_all", match_all)):
        if driver.find_element(By.ID, checkbox_id).is_selected() != wanted:
            click(driver, driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}'].ts-helper"))
    if submit:
        click(driver, driver.find_element(By.ID, "search_btn"))
        time.sleep(3)


def advanced_finds(driver, wait, name, **options):
    driver.get(EXPLORER_URL)
    advanced_search(driver, wait, name, **options)
    return name.lower() in body_text(driver)


def explorer_has(driver, wait, doc_type, name):
    """Open Explorer, expand all jsTree folders via API, click doc_type, and verify name is listed."""
    driver.get(EXPLORER_URL)
    time.sleep(2)
    leaf = doc_type.strip("/").split("/")[-1]

    try:
        driver.execute_script("""
            if (window.$ && $.jstree) {
                $('.jstree').each(function() {
                    var tree = $(this).jstree(true);
                    if (tree && tree.open_all) { tree.open_all(); }
                });
            }
        """)
        time.sleep(1.5)
    except Exception:
        pass

    anchors = driver.find_elements(
        By.XPATH,
        f"//a[contains(@class, 'jstree-anchor') and normalize-space(.)={xpath_text(leaf)}]"
    )
    if not anchors:
        anchors = driver.find_elements(
            By.XPATH,
            f"//a[contains(@class, 'jstree-anchor') and contains(normalize-space(.), {xpath_text(leaf)} )]"
        )
    if anchors:
        click(driver, anchors[0])
        try:
            ActionChains(driver).double_click(anchors[0]).perform()
        except Exception:
            pass
    else:
        try:
            click_label(driver, wait, leaf)
        except Exception:
            return False

    time.sleep(2.5)
    if wait_text(driver, name, 5):
        return True

    table_filters = visible(driver, "input[type='search'], .dataTables_filter input")
    if table_filters:
        table_filters[0].clear()
        table_filters[0].send_keys(name)
        time.sleep(2)
        if wait_text(driver, name, 4):
            return True

    for _ in range(5):
        next_btns = [
            b for b in visible(driver, ".pagination li:not(.disabled) a.next, .paginate_button.next:not(.disabled), #pagination button.next")
            if b.is_enabled()
        ]
        if not next_btns:
            break
        click(driver, next_btns[0])
        time.sleep(1.5)
        if wait_text(driver, name, 3):
            return True

    return False


# related files & versions
def add_version(driver, wait, suffix="v2"):
    """Open the Add Version modal, attach a PDF, set the extended name and version, and click Upload."""
    _, path = unique_copy(find_sample_file("pdf")[1])
    add_btns = driver.find_elements(By.CSS_SELECTOR, "#version-history-id button[data-type='version'], button[data-type='version']")
    if add_btns:
        click(driver, add_btns[0])
    else:
        click_label(driver, wait, "version history")
        click_label(driver, wait, "add")
    wait.until(EC.visibility_of_element_located((By.ID, "addVersion")))
    time.sleep(1)
    attach_to_file_input(driver, wait, path)
    time.sleep(1)
    extra = driver.find_elements(By.ID, "file_name_extended_part")
    box = extra[0] if extra and extra[0].is_displayed() else modal_text_input(driver)
    if box is not None:
        box.clear()
        box.send_keys(suffix)
    driver.execute_script("""
        var sel = document.getElementById('version');
        if (sel && !sel.value) {
            for (var i = 0; i < sel.options.length; i++) {
                if (sel.options[i].value) { sel.value = sel.options[i].value; break; }
            }
            if (window.$ && $.fn.selectpicker) { $(sel).selectpicker('refresh'); }
        }
        var cmt = document.getElementById('vcomment');
        if (cmt && !cmt.value.trim()) { cmt.value = 'Version upload'; }
    """)
    upload_btns = driver.find_elements(By.CSS_SELECTOR, "#addVersion button[data-type='uploadVersion']")
    if upload_btns:
        ok, msg = message_after(driver, lambda: click(driver, upload_btns[0]))
    else:
        ok, msg = do(driver, wait, "upload")
    if ok:
        time.sleep(3)
    return ok, msg


def show_versions(driver, wait, version_text):
    """Ensure the version history panel is expanded so version rows are visible."""
    panels = driver.find_elements(By.ID, "versionHistory")
    if panels and not panels[0].is_displayed():
        headers = driver.find_elements(By.CSS_SELECTOR, "#version-history-id .card-header")
        if headers:
            click(driver, headers[0])
        else:
            click_label(driver, wait, "version history")
        time.sleep(2)
    elif not panels and find_by_label(driver, version_text, slack=300) is None:
        click_label(driver, wait, "version history")
        time.sleep(2)


# test runner
def start_browser():
    options = Options()
    options.add_experimental_option(
        "prefs",
        {
            "download.default_directory": DOWNLOAD_DIR,
            "download.prompt_for_download": False,
            "profile.default_content_setting_values.automatic_downloads": 1,
        },
    )
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver, WebDriverWait(driver, 15)


def run(test_case_id, scenarios):
    """Verify Excel, launch Chrome, sign in, run all (label, fn) scenarios, and record results in Excel."""
    check_excel_ready(test_case_id)
    driver, wait = start_browser()
    results = []
    setup_problem = None

    try:
        login(driver, wait)
        for label, scenario in scenarios:
            slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
            try:
                ok, msg = scenario(driver, wait)
            except SetupError as error:
                setup_problem = f"{label}: {error}"
                fail(driver, test_case_id, slug, str(error))
                break
            except Exception as error:
                ok, msg = False, short(error)
            if ok:
                save_shot(driver, test_case_id, slug, "PASS")
            else:
                ok, msg = fail(driver, test_case_id, slug, msg)
            print(f"{label:28} -> {'PASS' if ok else 'FAIL'} ({msg})")
            results.append((label, ok, msg))
    finally:
        driver.quit()

    if setup_problem:
        raise SystemExit(f"Could not prepare the test data, nothing was written to Excel. {setup_problem}")

    status = "Pass" if all(ok for _, ok, _ in results) else "Fail"
    if len(results) == 1:
        actual = results[0][2]
    else:
        actual = ". ".join(f"{label}: {'OK' if ok else 'FAILED'} - {msg}" for label, ok, msg in results)

    write_result(test_case_id, actual, status)
    print(f"\n{test_case_id}: {status}")