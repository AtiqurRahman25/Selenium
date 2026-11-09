"""
DMS-TC110
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/master-table-method/
2. Clone a fetch method
3. Method should be cloned with proper confirmation message.
"""
import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC110"


def clone_method(driver, wait, name):
    """Open the card's settings (gear icon) if Clone is hidden, click Clone, and complete the clone
    (either via confirmation popup or by saving the pre-filled clone form)."""
    card_xpath = (
        f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
        f" and .//span[@title={c.xpath_text(name)}]]"
    )
    try:
        card = WebDriverWait(driver, 10).until(
            lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None)
        )
        button = card.find_element(By.CSS_SELECTOR, "button.mtm_clone_button")
        if not button.is_displayed():
            c.click(driver, card.find_element(By.CSS_SELECTOR, "a.mtm_setting_button"))
            time.sleep(1)
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not found in the method list")

    clone_name = f"{name}_CLONE"

    def action():
        c.click(driver, button)
        time.sleep(1.5)

        # Case 1: Clicking Clone opens #mtm_creation_main_form pre-filled with the method's data
        form = driver.find_elements(By.ID, "mtm_creation_main_form")
        if form and form[0].is_displayed():
            title = driver.find_element(By.CSS_SELECTOR, f'{d.MTM_FORM} input[name="method_name"]')
            # Wait for JS to finish populating the cloned dropdowns (same as d.update_method)
            WebDriverWait(driver, 15).until(
                lambda drv: drv.execute_script(
                    "var s = document.querySelector(arguments[0]); return !!s && !!s.value;",
                    f'{d.MTM_FORM} select[name="mtm_populate_metadata_field"]',
                )
            )
            current_title = (title.get_attribute("value") or "").strip()
            if not current_title or current_title == name:
                title.clear()
                title.send_keys(clone_name)
            save = driver.find_element(By.ID, "save_mtm_dms")
            c.click(driver, save)
            return

        # Case 2: Clicking Clone shows a confirmation modal or clones directly
        try:
            c.confirm(driver, wait, "yes", seconds=5)
        except Exception:
            pass

    ok, message = c.message_after(driver, action)
    return ok, f"{message} ({name})"


def clone(driver, wait):
    name = d.new_method(driver, wait)
    return clone_method(driver, wait, name)


SCENARIOS = [("Clone method", clone)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()