"""
DMS-TC049
Document Watermark
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Select a document type
3. Attach a pdf doc
4. Click on "Watermark File" field
5. Select a single watermark doc
6. Click on "Attach"
Document should be watermarked with proper confirmation message
"""
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC049"


def watermark_document(driver, wait):
    c.prepare_upload(driver, wait, "pdf")  # steps 1-3: attach a pdf & select document type
    text = datetime.now().strftime("AUTO_WM_%H%M%S")
    ok, message = d.create_text_watermark(driver, wait, text)
    if not ok:
        raise c.SetupError(f"could not create watermark ({message})")

    # Step 4-5: Open Public Library (where custom text watermarks are stored) and check the watermark's checkbox
    d.open_watermark_tab(driver, wait, "watermark_commonly_used_files_tab")
    checkbox_label = wait.until(
        EC.element_to_be_clickable(
            (
                By.XPATH,
                f"//input[@name='watermark_file_check' and contains(@value, {c.xpath_text(text)})]/..",
            )
        )
    )
    c.click(driver, checkbox_label)
    time.sleep(1)

    # Step 6: Click on "Attach" (#attachWatermarkFile)
    attach = wait.until(EC.element_to_be_clickable((By.ID, "attachWatermarkFile")))
    c.click(driver, attach)
    time.sleep(2)

    selected = driver.find_element(By.ID, "selected_watermark_name").text.strip()
    if not selected:
        return False, "watermark was not attached to the document (no watermark name shown)"

    # Ensure Document Name is populated before clicking Upload (#submit_meta_data)
    c.set_document_name(driver, datetime.now().strftime("AUTO_%H%M%S"))
    ok, message = c.message_after(driver, lambda: c.click(driver, driver.find_element(*c.UPLOAD_BTN)))
    return ok, f"Watermark '{selected}' attached. Upload message: {' '.join(message.split())}"


SCENARIOS = [("Document watermark", watermark_document)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()