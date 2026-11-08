"""
DMS-TC083
Document Notify On
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "Notify On" button
4. Select one or  multiple groups in "Owner Groups" field
5. Click on "Save" button
1. Selected Owner group members should get system notification when document (including version document) is downloaded by any of the access group or owner group users.
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC083"


def notify_on(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)

    # Notify On is a toggle inside the "More" menu
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    time.sleep(0.5)
    button = wait.until(EC.element_to_be_clickable((By.ID, "notify-enable")))
    label = button.text.strip()
    if "on" not in label.lower():
        return False, f"menu shows '{label}', notify is already on for '{name}'"
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, button))
    except Exception:
        ok, message = None, "confirmation message was not captured"

    # the row's data-info changes to notification:true
    time.sleep(2)
    driver.get(c.ROOT_URL)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]"
          f"[td[1][starts-with(normalize-space(.), '{name}')]]")
    row = wait.until(lambda dr: next(iter(dr.find_elements(By.XPATH, xp)), None))
    state = (row.get_attribute("data-info") or "").replace(" ", "")
    passed = "notification:true" in state and ok is not False
    return passed, (
        f"{message} ({name}). Row state '{state}'. "
        "The notification to the owner group members is not checked by the script")


SCENARIOS = [("Notify on", notify_on)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()