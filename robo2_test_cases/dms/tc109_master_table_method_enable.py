"""
DMS-TC109
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Enable a fetch method
3. Method should be enabled with proper confirmation message.
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC109"


def toggle_method_state(driver, wait, name, target_disabled):
    """Click the card's settings gear icon if needed, click button.mtm_disable_button (which toggles
    both Disable and Enable), confirm 'yes' if prompted, and verify data-mtm-disabled."""
    card_xpath = (
        f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
        f" and .//span[@title={c.xpath_text(name)}]]"
    )
    try:
        card = WebDriverWait(driver, 10).until(
            lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None)
        )
        # Both DISABLE and ENABLE use the button.mtm_disable_button element
        button = card.find_element(By.CSS_SELECTOR, "button.mtm_disable_button")
        if not button.is_displayed():
            c.click(driver, card.find_element(By.CSS_SELECTOR, "a.mtm_setting_button"))
            time.sleep(1)
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not found in the method list")

    def action():
        c.click(driver, button)
        time.sleep(1)
        try:
            c.confirm(driver, wait, "yes", seconds=5)
        except Exception:
            pass

    ok, message = c.message_after(driver, action)

    expected_attr = "true" if target_disabled else "false"
    try:
        WebDriverWait(driver, 8).until(
            lambda drv: drv.find_element(By.XPATH, card_xpath).get_attribute("data-mtm-disabled") == expected_attr
        )
        state_ok = True
    except Exception:
        state_ok = False

    return (ok or state_ok), message


def enable(driver, wait):
    name = d.new_method(driver, wait)
    ok, message = toggle_method_state(driver, wait, name, target_disabled=True)
    if not ok:
        raise c.SetupError(f"could not disable the method ({message})")
    time.sleep(1)
    ok, message = toggle_method_state(driver, wait, name, target_disabled=False)
    return ok, f"{message} ({name}). Data fetching on the upload page is not checked by the script"


SCENARIOS = [("Enable method", enable)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()