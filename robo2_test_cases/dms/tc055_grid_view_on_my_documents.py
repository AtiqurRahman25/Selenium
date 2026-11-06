"""
DMS-TC055
Grid View on My Documents
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Click on "grid" icon
3. Click on "document" icon
4. Click on "view" icon
1. Document list should be shown in grid view
2. Document should be opened in new tab
3. Document quick view modal should be opened
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import explorer_helper as e

TEST_CASE_ID = "DMS-TC055"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (or just the name)


def grid_view(driver, wait):
    e.open_doc_type(driver, wait, DOC_TYPE)

    # 1. grid icon -> documents shown as cards (div.file-thumb), not as the list table
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "grid_view"))))
    time.sleep(2)
    cards = c.visible(driver, "div.file-thumb a.ci-avatar")
    if not cards or c.visible(driver, e.LIST):
        return False, "documents are not shown in grid view after clicking the grid icon"

    # 2. document icon -> opens in a new tab
    main_tab = driver.current_window_handle
    old_tabs = driver.window_handles
    c.click(driver, cards[0])
    time.sleep(3)
    opened_tab = len(driver.window_handles) > len(old_tabs)
    if opened_tab:
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()
    driver.switch_to.window(main_tab)

    # 3. view (preview) icon -> quick view modal
    preview = c.visible(driver, "div.file-thumb a.quick_view")
    if not preview:
        return False, "Grid view shown, but the view (preview) icon was not found"
    c.click(driver, preview[0])
    time.sleep(2)
    quick_view = bool(c.visible(driver, ".modal.in, .modal.show"))

    ok = opened_tab and quick_view
    return ok, f"Grid view shown. Document opened in new tab: {'yes' if opened_tab else 'NO'}. Quick view modal opened: {'yes' if quick_view else 'NO'}"


SCENARIOS = [("Grid view", grid_view)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()