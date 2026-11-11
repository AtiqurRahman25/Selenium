"""
DMS-TC131
Document Maker-Checker feature
Document approve/reject
For all the pending documents, 
1. Approve the document and observe the results
2. Reject the documents and observe the results
Results should show accordingly
"""
import os

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC131"

DOC_TYPE = os.getenv("CHECKER_DOC_TYPE")  # a doc-type with a checker group, the second user is a checker


def approve_reject(driver, wait):
    approved = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE, require_checker=True)["name"]
    rejected = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE, require_checker=True)["name"]

    ok_a, msg_a = d.review_as_checker(driver, wait, approved, "approve")
    ok_r, msg_r = d.review_as_checker(driver, wait, rejected, "reject")
    approved_found = c.search_finds(driver, wait, approved, tries=5)
    rejected_found = c.search_finds(driver, wait, rejected)
    ok = ok_a and ok_r and approved_found and not rejected_found
    return ok, (f"Approve: {msg_a}. Reject: {msg_r}. Approved document found in search: {'yes' if approved_found else 'NO'}. "
                f"Rejected document found in search: {'YES' if rejected_found else 'no'}")


SCENARIOS = [("Approve and reject", approve_reject)]


def main():
    c.need_other_user()
    c.need_env("CHECKER_DOC_TYPE", "(search text of a doc-type that has a checker group, the second user is the checker)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
