"""
DMS-TC028
Restore Deleted Doc
1. Go to https://ecmv6.robo2mation.com/dms/restore/
2. Click on "Restore" button
Document should be restored with proper confirmation message
"""
import time
from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC028"


def open_restore_page(driver, wait, name):
    """Open the Restore Documents page (waiting out any post-delete redirect) until `name` is visible."""
    time.sleep(3)
    for _ in range(3):
        driver.get(c.RESTORE_URL)
        time.sleep(3)
        if "restore" not in driver.current_url.lower() or "no category/document type selected" in c.body_text(driver):
            try:
                c.click_label(driver, wait, "Restore Documents")
                time.sleep(3)
            except Exception:
                pass
        if c.wait_text(driver, name, 6):
            return True
    return False


def click_restore_in_row(driver, wait, name):
    """Select the row for `name` in the Restore table and click the #restore_doc button."""
    row = driver.find_element(By.XPATH, f"//table[@id='restore_data']//tbody//tr[contains(., {c.xpath_text(name)})]")

    # 1. Select the row if it isn't already selected
    if "selected" not in (row.get_attribute("class") or ""):
        c.click(driver, row.find_elements(By.TAG_NAME, "td")[0])
        time.sleep(1)

    # 2. Find the actual <a id="restore_doc"> button (not its parent <li>)
    restore_btns = driver.find_elements(By.ID, "restore_doc")
    restore_btn = next((b for b in restore_btns if b.is_displayed()), None)
    if not restore_btn:
        restore_btn = c.find_by_label(driver, "restore")
    if not restore_btn:
        raise Exception("Could not find the Restore button (#restore_doc) on the page")

    # Clicking #restore_doc immediately sends a PATCH request, shows a toast, and reloads after 2s (no confirm modal)
    def action():
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", restore_btn)
        driver.execute_script("arguments[0].click();", restore_btn)

    ok, message = c.message_after(driver, action)
    time.sleep(3)  # Wait out the 2-second auto-reload in restore_data.js
    return ok, message


def restore_deleted(driver, wait):
    info = c.new_document(driver, wait)
    name = info["name"]
    ok, message = c.do(driver, wait, "delete", "yes")
    if not ok:
        raise c.SetupError(f"could not delete the test document ({message})")

    if not open_restore_page(driver, wait, name):
        return False, f"'{name}' not listed on the Restore Documents page"

    ok, message = click_restore_in_row(driver, wait, name)
    if not ok:
        return False, message

    time.sleep(2)
    found = c.search_finds(driver, wait, name, tries=3)
    return found, f"{message}. Document " + ("found in quick search again" if found else "NOT found in quick search after restore")


SCENARIOS = [("Restore deleted", restore_deleted)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
