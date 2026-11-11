"""
DMS-TC122
Advanced Search (Disable Match All)
1. Click on global search arrow icon
2. Select doc type
3. Give metadata
4. Disable "Match All"
5. Click on "Search"
System should show all documents which matched any meta field data. Maximum matched data should show first
"""
import time

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC122"
MAX_PAGES = 50


def result_rows_text(driver):
    # read with JavaScript in one go: the table is redrawn on every page change, so Selenium row elements go stale
    return (driver.execute_script(
        "return Array.from(document.querySelectorAll('#search_modal tbody tr')).map(r => r.innerText).join('\\n');"
    ) or "").lower()


def find_in_result_pages(driver, names):
    """Walk the search result pages (10 rows each). Returns {name: page number where it was found}."""
    found = {}
    page = 1
    for _ in range(MAX_PAGES * 2):
        text = result_rows_text(driver)
        for name in names:
            if name not in found and name.lower() in text:
                found[name] = page
        if len(found) == len(names) or page >= MAX_PAGES:
            break
        try:
            next_links = driver.find_elements(By.CSS_SELECTOR, "#search_pagination li.next:not(.disabled) a")
            if not next_links or not next_links[0].is_displayed():
                break
            c.click(driver, next_links[0])
        except StaleElementReferenceException:
            time.sleep(1)  # pagination was redrawn - read this page again and retry
            continue
        try:
            WebDriverWait(driver, 15).until(lambda d: result_rows_text(d) and result_rows_text(d) != text)
        except TimeoutException:
            break
        page += 1
        time.sleep(0.5)
    return found


def advanced(driver, wait):
    first = c.upload_document(driver, wait, "pdf")
    second = c.upload_document(driver, wait, "pdf")
    if len(first["values"]) >= 2 and len(second["values"]) >= 2:
        # field 1 has the value of the first document, field 2 has the value of the second one
        pairs = [(first["values"][0][0], first["values"][0][1]), (second["values"][1][0], second["values"][1][1])]
        name = None
    elif first["values"] and second["values"]:
        pairs = [(second["values"][0][0], second["values"][0][1])]
        name = first["name"]  # document name of the first + meta-data of the second
    else:
        raise c.SetupError("the doc-type has no text meta-data to search with")

    driver.get(c.EXPLORER_URL)
    c.advanced_search(driver, wait, name, match_all=False, doc_type=first["doc_type"], extra=pairs)
    # with Match All off the result list is paged and the matching documents are not always on page 1
    found = find_in_result_pages(driver, [first["name"], second["name"]])
    found_a = first["name"] in found
    found_b = second["name"] in found

    def where(doc):
        return f"shown (page {found[doc]})" if doc in found else "not shown"

    ok = found_a and found_b
    return ok, f"Match All off: first document {where(first['name'])}, second document {where(second['name'])} (expected both documents)"


SCENARIOS = [("Match All disabled", advanced)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
