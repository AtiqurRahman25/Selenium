"""
DMS-TC024
Document Full View
1. Open a document 
2. Click on "view"
Document should be opened in a new tab
"""
import time

from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC024"

def full_view(driver, wait):
    c.new_document(driver, wait)
    old_tabs = driver.window_handles
    c.click_label(driver, wait, "view")
    WebDriverWait(driver, 10).until(lambda drv: len(drv.window_handles) > len(old_tabs))
    driver.switch_to.window(driver.window_handles[-1])
    time.sleep(2)
    url = driver.current_url
    return True, f"Document opened in a new tab ({url})"


SCENARIOS = [("Full view", full_view)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)

if __name__ == "__main__":
    main()