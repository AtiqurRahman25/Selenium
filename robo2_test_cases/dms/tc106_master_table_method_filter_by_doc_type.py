"""
DMS-TC106
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Filter fetch method according to the doc-type
Only selected doc-types fetch method should be shown
"""
import os
import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC106"

# Default to "aa" (or "HR") if MASTER_FILTER_DOC_TYPE is not set, as both have methods on this page
DOC_TYPE = os.getenv("MASTER_FILTER_DOC_TYPE", "aa")


def pick_filter_doc_type(driver, wait, term):
    """Open the #doctype_method Select2 filter, type the doc-type, and pick the matching option."""
    box = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, ".MTM-doctype_method span.select2-selection")
    ))
    c.click(driver, box)

    search = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".select2-container--open input.select2-search__field")
    ))
    search.click()
    search.clear()

    typed = term.strip().strip("/").split("/")[-1]
    for letter in typed[:30]:
        search.send_keys(letter)
        time.sleep(0.2)

    option_css = "#select2-doctype_method-results .select2-results__option"
    WebDriverWait(driver, 15).until(lambda drv: bool(c.select2_options(drv, option_css)))
    time.sleep(1.5)

    options = c.select2_options(driver, option_css)
    option = options[c.best_option_index(options, typed)]
    chosen_text = option.text.strip()
    ActionChains(driver).move_to_element(option).click().perform()
    time.sleep(1)
    return chosen_text


def filter_by_doc_type(driver, wait):
    driver.get(c.MASTER_TABLE_URL)
    # Wait until initial method cards finish loading
    WebDriverWait(driver, 15).until(
        lambda drv: bool(c.visible(drv, ".mtm-list-card, .MTM-empty-card"))
    )
    time.sleep(1)

    chosen = pick_filter_doc_type(driver, wait, DOC_TYPE)
    time.sleep(3)

    # Master Table Methods are rendered as .mtm-list-card divs, not table rows
    cards = c.visible(driver, ".method-list-card-container .mtm-list-card")
    doc_types_shown = []
    for card in cards:
        # Read the Document Type span next to the folder icon inside each card
        spans = card.find_elements(By.CSS_SELECTOR, ".summary-item i[title='Document Type'] + span")
        doc_types_shown.append(spans[0].text.strip() if spans else card.text.strip())

    target = chosen.strip().strip("/").split("/")[-1].lower()
    wrong = [dt for dt in doc_types_shown if target not in dt.lower()]
    ok = bool(cards) and not wrong
    return ok, (
        f"Filter '{chosen}' shows {len(cards)} methods"
        + ("" if ok else f", {len(wrong)} of them do not belong to this doc-type")
    )


SCENARIOS = [("Filter by doc-type", filter_by_doc_type)]


def main():
    c.need_env("MASTER_FILTER_DOC_TYPE", "(a doc-type that has a fetch method assigned, e.g. 'aa' or 'HR')")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()