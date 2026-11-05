"""
DMS-TC042
Watermark (Custom Text)
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Select a document type
3. Click on "Watermark File" field
4. Go to "Custom Text"
5. Type watermark text (max: 20 character)
6. Click on "Create"
Watermark should be created with proper confirmation message.
"""
from datetime import datetime

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC042"

def custom_text(driver, wait):
    c.prepare_upload(driver, wait, "pdf")  # step 2: a document type is selected
    text = datetime.now().strftime("AUTO_WM_%H%M%S")  # max 20 characters
    return d.create_text_watermark(driver, wait, text)


SCENARIOS = [("Custom text watermark", custom_text)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
