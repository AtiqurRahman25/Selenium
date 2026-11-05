"""
DMS-TC046
Search Water Mark
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Select a document type
3. Click on "Watermark File" field
4. Go to "Public Library" or "Private Library" tab
5. Search by filename
Only searched result should be shown
"""
import time
from datetime import datetime

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC046"


def search_watermark(driver, wait):
    c.prepare_upload(driver, wait, "pdf")
    run_id = datetime.now().strftime("%H%M%S")
    wanted, other = f"AUTO_WM_A{run_id}", f"AUTO_WM_B{run_id}"
    for text in (wanted, other):  # two watermarks, so "only the searched result" means something
        ok, message = d.create_text_watermark(driver, wait, text)
        if not ok:
            raise c.SetupError(f"could not create watermark '{text}' ({message})")

    # Step 4: Go to "Public Library" tab (where custom text watermarks are saved by default)
    d.open_watermark_tab(driver, wait, "watermark_commonly_used_files_tab")
    container = (By.ID, "watermark_commonly_used_files_container")
    wait.until(lambda drv: wanted.lower() in drv.find_element(*container).text.lower())

    # Step 5: Search by filename
    box = wait.until(EC.element_to_be_clickable((By.ID, "watermark_files_search_box")))
    c.click(driver, box)
    box.clear()
    for ch in wanted:
        ActionChains(driver).send_keys(ch).perform()
        time.sleep(0.05)
    ActionChains(driver).send_keys(Keys.ENTER).perform()

    # Wait up to 10s for the AJAX search to filter out `other`
    try:
        WebDriverWait(driver, 10).until(
            lambda drv: (
                wanted.lower() in drv.find_element(*container).text.lower()
                and other.lower() not in drv.find_element(*container).text.lower()
            )
        )
    except Exception:
        pass

    shown = driver.find_element(*container).text.lower()
    if wanted.lower() in shown and other.lower() not in shown:
        return True, f"Search for '{wanted}' shows only that watermark"
    return False, f"Search for '{wanted}' shows: {' '.join(shown.split())[:100] or 'nothing'}"


SCENARIOS = [("Search watermark", search_watermark)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()