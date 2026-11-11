"""
DMS-TC128
Document Maker-Checker feature
Pending For Review
1. Go to https://ecmv6.robo2mation.com/dms/document/pending-for-review/
2. Select "Requested By Me" filter
3. Filter "Pending", "Approved" & "Rejected" files and check by checker filter
4. Apply approve date range and review date range filter and check document results
5. Search by doctype and check the "Pending", "Approved" & "Rejected" documents
Results should show accordingly

Roles: maker = second user (OTHER_USERNAME), checker = main user (USERNAME, 'sharar'), same as TC127.
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC128"

DOC_TYPE = os.getenv("CHECKER_DOC_TYPE")  # a doc-type with a checker group, the main user is the checker


def choose(driver, wait, select_id, text):
    """Pick an option in a bootstrap-select drop-down: open it first, then click the option."""
    c.click(driver, wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, f"button[data-id='{select_id}']"))))
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//button[@data-id='{select_id}']/following-sibling::div//span[@class='text'][normalize-space()='{text}']")))
    c.click(driver, option)


def listed(driver, wait, status, name):
    """Pending For Review > Requested By Me > status filter. True if the document is listed."""
    driver.get(c.REVIEW_URL)
    choose(driver, wait, "select-user", "Requested By Me")
    time.sleep(2)
    choose(driver, wait, "select-status", status)
    time.sleep(3)
    return name.lower() in c.body_text(driver)


def statuses(driver, wait, name):
    """Is the document shown under Pending / Approved / Rejected?"""
    return [listed(driver, wait, status, name) for status in ("Pending", "Approved", "Rejected")]


def requested_by_me(driver, wait):
    # maker (second user) uploads the document and looks at "Requested By Me"
    def maker_uploads():
        info = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE, require_checker=True)
        return info, statuses(driver, wait, info["name"])

    info, before = c.as_other_user(driver, wait, maker_uploads)
    name = info["name"]
    if before != [True, False, False]:
        return False, f"Before review: shown in Pending/Approved/Rejected = {before} (expected [True, False, False])"

    # checker (main user, logged in again by as_other_user) approves the document
    ok, message = d.review_document(driver, wait, name, "approve")
    if not ok:
        raise c.SetupError(f"checker could not approve the document ({message})")

    # maker looks at "Requested By Me" again
    after = c.as_other_user(driver, wait, lambda: statuses(driver, wait, name))
    ok = after == [False, True, False]
    return ok, f"Pending / Approved / Rejected before review {before}, after approval {after}. Date range and checker filters are not checked by the script"


SCENARIOS = [("Requested by me filters", requested_by_me)]


def main():
    c.need_other_user()
    c.need_env("CHECKER_DOC_TYPE", "(search text of a doc-type that has a checker group, the main user is the checker)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()