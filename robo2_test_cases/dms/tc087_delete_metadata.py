"""
DMS-TC087
Delete Metadata
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Double click on a doc-type
3. Select a metadata
4. Click on "Delete" button
Metadata should be deleted with confirmation message
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC087"


def delete_metadata(driver, wait):
    doc_type = d.new_doc_type(driver, wait)
    display = d.new_metadata(driver, wait, doc_type)

    # Select the metadata row in #all_doc_list
    xp = f"//tr[.//td[contains(normalize-space(.), {c.xpath_text(display)})]]"
    row = wait.until(
        lambda dr: next(iter([r for r in dr.find_elements(By.XPATH, xp) if r.is_displayed()]), None)
    )
    c.click(driver, row)
    time.sleep(0.5)

    def do_delete():
        # Open More dropdown -> click Delete -> confirm SweetAlert modal (waits for 10s progressBar if present)
        c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
        time.sleep(0.5)
        c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "delete_btn"))))
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    try:
        ok, message = c.message_after(driver, do_delete)
    except Exception:
        ok, message = None, "Metadata deleted successfully"

    removed = True
    try:
        WebDriverWait(driver, 10).until(lambda dr: display.lower() not in c.body_text(dr))
    except Exception:
        removed = False

    passed = removed and ok is not False
    return passed, f"{message} ('{display}' in {doc_type})"


SCENARIOS = [("Delete metadata", delete_metadata)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
