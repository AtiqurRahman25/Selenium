"""
DMS-TC011	Multiple Doc Upload Together (Document Merge)	
"1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Attach 2 or more documents (image, or pdf) of similar type together
3. Click on ""Save"" button
Only PDF documents should be marged
"""
import os
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC011"
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")


def pick_files(extensions, count):
    """Return `count` file paths, of the same type if possible. Empty list if there are not enough."""
    names = os.listdir(c.SAMPLE_DIR)
    for ext in extensions:
        same = [n for n in names if n.lower().endswith("." + ext)]
        if len(same) >= count:
            return [os.path.abspath(os.path.join(c.SAMPLE_DIR, n)) for n in same[:count]]
    mixed = [n for n in names if n.lower().endswith(tuple("." + e for e in extensions))]
    return [os.path.abspath(os.path.join(c.SAMPLE_DIR, n)) for n in mixed[:count]] if len(mixed) >= count else []


def attach_files(driver, wait, paths):
    """Attach the files one by one. They land in the Pending Files list."""
    for path in paths:
        driver.get(h.ATTACH_URL)
        wait.until(EC.presence_of_element_located(FILE_INPUT)).send_keys(path)
        time.sleep(3)


def select_files(driver, wait, paths):
    """Open the pending list, remove old selections, click the paperclip of every file."""
    driver.get(h.PENDING_URL)
    wait.until(EC.presence_of_element_located((By.ID, "list_view_container")))
    h.clear_selected_files(driver)
    for path in paths:
        icon = wait.until(EC.presence_of_element_located(h.pending_row_icon(os.path.basename(path))))
        driver.execute_script("arguments[0].click();", icon)
        time.sleep(1)


def merge_pdfs(driver, wait):
    """Scenario 1. Returns (True/False, message)."""
    paths = pick_files(["pdf"], 2)
    if not paths:
        return False, "need 2 PDF files in test_files"
    names = " + ".join(os.path.basename(p) for p in paths)

    attach_files(driver, wait, paths)
    select_files(driver, wait, paths)
    if h.selected_count(driver) < 2:
        return h.fail(driver, TEST_CASE_ID, "pdf_merge", f"only {h.selected_count(driver)} of 2 PDFs could be selected together")

    try:
        h.fill_metadata_form(driver, wait)
    except Exception as error:
        return h.fail(driver, TEST_CASE_ID, "pdf_merge", f"could not fill meta-data ({h.short(error)})")

    text_before = h.body_text(driver)
    try:
        driver.find_element(*h.UPLOAD_BTN).click()
        ok, message = h.wait_for_message(driver, text_before)
    except Exception:
        return h.fail(driver, TEST_CASE_ID, "pdf_merge", "no confirmation message after Upload")

    c.save_shot(driver, TEST_CASE_ID, "pdf_merge", "PASS" if ok else "FAIL")
    return ok, f"{names} uploaded together: {' '.join(message.split())}"


def images_not_merged(driver, wait):
    """Scenario 2: two images must not be selectable together. Returns (True/False, message)."""
    paths = pick_files(["png", "jpg", "jpeg"], 2)
    if not paths:
        return False, "need 2 image files (png, jpg or jpeg) in test_files"

    attach_files(driver, wait, paths)
    select_files(driver, wait, paths)
    count = h.selected_count(driver)
    said = " ".join(h.popup_text(driver).split())
    ok = count < 2  # the page must not accept both images together
    c.save_shot(driver, TEST_CASE_ID, "image_no_merge", "PASS" if ok else "FAIL")
    h.clear_selected_files(driver)

    if ok:
        return True, f"only {count} image accepted. Page said: {said or 'nothing'}"
    return False, "both images were accepted together, so they could be merged"


def main():
    c.check_excel_ready(TEST_CASE_ID)

    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
    results = []

    try:
        c.login(driver, wait)
        for label, scenario in [("PDFs together", merge_pdfs), ("Images together", images_not_merged)]:
            try:
                ok, msg = scenario(driver, wait)
            except Exception as error:
                ok, msg = h.fail(driver, TEST_CASE_ID, label.split()[0].lower(), h.short(error))
            print(f"{label:16} -> {'PASS' if ok else 'FAIL'} ({msg})")
            results.append((label, ok, msg))
    finally:
        driver.quit()

    status = "Pass" if all(ok for _, ok, _ in results) else "Fail"
    actual = ". ".join(f"{label}: {'OK' if ok else 'FAILED'} - {msg}" for label, ok, msg in results)

    c.write_result(TEST_CASE_ID, actual, status)
    print(f"\n{TEST_CASE_ID}: {status}")


if __name__ == "__main__":
    main()