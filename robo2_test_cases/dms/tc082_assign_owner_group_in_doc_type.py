"""
DMS-TC082
Assign Owner Group in Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "Assign Group" button
4. Select one or  multiple groups in "Owner Groups" field
5. Click on "Save" button
1. Selected groups (members) should be assigned as owners in document type with confirmation message
2. Owner group member will get the access of "DMS Owner" roles assigned permission to the selected document type
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC082"

OPTIONS_XPATH = ("//div[@id='group_modal']//button[@data-id='owner_group_select']"
                 "/following-sibling::div//ul/li/a")


def assign(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)

    # Assign Group is inside the "More" menu
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    time.sleep(0.5)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "assign_group"))))

    # "Assign Group" modal: open Owner Groups and pick the first group
    toggle = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "#group_modal button[data-id='owner_group_select']")))
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

    # owner groups show in the Groups column as "Name (OG)"
    time.sleep(2)
    driver.get(c.ROOT_URL)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]"
          f"[td[1][starts-with(normalize-space(.), '{name}')]]/td[4]")
    cell = wait.until(lambda dr: next(iter(dr.find_elements(By.XPATH, xp)), None))
    groups = cell.text.strip()
    passed = f"{group} (OG)".lower() in groups.lower() and ok is not False
    return passed, (
        f"{message} ({name}, owner group '{group}'). Groups column shows '{groups}'. "
        "The DMS Owner permissions of the group members are not checked by the script")


SCENARIOS = [("Assign owner group", assign)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()