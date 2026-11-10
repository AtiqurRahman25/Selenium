"""
DMS-TC126
Save Search
1. Go to save search list
2. Double click on a save search
3. Click on "Search"
Saved search list should be shown & by double clicking on a saved search should fillup relavent metadata
"""
import time
from datetime import datetime

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC126"


def search_meta_values(driver):
    """Values of the metadata inputs currently shown in the advanced search form."""
    inputs = driver.find_elements(By.CSS_SELECTOR, "#dms_search_form .meta-data-wrap input[id]:not([type='hidden'])")
    return [i.get_attribute("value") for i in inputs]


def saved_search_list(driver, wait):
    info = c.upload_document(driver, wait)
    search_name = datetime.now().strftime("AUTO_SEARCH_%H%M%S")
    ok, message = d.save_search(driver, wait, search_name, info)
    if not ok:
        raise c.SetupError(f"could not save the search ({message})")

    driver.get(c.EXPLORER_URL)
    c.click(driver, wait.until(EC.element_to_be_clickable(c.FILTER_BTN)))
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "saved_search"))))  # saved search list
    time.sleep(2)
    c.double_click_label(driver, wait, search_name)
    time.sleep(2)

    # save_search() saved: doc type + first metadata value (or doc type + document name if there is no metadata)
    if info["values"]:
        expected = info["values"][0][1]
        try:
            WebDriverWait(driver, 10).until(lambda drv: expected in search_meta_values(drv))
            filled_ok, filled_msg = True, f"metadata '{expected}' was filled"
        except TimeoutException:
            filled_ok, filled_msg = False, f"metadata '{expected}' was NOT filled (form has {search_meta_values(driver)})"
    else:
        expected = info["name"]
        filled = wait.until(EC.visibility_of_element_located((By.ID, "docname"))).get_attribute("value")
        filled_ok, filled_msg = filled == expected, f"document name field has '{filled}' (expected '{expected}')"

    # step 3: click Search either way, so the result shows what Search returns for the restored form
    c.click(driver, driver.find_element(By.ID, "search_btn"))
    shown = c.wait_text(driver, info["name"], 10)
    search_msg = "Search shows the document" if shown else "Search does NOT show the document"
    return filled_ok and shown, f"Saved search '{search_name}' listed, double click: {filled_msg}; {search_msg}"


SCENARIOS = [("Saved search list", saved_search_list)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()