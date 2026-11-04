"""
DMS-TC025
Archive Doc
1. Open a document 
2. Click on "Archive"
3. Click on "Yes, Archive"
1. Document should be archived with proper confirmation message
2. Document should be removed from explorer view
3. Document should be removed from quick search
4. Document should be removed from advanced search (without enabling "include archive"
"""
import time

import common as c

TEST_CASE_ID = "DMS-TC025"

def archive(driver, wait):
    info = c.new_document(driver, wait)
    name = info["name"]
    ok, message = c.do(driver, wait, "archive", "yes")
    if not ok:
        return False, message
    time.sleep(3)

    still_shown = []
    if c.explorer_has(driver, wait, info["doc_type"], name):
        still_shown.append("explorer view")
    if c.search_finds(driver, wait, name):
        still_shown.append("quick search")
    if c.advanced_finds(driver, wait, name):
        still_shown.append("advanced search")
    if still_shown:
        return False, f"{message}. Archived document is still shown in: {', '.join(still_shown)}"
    return True, f"{message}. Document removed from explorer view, quick search and advanced search"


SCENARIOS = [("Archive", archive)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
