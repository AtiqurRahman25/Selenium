"""
DMS-TC125
Save Search
1. Click on global search arrow icon
2. Select doc type
3. Give metadata
4. Click on "Save Search"
5. Give a search name & click on "Save"
An advanced search result should be saved
"""
from datetime import datetime

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC125"

def saving(driver, wait):
    info = c.upload_document(driver, wait)
    search_name = datetime.now().strftime("AUTO_SEARCH_%H%M%S")
    ok, message = d.save_search(driver, wait, search_name, info)
    return ok, f"{message} ({search_name})"


SCENARIOS = [("Save search", saving)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()