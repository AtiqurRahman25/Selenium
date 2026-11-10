"""
DMS-TC127
Document Maker-Checker feature
Document Review (Upload Document for review- Maker)
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/
2. Select a checker group assigned document type
3. Select checker and fill the necessary fields
4. Upload Document
Document should be uploaded and should go to the checker.
If checker approves the document only then it should appear on the system search and in My Documents

Roles: maker = second user (OTHER_USERNAME), checker = main user (USERNAME, 'sharar').
"""
import os

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC127"

DOC_TYPE = os.getenv("CHECKER_DOC_TYPE")  # a doc-type with a checker group, the main user is a checker


def maker_checker(driver, wait):
    # maker (second user) uploads the document and checks it is hidden from search before approval
    def maker_uploads():
        info = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE, require_checker=True)
        hidden = not c.search_finds(driver, wait, info["name"], tries=2)
        return info, hidden

    info, hidden_before = c.as_other_user(driver, wait, maker_uploads)
    name = info["name"]

    # checker (main user, logged in again by as_other_user) approves the document
    ok, message = d.review_document(driver, wait, name, "approve")
    if not ok:
        return False, (f"Checker could not approve the document ({message}). Doc type used: '{info['doc_type']}'. "
                       f"Document hidden from search before approval: {'yes' if hidden_before else 'NO (it did not go to review)'}")

    found_after = c.search_finds(driver, wait, name, tries=5)
    ok = hidden_before and found_after
    return ok, (f"Before approval the document is hidden in search: {'yes' if hidden_before else 'NO'}. "
                f"Checker approved it ({message}). After approval it is found in search: {'yes' if found_after else 'NO'}")


SCENARIOS = [("Maker uploads, checker approves", maker_checker)]


def main():
    c.need_other_user()
    c.need_env("CHECKER_DOC_TYPE", "(search text of a doc-type that has a checker group, the main user is the checker)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()