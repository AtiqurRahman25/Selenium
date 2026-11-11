"""
DMS-TC011
Multiple Doc Upload Together (Document Merge)
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Attach 2 or more documents (image, or pdf) of similar type together
3. Click on "Save" button
Only PDF documents should be merged
"""
import os
import time
from datetime import datetime

from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC011"


def pick_files(extensions, count):
    """Return `count` file paths of the given extensions from SAMPLE_DIR."""
    names = os.listdir(c.SAMPLE_DIR)
    for ext in extensions:
        same = [n for n in names if n.lower().endswith("." + ext)]
        if len(same) >= count:
            return [os.path.abspath(os.path.join(c.SAMPLE_DIR, n)) for n in same[:count]]
    mixed = [n for n in names if n.lower().endswith(tuple("." + e for e in extensions))]
    return [os.path.abspath(os.path.join(c.SAMPLE_DIR, n)) for n in mixed[:count]] if len(mixed) >= count else []


def attach_and_get_pending_names(driver, wait, paths):
    """Attach unique copies of `paths` and return their names in the Pending Files list."""
    pending_names = []
    for path in paths:
        _, copy_path = c.unique_copy(path)
        name = c.attach_new_file(driver, wait, copy_path) or c.attach_new_file(driver, wait, path)
        if not name:
            raise c.SetupError(f"could not attach '{os.path.basename(path)}' to Pending Files")
        pending_names.append(name)
    return pending_names


def select_pending_files(driver, wait, pending_names):
    """Open Pending Documents, clear prior selections, and click the paperclip icon for each file."""
    c.open_pending_list(driver, wait)
    c.clear_selected_files(driver)
    for idx, name in enumerate(pending_names):
        if idx > 0:
            c.open_pending_list(driver, wait)
        c.click_pending_icon(driver, name)
        time.sleep(1)


def merge_pdfs(driver, wait):
    """Scenario 1: Attach and select 2 PDFs together, fill metadata, and upload."""
    paths = pick_files(["pdf"], 2)
    if not paths:
        return False, "need 2 PDF files in test_files"

    pending_names = attach_and_get_pending_names(driver, wait, paths)
    select_pending_files(driver, wait, pending_names)
    if c.selected_count(driver) < 2:
        return False, f"only {c.selected_count(driver)} of 2 PDFs could be selected together"

    c.fill_metadata_form(driver, wait)
    time.sleep(1.5)
    checker_divs = driver.find_elements(By.ID, "checker-div")
    if checker_divs and checker_divs[0].is_displayed():
        c.select_checker(driver)
    c.set_document_name(driver, datetime.now().strftime("AUTO_MERGE_%H%M%S"))

    ok, message = c.message_after(driver, lambda: c.click(driver, driver.find_element(*c.UPLOAD_BTN)))
    names = " + ".join(os.path.basename(p) for p in paths)
    return ok, f"{names} uploaded together: {message}"


def images_not_merged(driver, wait):
    """Scenario 2: Two images must not be selectable together."""
    paths = pick_files(["png", "jpg", "jpeg"], 2)
    if not paths:
        return False, "need 2 image files (png, jpg or jpeg) in test_files"

    pending_names = attach_and_get_pending_names(driver, wait, paths)
    select_pending_files(driver, wait, pending_names)
    count = c.selected_count(driver)
    said = " ".join(c.popup_text(driver).split())
    ok = count < 2
    c.clear_selected_files(driver)

    if ok:
        return True, f"only {count} image accepted. Page said: {said or 'nothing'}"
    return False, "both images were accepted together, so they could be merged"


SCENARIOS = [
    ("PDFs together", merge_pdfs),
    ("Images together", images_not_merged),
]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
