"""
DMS-TC067
Categorization/Doc-Type Creation
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Click on "Add" button
3. Select category/doc-type
4. Give a tree wise unique category/doc-type name
5. Click on "Save" button
Category/doc-type should be created with proper confirmation message
"""
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c

TEST_CASE_ID = "DMS-TC067"

MODAL = "add_parent_new_cat_doc"  # the Add dialog when nothing is selected in the tree


def create_doc_type(driver, wait):
    name = datetime.now().strftime("AUTO_DT_%H%M%S")  # tree wise unique name

    driver.get(c.ROOT_URL)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "add_btn"))))
    modal = wait.until(EC.visibility_of_element_located((By.ID, MODAL)))
    time.sleep(1)

    # choose "Document" (= doc-type) in the Category / Document dropdown
    c.click(driver, modal.find_element(By.CSS_SELECTOR, "button[data-id='parent_cat_doc_field']"))
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//div[@id='{MODAL}']//button[@data-id='parent_cat_doc_field']"
                  "/following-sibling::div//span[@class='text'][normalize-space()='Document']")))
    c.click(driver, option)
    time.sleep(1)
    chosen = modal.find_element(By.CSS_SELECTOR, "button[data-id='parent_cat_doc_field'] .filter-option").text.strip()
    if chosen.lower() != "document":
        return False, f"could not choose Document in the dropdown (it shows '{chosen}')"

    box = modal.find_element(By.CSS_SELECTOR, "input[name='name']")
    box.clear()
    box.send_keys(name)

    save = wait.until(EC.element_to_be_clickable((By.ID, "submit_add_new_cat_doc")))
    ok, message = c.message_after(driver, lambda: c.click(driver, save))
    return ok, f"{message} ({name})"


SCENARIOS = [("Create doc-type", create_doc_type)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()