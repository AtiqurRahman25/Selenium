"""
DMS-TC069
Update Category/Doc Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a category/doc-type
3. Update category/doc-type name with unique value
4. Click on "Save" button
Category/doc-type should be updated with confirmation message
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c

TEST_CASE_ID = "DMS-TC069"

CATEGORY = os.getenv("CATEGORY_TO_UPDATE")  # name of an existing top-level category
ROWS = "#all_doc_list tbody tr.clickie"
MODAL = "update_parent_new_cat_doc"  # Update dialog for a top-level category / doc-type


def rename(driver, wait, old, new):
    """Select the row, More -> Update, type the new name, click Update. Returns (True/False, message)."""
    driver.get(c.ROOT_URL)
    wait.until(lambda drv: drv.find_elements(By.CSS_SELECTOR, ROWS))
    time.sleep(1)
    rows = driver.find_elements(By.CSS_SELECTOR, ROWS)
    match = [r for r in rows if r.find_element(By.TAG_NAME, "td").text.strip() == old]
    if not match:
        names = [r.find_element(By.TAG_NAME, "td").text.strip() for r in rows][:15]
        raise c.SetupError(f"'{old}' not found in the first list. Items there: {names}")
    c.click(driver, match[0].find_element(By.TAG_NAME, "td"))
    time.sleep(1)

    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "update_btn"))))
    modal = wait.until(EC.visibility_of_element_located((By.ID, MODAL)))
    time.sleep(1)

    box = modal.find_element(By.CSS_SELECTOR, "input[name='name']")
    shown = (box.get_attribute("value") or "").strip()
    if shown != old:
        return False, f"the Update dialog shows '{shown}', not '{old}' (the wrong row may be selected)"
    box.clear()
    box.send_keys(new)
    button = modal.find_element(By.CSS_SELECTOR, "button[type='submit']")
    return c.message_after(driver, lambda: c.click(driver, button))


def update_category(driver, wait):
    new = CATEGORY + "_UPD"
    if len(new) > 50:
        raise c.SetupError(f"'{new}' is longer than 50 characters, use a shorter category name")
    ok, message = rename(driver, wait, CATEGORY, new)
    if not ok:
        return False, message

    # put the original name back
    try:
        restored, note = rename(driver, wait, new, CATEGORY)
    except Exception as error:
        restored, note = False, str(error)
    back = "restored" if restored else f"NOT restored ({note}), rename '{new}' back to '{CATEGORY}' by hand"
    return True, f"{message} ({CATEGORY} -> {new}). Original name {back}"


SCENARIOS = [("Update category", update_category)]


def main():
    c.need_env("CATEGORY_TO_UPDATE", "(name of an existing top-level category)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()