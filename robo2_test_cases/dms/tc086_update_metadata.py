"""
DMS-TC086
Update Metadata
1. Go to https://flow.robo2mation.com/dms/document/root
2. Double click on a doc-type
3. Select a metadata
4. Click on "Update" button
5. Update metadata information
6. Click on "Save" button
Metadata should be updated with confirmation message
"""
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC086"

ADD = "#add_new_metafield"


def create_metadata_here(driver, wait, doc_type, display):
    """Setup: open the doc-type, Add, fill the form (String type), Save. Leaves the doc-type page open."""
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, doc_type)
    c.double_click_label(driver, wait, doc_type)
    time.sleep(2)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "add_btn"))))
    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, ADD)))
    time.sleep(1)

    values = (("title", display.lower().replace(" ", "_")),
              ("displayname", display), ("min", "1"), ("max", "50"))
    for field, value in values:
        box = driver.find_element(By.CSS_SELECTOR, f"{ADD} input[name='{field}']")
        box.clear()
        box.send_keys(value)

    # data type: pick String
    c.click(driver, driver.find_element(By.CSS_SELECTOR, f"{ADD} button[data-id='add_meta_type']"))
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH,
        "//div[@id='add_new_metafield']//button[@data-id='add_meta_type']"
        "/following-sibling::div//span[@class='text'][normalize-space()='String']")))
    c.click(driver, option)

    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "save_metafield"))))
    if not c.wait_text(driver, display, 10):
        errors = [e.text.strip() for e in driver.find_elements(
            By.CSS_SELECTOR, f"{ADD} .parsley-errors-list li") if e.is_displayed() and e.text.strip()]
        raise c.SetupError(f"meta-data was not created. Form errors: {errors or 'none shown'}")


def update_metadata(driver, wait):
    doc_type = d.new_doc_type(driver, wait)
    display = datetime.now().strftime("AUTO Meta %H%M%S")
    create_metadata_here(driver, wait, doc_type, display)
    new_display = display + " UPD"

    # select the meta-data row
    xp = f"//tr[.//td[contains(normalize-space(.), '{display}')]]"
    row = wait.until(lambda dr: next(iter(
        [r for r in dr.find_elements(By.XPATH, xp) if r.is_displayed()]), None))
    c.click(driver, row)

    # More -> Update (only appears once a meta-data is selected)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    time.sleep(0.5)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "update_btn"))))

    # change the display name and save
    box = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#update_metafield_modal input[name='displayname']")))
    time.sleep(1)                                   # let the form fill with the current values
    box.clear()
    box.send_keys(new_display)
    save = wait.until(EC.element_to_be_clickable((By.ID, "update_meta_save")))
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except Exception:
        ok, message = None, "confirmation message was not captured"

    shown = c.wait_text(driver, new_display, 10)
    passed = shown and ok is not False
    return passed, f"{message} ('{display}' -> '{new_display}'). " + (
        "New display name is listed" if shown else "New display name is NOT listed")


SCENARIOS = [("Update metadata", update_metadata)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()