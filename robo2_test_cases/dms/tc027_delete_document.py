"""
DMS-TC027
Delete Document
1. Open a document
2. Click on "Delete"
3. Click on "Yes, Delete"
Document should be deleted
"""
import time

import common as c

TEST_CASE_ID = "DMS-TC027"

def delete_document(driver, wait):
    info = c.new_document(driver, wait)
    ok, message = c.do(driver, wait, "delete", "yes")
    if not ok:
        return False, message
    time.sleep(3)
    if c.search_finds(driver, wait, info["name"]):
        return False, f"{message}. Deleted document is still found in quick search"
    return True, f"{message}. Document is not found in quick search any more"


SCENARIOS = [("Delete document", delete_document)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
