"""
DMS-TC077
Deleted Category Permanent Deletion
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category/doc-type
3. Click on "Delete Permanently"
4. Click on "Yes" on confirmation modal
Selected category/doc-type should be permanently deleted
"""
import time

from selenium.webdriver.common.by import By

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC077"


def find_row(driver, name):
    return next(iter(driver.find_elements(
        By.XPATH, f"//tr[contains(@class,'clickie')][td[1][normalize-space()='{name}']]")), None)


def delete_permanently(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)

    # click Delete Permanently in OUR row, not the first one on the page
    row = wait.until(lambda dr: find_row(dr, name))

    def action():
        row.find_element(By.CSS_SELECTOR, "td.delete").click()
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    ok, message = c.message_after(driver, action)
    if not ok:
        return False, message

    # reload, wait for the list to load, then check our row is gone
    driver.get(c.DELETED_ROOT_URL)
    wait.until(lambda dr: dr.find_elements(By.CSS_SELECTOR, "tr.clickie"))
    still_there = find_row(driver, name) is not None
    return (not still_there), f"{message}. '{name}' " + (
        "is STILL in the deleted list" if still_there else "is gone from the deleted list")


SCENARIOS = [("Delete permanently", delete_permanently)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()