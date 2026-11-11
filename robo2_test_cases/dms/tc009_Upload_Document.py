"""
DMS-TC009
Upload Document
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Attach a document (image, media or office file), select doc-type, give all required meta-data value & give unique value to unique field.
3. Click on "Save" button
Documents should be uploaded with proper confirmation message
"""
from datetime import datetime

import common as c

TEST_CASE_ID = "DMS-TC009"
FILES_TO_UPLOAD = ["png", "mp3", "docx"]  # image, media, office file


def upload_document(driver, wait, ext):
    """Attach a sample file of type `ext`, fill required metadata, and save."""
    try:
        c.prepare_upload(driver, wait, ext)
        c.set_document_name(driver, datetime.now().strftime(f"AUTO_{ext}_%H%M%S"))
        ok, message = c.message_after(driver, lambda: c.click(driver, driver.find_element(*c.UPLOAD_BTN)))
    except Exception as error:
        return c.fail(driver, TEST_CASE_ID, ext, c.short(error))

    if ok:
        c.save_shot(driver, TEST_CASE_ID, ext, "PASS")
        return True, message
    return c.fail(driver, TEST_CASE_ID, ext, message)


def main():
    c.check_excel_ready(TEST_CASE_ID)

    driver, wait = c.start_browser()
    passed, failed = [], []

    try:
        c.login(driver, wait)
        for ext in FILES_TO_UPLOAD:
            ok, msg = upload_document(driver, wait, ext)
            print(f"{ext:5} -> {'PASS' if ok else 'FAIL'} ({msg})")
            (passed if ok else failed).append(f"{ext} ({msg})")
    finally:
        driver.quit()

    total = len(FILES_TO_UPLOAD)
    if failed:
        status = "Fail"
        actual = f"Uploaded {len(passed)}/{total}. Failed: " + ", ".join(failed)
    else:
        status = "Pass"
        actual = f"All {total} documents uploaded. Confirmation shown: " + "; ".join(passed)

    c.write_result(TEST_CASE_ID, actual, status)
    print(f"\n{TEST_CASE_ID}: {status}")
    if status == "Fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
