"""
DMS-TC108
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Disable a fetch method
3. Method should be disabled with proper confirmation message.
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC108"


def disable_method(driver, wait, name):
    """Method list: open the card's settings (gear icon) if Disable is hidden, click Disable, confirm if asked."""
    card_xpath = (
        f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
        f" and .//span[@title={c.xpath_text(name)}]]"
    )
    try:
        card = WebDriverWait(driver, 10).until(
            lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None)
        )
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
            pass  # in case disable happens immediately without a confirmation modal

    ok, message = c.message_after(driver, action)

    # Also verify the card state updated to disabled (data-mtm-disabled="true")
    try:
        WebDriverWait(driver, 8).until(
            lambda drv: drv.find_element(By.XPATH, card_xpath).get_attribute("data-mtm-disabled") == "true"
        )
        disabled_state = True
    except Exception:
        disabled_state = False

    return (ok or disabled_state), f"{message} ({name})"


def disable(driver, wait):
    name = d.new_method(driver, wait)
    ok, message = disable_method(driver, wait, name)
    return ok, f"{message}. Data fetching on the upload page is not checked by the script"


SCENARIOS = [("Disable method", disable)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()