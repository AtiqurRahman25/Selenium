"""
DMS-TC037
Document OCR
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/
2. Try to attach a doc apart from pdf or image (jpg,jpeg or png)
3. Try to click on "OCR Document" icon
Document ocr should be done.
"""
import time

from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC037"


def expand_system_metadata(driver):
    panel = driver.find_elements(By.ID, "systemDefinedMetaDataBody")
    if panel and "in" not in (panel[0].get_attribute("class") or "").split():
        toggle = driver.find_elements(
            By.CSS_SELECTOR,
            "[data-target='#systemDefinedMetaDataBody'], #systemDefinedMetaDataBodyHeadingOne a",
        )
        if toggle:
            c.click(driver, toggle[0])
            time.sleep(1.5)


def ocr(ext):
    def scenario(driver, wait):
        info = c.upload_document(driver, wait, ext)
        name = info["name"]

        c.open_document(driver, wait, name)
        time.sleep(2)
        expand_system_metadata(driver)

        status_el = driver.find_elements(By.ID, "ocr-status")
        ocr_status = (
            (status_el[0].text or status_el[0].get_attribute("textContent") or "").strip()
            if status_el
            else ""
        )
        if not ocr_status or ocr_status.upper() == "N/A":
            return False, f"OCR was not enabled for uploaded .{ext} document '{name}' (OCR Status: {ocr_status or 'missing'})"

        return True, f"Document '{name}' (.{ext}) uploaded with OCR enabled (OCR Status: {ocr_status})"

    return scenario


SCENARIOS = [("OCR pdf", ocr("pdf")), ("OCR png", ocr("png"))]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
