"""
DMS-TC076
Deleted Category Restore
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category/doc-type
3. Click on "Restore Now"
4. Click on "Yes" on confirmation modal
Selected category/doc-type should be restored
"""
import time

from selenium.webdriver.common.by import By

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC076"


def restore_category(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)

    # find the row of OUR item, not the first "Restore Now" on the page
    row = wait.until(lambda dr: next(iter(dr.find_elements(
        By.XPATH, f"//tr[contains(@class,'clickie')][td[1][normalize-space()='{name}']]")), None))

    def action():
        row.find_element(By.CSS_SELECTOR, "td.restore").click()
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    ok, message = c.message_after(driver, action)
    if not ok:
        return False, message

    # restored doc-types show as "NAME (0)", categories as "NAME"
    driver.get(c.ROOT_URL)
    q = c.xpath_text(name)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]/td[1]"
          f"[normalize-space(.)={q} or starts-with(normalize-space(.), concat({q}, ' ('))]")
    try:
        wait.until(lambda dr: [e for e in dr.find_elements(By.XPATH, xp) if e.is_displayed()])
        back = True
    except Exception:
        back = False
    return back, f"{message}. '{name}' " + ("is back in Categorization" if back else "is NOT back in Categorization")


SCENARIOS = [("Restore category", restore_category)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()