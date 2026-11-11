"""
DMS-TC137
PDF Document OCR from My Documents Search
1. Enable OCR for a document type
2. Upload readable quality pdf document
3. Wait until OCR status is done
4. In Explorer search Select OCR enabled document type
5. Type document content in "Content Search" field
6. Observe the results
Matched content should show the respective document
"""
import os
import time

from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC137"

DOC_TYPE = os.getenv("OCR_DOC_TYPE")        # a doc-type with OCR enabled
SEARCH_TEXT = os.getenv("OCR_SEARCH_TEXT")  # a word or phrase that is inside the sample PDF


def wait_for_ocr(driver, wait, name, timeout_seconds=60):
    """Open document view, verify OCR status is enabled/active, and return to explorer."""
    c.open_document(driver, wait, name)
    time.sleep(2)
    end = time.time() + timeout_seconds
    ocr_status = ""
    while time.time() < end:
        status_el = driver.find_elements(By.ID, "ocr-status")
        ocr_status = (
            (status_el[0].text or status_el[0].get_attribute("textContent") or "").strip()
            if status_el
            else ""
        )
        if ocr_status and ocr_status.upper() != "N/A":
            break
        time.sleep(2)

    # Close document view tab and switch back to main tab
    if len(driver.window_handles) > 1:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    if not ocr_status or ocr_status.upper() == "N/A":
        return False, f"OCR was not enabled for document '{name}' (OCR Status: {ocr_status or 'missing'})"
    return True, f"OCR Status: {ocr_status}"


def ocr_explorer_search(driver, wait):
    info = c.upload_document(driver, wait, "pdf", doc_type=DOC_TYPE)
    name = info["name"]
    ok, status_msg = wait_for_ocr(driver, wait, name)
    if not ok:
        return False, status_msg
    driver.get(c.EXPLORER_URL)
    time.sleep(2)
    c.advanced_search(driver, wait, None, match_all=False, doc_type=info["doc_type"], extra=[("content search", SEARCH_TEXT)])
    time.sleep(3)
    shown = name.lower() in c.body_text(driver)
    return shown, f"Content search '{SEARCH_TEXT}' in My Documents " + ("shows the document" if shown else "does NOT show the document") + f" ({status_msg})"


SCENARIOS = [("OCR My Documents search", ocr_explorer_search)]


def main():
    c.need_env("OCR_DOC_TYPE", "(search text of a doc-type with OCR enabled)")
    c.need_env("OCR_SEARCH_TEXT", "(a word that is inside the sample pdf)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
