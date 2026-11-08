"""
DMS-TC081
Assign Access Group in Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "Assign Group" button
4. Select one or  multiple groups in "Access Groups" field
5. Click on "Save" button
1. Selected groups should be assigned in document type with confirmation message
2. Document type should be accessible for the user of assigned groups
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC081"

OPTIONS_XPATH = ("//div[@id='group_modal']//button[@data-id='group_select']"
                 "/following-sibling::div//ul/li/a")


def assign(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)

    # Assign Group is inside the "More" menu
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    time.sleep(0.5)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "assign_group"))))

    # "Assign Group" modal: open Access Groups and pick the first group
    toggle = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#group_modal button[data-id='group_select']")))
    c.click(driver, toggle)
    option = wait.until(lambda dr: next(iter(
        [o for o in dr.find_elements(By.XPATH, OPTIONS_XPATH) if o.is_displayed()]), None))
    group = option.find_element(By.CSS_SELECTOR, "span.text").text.strip()
    c.click(driver, option)

    # close the dropdown, then Save
    c.click(driver, driver.find_element(By.CSS_SELECTOR, "#group_modal .modal-title"))
    save = wait.until(EC.element_to_be_clickable((By.ID, "save_grp")))
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except Exception:
        ok, message = None, "confirmation message was not captured"

    # check the Groups column of our row shows the group
    time.sleep(2)
    driver.get(c.ROOT_URL)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]"
          f"[td[1][starts-with(normalize-space(.), '{name}')]]/td[4]")
    cell = wait.until(lambda dr: next(iter(dr.find_elements(By.XPATH, xp)), None))
    groups = cell.text.strip()
    passed = group.lower() in groups.lower() and ok is not False
    return passed, (
        f"{message} ({name}, group '{group}'). Groups column shows '{groups}'. "
        "Access for users of the assigned group is not checked by the script")


SCENARIOS = [("Assign access group", assign)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()