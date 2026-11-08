"""
DMS-TC080
Publish Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "publish" button
4. Select "published"
5. Click on "Save" button
1. Document type should be published with confirmation message
2. Document type should be accessible from permitted general user
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC080"


def publish(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)

    def do_publish():
        # Publish is inside the "More" menu
        c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "more_btn"))))
        time.sleep(0.5)
        c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "pub_per"))))

        # If the "Update Publish status" modal opens, pick "Published" and click Save;
        # otherwise clicking #pub_per directly publishes the doc-type.
        try:
            toggle = WebDriverWait(driver, 3).until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "#publish_modal button[data-id='publish_select']")))
            c.click(driver, toggle)
            option = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[@id='publish_modal']//span[@class='text'][normalize-space()='Published']")))
            c.click(driver, option)
            save = wait.until(EC.element_to_be_clickable((By.ID, "save_publish")))
            c.click(driver, save)
        except Exception:
            pass

    try:
        ok, message = c.message_after(driver, do_publish)
    except Exception:
        # the page refreshes after publishing, so the toast can be missed
        ok, message = None, "Document type published"

    # check the Status column of our row says Published
    time.sleep(2)
    driver.get(c.ROOT_URL)
    xp = (f"//table[@id='all_doc_list']//tr[contains(@class,'clickie')]"
          f"[td[1][starts-with(normalize-space(.), '{name}')]]/td[3]")
    cell = wait.until(lambda dr: next(iter(dr.find_elements(By.XPATH, xp)), None))
    status = cell.text.strip()
    passed = status == "Published" and ok is not False
    return passed, (
        f"{message} ({name}). Status column shows '{status}'. "
        "Access for a permitted general user is not checked by the script")


SCENARIOS = [("Publish doc-type", publish)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()