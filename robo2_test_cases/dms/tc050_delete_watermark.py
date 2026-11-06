"""
DMS-TC050
Delete Watermark
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Select a document type
3. Click on "Watermark File" field
4. Go to "Public Library" or "Private Library" tab
5. Click on "Delete" icon
Watermark should be deleted with proper confirmation message
"""
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC050"


def delete_watermark(driver, wait):
    c.prepare_upload(driver, wait, "pdf")
    text = datetime.now().strftime("AUTO_WM_%H%M%S")
    ok, message = d.create_text_watermark(driver, wait, text)
    if not ok:
        raise c.SetupError(f"could not create watermark ({message})")

    # Open Public Library (where custom text watermarks are saved by default)
    d.open_watermark_tab(driver, wait, "watermark_commonly_used_files_tab")
    container = driver.find_element(By.ID, "watermark_commonly_used_files_container")
    icon_xpath = (".//div[contains(@class,'list-group-item')]"
                  f"[contains(., '{text}')]//strong[contains(@class,'watermark-delete')]")

    def delete_it():
        icons = WebDriverWait(driver, 10).until(lambda drv: container.find_elements(By.XPATH, icon_xpath))
        c.click(driver, icons[0])
        c.confirm(driver, wait, "yes")

    ok, message = c.message_after(driver, delete_it)
    if not ok:
        return False, message
    time.sleep(2)

    gone = text.lower() not in driver.find_element(By.ID, "watermark_commonly_used_files_container").text.lower()
    return gone, f"{message}. Watermark " + ("removed from the library" if gone else "still shown in the library")


SCENARIOS = [("Delete watermark", delete_watermark)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
