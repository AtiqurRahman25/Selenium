"""
DMS-TC130
Document Maker-Checker feature
Document Review by checker
1. Go to https://ecmv6.robo2mation.com/dms/document/pending-for-review/
2. By default, "Requested by others" is selected
3. Check the pending document list with option for approve/reject
4. Check the pending documents by "Select maker" filter
5. Apply "Upload date range" filter and check the document list
Results should show accordingly
"""
import os

import common as c

TEST_CASE_ID = "DMS-TC130"

DOC_TYPE = os.getenv("CHECKER_DOC_TYPE")  # a doc-type with a checker group, the second user is a checker


def checker_list(driver, wait):
    info = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE, require_checker=True)
    name = info["name"]

    def look():
        driver.get(c.REVIEW_URL)  # "Requested by others" is the default
        shown = c.wait_text(driver, name, 10)
        approve = c.find_near(driver, name, "approve") is not None
        reject = c.find_near(driver, name, "reject") is not None
        return shown, approve, reject
    shown, approve, reject = c.as_other_user(driver, wait, look)
    ok = shown and approve and reject
    return ok, f"Checker sees the document: {'yes' if shown else 'NO'}, approve option: {'yes' if approve else 'NO'}, reject option: {'yes' if reject else 'NO'}. Maker and upload date filters are not checked by the script"


SCENARIOS = [("Checker pending list", checker_list)]


def main():
    c.need_other_user()
    c.need_env("CHECKER_DOC_TYPE", "(search text of a doc-type that has a checker group, the second user is the checker)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
