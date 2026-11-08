"""
DMS-TC075
Deleted Category Map
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category
3. Click on "See Map"
Selected categories map will be shown
"""
from datetime import datetime

from selenium.webdriver.common.by import By

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC075"


def see_map(driver, wait):
    # See Map exists only for categories (doc types show up as "Document" with no map)
    name = datetime.now().strftime("AUTO_CAT_%H%M%S")
    ok, message = d.create_category(driver, wait, name, "category")
    if not ok:
        raise c.SetupError(f"category could not be created ({message})")

    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the category ({message})")

    driver.get(c.DELETED_ROOT_URL)

    # find the row of OUR category, not the first "See Map" on the page
    row = wait.until(lambda dr: next(iter(dr.find_elements(
        By.XPATH,
        f"//tr[@data-type='cat'][td[1][normalize-space()='{name}']]")), None))
    row.find_element(By.CSS_SELECTOR, "td.map").click()

    # wait for the "Categorization Map" modal and read its tree nodes
    shown = wait.until(lambda dr: [
        a.text.strip()
        for a in dr.find_elements(By.CSS_SELECTOR, "#see_map.in .jstree-anchor")
        if a.is_displayed()])

    if name in shown:
        return True, f"Map of '{name}' is shown"
    return False, f"map opened but showed {shown}, expected '{name}'"


SCENARIOS = [("See map", see_map)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()