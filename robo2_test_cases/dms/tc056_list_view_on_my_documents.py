"""
DMS-TC056
List View on My Documents
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Click on "list" icon
3. Click on "document" icon
4. Click on "view" icon
1. Document list should be shown in list view
2. Document "title" & "publisher name" should be shown
2. Document should be opened in new tab
3. Document quick view modal should be opened
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import explorer_helper as e

TEST_CASE_ID = "DMS-TC056"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (or just the name)


def list_view(driver, wait):
    e.open_doc_type(driver, wait, DOC_TYPE)

    # 1. switch to grid first, then click the list icon, so the click really changes the view
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "grid_view"))))
    time.sleep(2)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "list_view"))))
    time.sleep(2)
    if not c.visible(driver, e.LIST) or c.visible(driver, "div.file-thumb"):
        return False, "documents are not shown in list view after clicking the list icon"

    # 2. "title" = Document Name column, "publisher name" = Uploaded By column
    headers = [th.text.strip().lower() for th in driver.find_elements(By.CSS_SELECTOR, e.LIST + " thead th")]
    missing = [name for name in ("document name", "uploaded by") if name not in headers]
    if missing:
        return False, f"list view does not show the columns {missing} (found: {headers})"
    if not e.page_rows(driver):
        return False, "the list view shows no document rows"

    # 3. document icon -> opens in a new tab
    main_tab = driver.current_window_handle
    old_tabs = driver.window_handles
    c.click(driver, driver.find_elements(By.CSS_SELECTOR, e.LIST + " a.ci-avatar")[0])
    time.sleep(3)
    opened_tab = len(driver.window_handles) > len(old_tabs)
    if opened_tab:
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()
    driver.switch_to.window(main_tab)

    # 4. view (preview) icon -> quick view modal
    preview = driver.find_elements(By.CSS_SELECTOR, e.LIST + " a.quick_view")
    if not preview:
        return False, "List view shown, but the view (preview) icon was not found"
    c.click(driver, preview[0])
    time.sleep(2)
    quick_view = bool(c.visible(driver, ".modal.in, .modal.show"))

    ok = opened_tab and quick_view
    return ok, f"List view shows Document Name and Uploaded By. Document opened in new tab: {'yes' if opened_tab else 'NO'}. Quick view modal opened: {'yes' if quick_view else 'NO'}"


SCENARIOS = [("List view", list_view)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()