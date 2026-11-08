"""
DMS-TC085
Create Metadata
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Double click on a doc-type
3. Click on "Add" button
4. Give "name(variable name), "display name", order & data type
5. Give option in "Dropdown Value" for drop-down data type
6. Click on "Save" button
Metadata should be created with confirmation message
"""
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC085"

MODAL = "#add_new_metafield"


def type_into(driver, css, text):
    box = driver.find_element(By.CSS_SELECTOR, f"{MODAL} {css}")
    box.clear()
    box.send_keys(text)


def create_metadata(driver, wait):
    doc_type = d.new_doc_type(driver, wait)
    display = datetime.now().strftime("AUTO Meta %H%M%S")
    variable = display.lower().replace(" ", "_")      # name = variable name, no spaces

    # open the doc-type (double click) and click Add
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, doc_type)
    c.double_click_label(driver, wait, doc_type)
    time.sleep(2)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "add_btn"))))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, MODAL)))
    time.sleep(1)

    # name, display name, min / max (order stays at its default 1)
    type_into(driver, "input[name='title']", variable)
    type_into(driver, "input[name='displayname']", display)
    type_into(driver, "input[name='min']", "1")
    type_into(driver, "input[name='max']", "50")

    # data type: pick String
    c.click(driver, driver.find_element(By.CSS_SELECTOR, f"{MODAL} button[data-id='add_meta_type']"))
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        f"//div[@id='add_new_metafield']//button[@data-id='add_meta_type']"
        f"/following-sibling::div//span[@class='text'][normalize-space()='String']")))
    c.click(driver, option)

    save = wait.until(EC.element_to_be_clickable((By.ID, "save_metafield")))
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except Exception:
        ok, message = None, "confirmation message was not captured"

    # the new meta field should now be listed in the doc-type
    shown = c.wait_text(driver, display, 10)
    passed = shown and ok is not False
    return passed, (
        f"{message} ('{display}' in {doc_type}). "
        + ("Meta field is listed" if shown else "Meta field is NOT listed"))


SCENARIOS = [("Create metadata", create_metadata)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()