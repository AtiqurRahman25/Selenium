"""
DMS-TC045
Watermark (Upload)
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Select a document type
3. Click on "Watermark File" field
4. Go to "Upload" tab
5. Attach watermark doc (image or pdf file)
6. Click on "upload"
Watermark should be uploaded with proper confirmation message.
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC045"

def upload_watermark(driver, wait):
    c.prepare_upload(driver, wait, "pdf")
    d.open_watermark_tab(driver, wait, "watermark_upload_file_tab")
    c.attach_to_file_input(driver, wait, c.find_sample_file("png")[1])  # watermark must be an image or pdf
    button = wait.until(EC.element_to_be_clickable((By.ID, "submit-all")))  # enabled after a file is attached
    return c.message_after(driver, lambda: c.click(driver, button))


SCENARIOS = [("Upload watermark", upload_watermark)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
