"""
DMS-TC107
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Search by "method name" & "master table"
Only searched fetch method should be shown
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC107"


def search_method(driver, wait):
    name = d.new_method(driver, wait)
    d.new_method(driver, wait)  # a second method, so the search has something to leave out

    driver.get(c.MASTER_TABLE_URL)
    WebDriverWait(driver, 15).until(
        lambda drv: bool(c.visible(drv, ".mtm-list-card, .MTM-empty-card"))
    )
    time.sleep(1)

    # Specifically target the Master Table Method search input (not #search_text in the top navbar)
    search_box = wait.until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "input.method_search_input"))
    )
    search_box.click()
    search_box.clear()
    search_box.send_keys(name)
    search_box.send_keys(Keys.ENTER)
    time.sleep(3)

    # Methods are rendered as .mtm-list-card divs, not table rows
    cards = c.visible(driver, ".method-list-card-container .mtm-list-card")
    shown_names = []
    for card in cards:
        spans = card.find_elements(By.CSS_SELECTOR, ".summary-item i[title='Method'] + span")
        shown_names.append(spans[0].text.strip() if spans else card.text.strip())

    wrong = [m for m in shown_names if name.lower() not in m.lower()]
    ok = bool(cards) and not wrong
    return ok, f"Search '{name}' shows {len(cards)} method(s)" + ("" if ok else f", {len(wrong)} do not match")


SCENARIOS = [("Search by method name", search_method)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()