"""
DMS-TC084
Document Notify Off
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "Notify Off" button
4. Select one or  multiple groups in "Owner Groups" field
5. Click on "Save" button
1. Selected Owner group members should not get system notification when document (including version document) is downloaded by any of the access group or owner group users.
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC084"


def click_notify(driver, wait, name, expect):
    """Select the doc-type, open More, click the notify toggle. expect = 'on' or 'off' (what the menu should say)."""
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
    time.sleep(0.5)
    button = wait.until(EC.element_to_be_clickable((By.ID, "notify-enable")))
    label = " ".join(button.text.split())
    if label.lower() != f"notify {expect}":
        raise Exception(f"menu shows '{label}', expected 'Notify {expect.title()}'")
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, button))
    except Exception:
        ok, message = None, "confirmation message was not captured"
    return ok, message


def notify_is_on(driver, wait, name):
    """Reload the list and read notification:true/false from the row's data-info."""
    time.sleep(2)
    driver.get(c.ROOT_URL)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]"
          f"[td[1][starts-with(normalize-space(.), '{name}')]]")
    row = wait.until(lambda dr: next(iter(dr.find_elements(By.XPATH, xp)), None))
    return "notification:true" in (row.get_attribute("data-info") or "").replace(" ", "")


def notify_off(driver, wait):
    name = d.new_doc_type(driver, wait)

    # setup: turn notify on first, so there is something to turn off
    try:
        click_notify(driver, wait, name, "on")
    except Exception as e:
        raise c.SetupError(f"could not turn notify on ({c.short(e)})")
    if not notify_is_on(driver, wait, name):
        raise c.SetupError("notify did not turn on")

    # test: turn it off
    ok, message = click_notify(driver, wait, name, "off")
    off = not notify_is_on(driver, wait, name)
    passed = off and ok is not False
    return passed, (
        f"{message} ({name}). Notify is " + ("off" if off else "STILL on") +
        ". The missing notification is not checked by the script")


SCENARIOS = [("Notify off", notify_off)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()