"""
DMS-TC026
Restore Archived Doc
1. Open a document that is checked-out
2. Click on "Restore Archive"
3. Click on "Yes, Restore"
4. Document should be restored with proper confirmation message
2. Document should be available in xplorer view
3. Document should be available in quick search
4. Document should be available in advanced search (without enabling "include archive"
"""
import time
from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC026"


def open_from_advanced_search(driver, wait, name):
    """Click the Open action icon in the Advanced Search result row for `name` and switch to the new tab."""
    old_tabs = driver.window_handles
    row = driver.find_element(By.XPATH, f"//tr[contains(., {c.xpath_text(name)})]")
    # Look for the 'open in new tab' icon/link in the Actions column (last icon/link in the row)
    action_els = row.find_elements(
        By.XPATH,
        ".//*[contains(@class, 'openInNew') or contains(@title, 'Open') or contains(@data-original-title, 'Open')] | "
        ".//td[last()]//*[self::a or self::button or self::i]"
    )
    action_els = [el for el in action_els if el.is_displayed()]
    if action_els:
        c.click(driver, action_els[-1])  # the rightmost icon in Actions is 'Open in new tab'
    else:
        c.double_click_label(driver, wait, name)

    time.sleep(3)
    c.switch_to_new_tab(driver, old_tabs)


def restore_archived(driver, wait):
    info = c.new_document(driver, wait)
    name = info["name"]
    ok, message = c.do(driver, wait, "archive", "yes")
    if not ok:
        raise c.SetupError(f"could not archive the test document ({message})")
    time.sleep(3)

    # An archived document is only found when "Include Archive" is on
    driver.get(c.EXPLORER_URL)
    c.advanced_search(driver, wait, name, include_archive=True)
    open_from_advanced_search(driver, wait, name)

    label = "restore archive" if c.find_by_label(driver, "restore archive") is not None else "restore"
    ok, message = c.do(driver, wait, label, "yes")
    if not ok:
        return False, message
    time.sleep(3)

    missing = []
    if not c.explorer_has(driver, wait, info["doc_type"], name):
        missing.append("explorer view")
    if not c.search_finds(driver, wait, name, tries=3):
        missing.append("quick search")
    if not c.advanced_finds(driver, wait, name):
        missing.append("advanced search")
    if missing:
        return False, f"{message}. Restored document is not shown in: {', '.join(missing)}"
    return True, f"{message}. Document is available in explorer view, quick search and advanced search"


SCENARIOS = [("Restore archive", restore_archived)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()