"""
DMS-TC112
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Assign a fetch method where all the metadata's are same
3. Fetch method should be assigned to the selected doc-type with proper confirmation message.
"""
import os
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC112"

DOC_TYPE = os.getenv("MASTER_ASSIGN_DOC_TYPE")  # a doc-type whose meta-data match the method
ASSIGN_BOX = "#method_assign_to_document_type_parent"


def pick_assign_doc_type(driver, wait, term):
    """'Assign To' is a Select2 search box: its drop-down has no options until you type, so type the name and click it."""
    search = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"{ASSIGN_BOX} input.select2-search__field")))
    search.click()
    typed = term.strip().strip("/").split("/")[-1]
    for letter in typed[:30]:
        search.send_keys(letter)
        time.sleep(0.2)
    option_css = ".select2-container--open .select2-results__option"
    WebDriverWait(driver, 15).until(lambda drv: bool(c.select2_options(drv, option_css)))
    time.sleep(1.5)
    options = c.select2_options(driver, option_css)
    ActionChains(driver).move_to_element(options[c.best_option_index(options, term)]).click().perform()
    time.sleep(1)
    if not driver.find_elements(By.CSS_SELECTOR, f"{ASSIGN_BOX} li.select2-selection__choice"):
        raise c.SetupError(f"document type '{typed}' could not be selected in the Assign To box")


def assign_method(driver, wait, name):
    card_xpath = (
        f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
        f" and .//span[@title={c.xpath_text(name)}]]"
    )
    try:
        card = WebDriverWait(driver, 10).until(
            lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None)
        )
        button = card.find_element(By.CSS_SELECTOR, "button.mtm_assign_button")
        if not button.is_displayed():
            c.click(driver, card.find_element(By.CSS_SELECTOR, "a.mtm_setting_button"))
            time.sleep(1)
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not found in the method list")

    def action():
        c.click(driver, button)
        wait.until(EC.visibility_of_element_located((By.ID, "on_assign_method_doc_type_modal")))
        time.sleep(1)
        pick_assign_doc_type(driver, wait, (DOC_TYPE or "aa").strip())
        c.click(driver, driver.find_element(By.ID, "on_assign_method_doc_type_modal_form_save_btn"))

    try:
        ok, message = c.message_after(driver, action)
    except TimeoutException:
        problem = driver.find_element(By.ID, "doc_type_assign_error_div").text.strip()
        raise c.SetupError(f"method '{name}' was not assigned. The window says: {problem or 'nothing'}")
    problem = driver.find_element(By.ID, "doc_type_assign_error_div").text.strip()
    return ok, (f"{message} ({name} -> {DOC_TYPE})" + (f". Window says: {problem}" if problem else "")
                + ". Fetched data on the upload page is not checked by the script")


def assign(driver, wait):
    name = d.new_method(driver, wait)
    return assign_method(driver, wait, name)


SCENARIOS = [("Assign method", assign)]


def main():
    c.need_env("MASTER_ASSIGN_DOC_TYPE", "(a doc-type whose meta-data match the method)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()