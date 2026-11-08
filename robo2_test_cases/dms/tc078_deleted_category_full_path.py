"""
DMS-TC078
Deleted Category Full Path
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
Categories/Doc-type full path should be shown
"""
from selenium.webdriver.common.by import By

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC078"


def full_path(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)

    # the list is loaded by JavaScript, so wait for OUR row
    row = wait.until(lambda dr: next(iter(dr.find_elements(
        By.XPATH, f"//tr[contains(@class,'clickie')][td[1][normalize-space()='{name}']]")), None))

    path = row.find_elements(By.TAG_NAME, "td")[-1].text.strip()   # last column = Full Path
    expected = f"/{name}/"
    if path == expected:
        return True, f"Full path of the deleted doc-type is shown as '{path}'"
    return False, f"Full path column shows '{path}', expected '{expected}'"


SCENARIOS = [("Full path", full_path)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()