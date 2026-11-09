"""
DMS-TC119
Quick Search
1. Click on global search
2. Search by doc name or any metadata
Only searched result should be shown
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c

TEST_CASE_ID = "DMS-TC119"


def search_for(driver, wait, text, expected, tries=5):
    """Type `text` in the global search box on My Documents. Returns (True/False, number of results shown).
    The search index can be a little late, so the search is repeated until `expected` is listed."""
    count = 0
    for _ in range(tries):
        driver.get(c.EXPLORER_URL)
        box = wait.until(EC.element_to_be_clickable(c.SEARCH_BOX))
        box.clear()
        box.send_keys(text)
        time.sleep(3)
        results = driver.find_element(*c.SEARCH_RESULTS)
        count = len(results.find_elements(By.TAG_NAME, "a"))
        if expected in results.text:
            return True, count
        time.sleep(3)
    return False, count


def quick_search(driver, wait):
    info = c.upload_document(driver, wait)
    name = info["name"]
    found, count = search_for(driver, wait, name, name)
    if not found:
        return False, f"Search by document name '{name}' did not show the document"
    if not info["values"]:
        return True, f"Search by document name shows the document ({count} result(s)). No text meta-data to search with"
    value = info["values"][0][1]
    found_meta, count_meta = search_for(driver, wait, value, name)
    return found_meta, (f"Search by name shows the document ({count} result(s)). Search by meta-data '{value}' "
                        + (f"shows the document ({count_meta} result(s))" if found_meta else "does NOT show the document"))


SCENARIOS = [("Quick search", quick_search)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()