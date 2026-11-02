"""
DMS-TC003	
Document View in Pending Documents (Grid View)	
"1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Click on ""Grid View"" icon
3. Click on ""view document"" icon (PDF, PNG, JPG, JPEG, SVG, GIF, MP3, MP4, DOC, DOCX, XLS, XLSX, CSV, PPT, PPTX, MSG, EML, TXT file)"	
System should allow to view the document and if give user a message if preview not available
"""
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC003"
PENDING_URL = c.BASE_URL + "/dms/document/upload/standard_upload/filesave/pendingmetalist/"

# ---------- locators (adjust if the page differs) ----------
LOWER = "translate({0}, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
GRID_VIEW = (By.XPATH, "//*[contains(@title,'Grid') or contains(@data-original-title,'Grid') or contains(@aria-label,'Grid')]")
VIEW_ICON = ("[contains(" + LOWER.format("@title") + ", 'view document') or contains(" + LOWER.format("@data-original-title")
             + ", 'view document') or contains(" + LOWER.format("@aria-label") + ", 'view document')]")
POPUP = ".modal.show, .modal.in, [role='dialog'], .swal2-popup, .ant-modal, .mat-dialog-container, iframe, embed, video, audio"


def find_view_icon(driver, ext):
    """Find the file name ending with .<ext>, then the view icon inside the same card."""
    name = driver.find_element(By.XPATH, f"//*[contains({LOWER.format('normalize-space(text())')}, '.{ext}')]")
    card = name.find_element(By.XPATH, f"ancestor::*[.//*{VIEW_ICON}][1]")
    return card.find_element(By.XPATH, f".//*{VIEW_ICON}")


def preview_result(driver, old_tabs):
    """What happened after clicking the view icon? Returns text, or None if nothing happened."""
    if len(driver.window_handles) > len(old_tabs):
        return "preview opened in new tab"
    if any(e.is_displayed() for e in driver.find_elements(By.CSS_SELECTOR, POPUP)):
        return "preview opened"
    text = driver.find_element(By.TAG_NAME, "body").text.lower()
    if "preview" in text and any(w in text for w in ("not available", "unavailable", "not supported")):
        return "'preview not available' message shown"
    return None


def view_document(driver, wait, ext):
    """Returns (True/False, message)."""
    driver.get(PENDING_URL)
    try:
        wait.until(EC.element_to_be_clickable(GRID_VIEW)).click()
        time.sleep(1)  # let the grid load
    except Exception:
        return False, "Grid View icon not found"

    try:
        icon = find_view_icon(driver, ext)
    except Exception:
        return False, f"no .{ext} document in pending list"

    old_tabs = driver.window_handles
    try:
        icon.click()
        result = WebDriverWait(driver, 8).until(lambda d: preview_result(d, old_tabs))
    except Exception:
        c.save_shot(driver, TEST_CASE_ID, ext, "FAIL")
        with open(f"debug/{TEST_CASE_ID}_{ext}.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("   page:", driver.current_url)
        return False, "nothing happened after clicking view icon"

    c.save_shot(driver, TEST_CASE_ID, ext, "PASS")

    # close the preview before the next file type
    if len(driver.window_handles) > len(old_tabs):
        driver.close()
        driver.switch_to.window(old_tabs[0])
    else:
        driver.switch_to.active_element.send_keys(Keys.ESCAPE)
    return True, result


def main():
    c.check_excel_ready(TEST_CASE_ID)

    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    passed, failed = [], []

    try:
        c.login(driver, wait)
        for ext in c.EXTENSIONS:
            ok, msg = view_document(driver, wait, ext)
            print(f"{ext:5} -> {'PASS' if ok else 'FAIL'} ({msg})")
            (passed if ok else failed).append(ext if ok else f"{ext} ({msg})")
    finally:
        driver.quit()

    total = len(c.EXTENSIONS)
    if failed:
        status = "Fail"
        actual = f"Viewed {len(passed)}/{total} file types. Could not view: " + ", ".join(failed)
    else:
        status = "Pass"
        actual = f"All {total} file types opened in preview, or showed a preview not available message"

    c.write_result(TEST_CASE_ID, actual, status)
    print(f"\n{TEST_CASE_ID}: {status}")


if __name__ == "__main__":
    main()