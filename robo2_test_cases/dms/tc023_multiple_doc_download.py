"""
DMS-TC023
Multiple Doc Download Together
1. Go to advanced search
2. Select a doc type
3. Click on search
4. Select one, multiple or all documents
5. Click on "Download" icon
1. An URL should be generated in "Requested Download"
2. All selected documents should be downloaded as zip file when click on "Download" button
"""
import os
import time

from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC023"
SKIP_BOXES = ("include_archive", "match_all", "select_all_search_result")


def result_boxes(driver):
    """Check boxes of the search result (the open popup first, then the whole page)."""
    for scope in (c.MODAL, ""):
        boxes = driver.find_elements(By.XPATH, f"{scope}//input[@type='checkbox']")
        boxes = [
            b for b in boxes
            if b.get_attribute("id") not in SKIP_BOXES
            and "select_all" not in (b.get_attribute("class") or "")
        ]
        if boxes:
            return boxes
    return []


def tick(driver, box):
    """Tick a check box. The real input can be hidden behind a styled label, so click the label then."""
    if box.is_displayed():
        c.click(driver, box)
        return
    box_id = box.get_attribute("id")
    labels = driver.find_elements(By.CSS_SELECTOR, f"label[for='{box_id}']") if box_id else []
    labels = [lb for lb in labels if lb.is_displayed()]
    if labels:
        c.click(driver, labels[0])
    else:
        driver.execute_script("arguments[0].click();", box)


def multiple_download(driver, wait):
    c.upload_document(driver, wait, "pdf")
    first = c.upload_document(driver, wait, "txt")  # two fresh documents, so the doc type has at least two
    driver.get(c.EXPLORER_URL)
    c.advanced_search(driver, wait, "", doc_type=first["doc_type"])  # doc type only, like the test case

    if "no search result found" in c.body_text(driver):
        return False, f"advanced search found no document for doc type '{first['doc_type']}'"
    boxes = result_boxes(driver)
    if len(boxes) < 2:
        return False, f"document check boxes not found in the search result (found {len(boxes)})"
    for box in boxes[:2]:
        tick(driver, box)

    c.click_label(driver, wait, "download")
    if not c.wait_text(driver, "requested download", 15):
        return False, "no 'Requested Download' URL was generated"

    time.sleep(3)
    driver.get(c.REQUESTED_DOWNLOAD_URL)
    before = set(os.listdir(c.DOWNLOAD_DIR))
    c.click_label(driver, wait, "download")
    file_name = c.wait_for_download(before)
    if file_name and file_name.lower().endswith(".zip"):
        return True, f"Download URL generated in Requested Download, zip file downloaded: {file_name}"
    return False, f"zip file was not downloaded (got: {file_name})"


SCENARIOS = [("Multiple download", multiple_download)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
