"""
DMS-TC002
Document Attach
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/
2. Attach documents (PDF, PNG, JPG, JPEG, SVG, GIF, MP3, MP4, DOC, DOCX, XLS, XLSX, CSV, PPT, PPTX, MSG, EML, TXT) less than 20 mb
System should allow to attach documents (media or office file)
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC002"
NEXT_BTN = (By.XPATH, "//button[normalize-space()='Next']")


def next_is_ready(driver):
    """The Next button is disabled until a file is attached."""
    try:
        btn = driver.find_element(*NEXT_BTN)
        return btn.is_enabled() and "disabled" not in (btn.get_attribute("class") or "").lower()
    except Exception:
        return False


def attach_file(driver, wait, ext):
    """Attach a sample file of type `ext` and verify it appears on the page."""
    sample = c.find_sample_file(ext)
    if not sample:
        return False, "sample file missing"
    file_name, path = sample

    driver.get(c.ATTACH_URL)
    wait.until(EC.presence_of_element_located(c.FILE_INPUT))
    next_was_ready = next_is_ready(driver)

    def attached(d):
        return (
            file_name.lower() in c.body_text(d)
            or bool(d.find_elements(By.CSS_SELECTOR, ".dz-preview, .dz-filename"))
            or (not next_was_ready and next_is_ready(d))
        )

    for file_input in driver.find_elements(*c.FILE_INPUT):
        driver.execute_script(
            "arguments[0].style.display='block'; arguments[0].style.visibility='visible';",
            file_input,
        )
        try:
            file_input.send_keys(path)
            WebDriverWait(driver, 6).until(attached)
            c.save_shot(driver, TEST_CASE_ID, ext, "PASS")
            return True, "attached"
        except Exception:
            continue

    return c.fail(driver, TEST_CASE_ID, ext, "file not shown after attach")


def main():
    c.check_excel_ready(TEST_CASE_ID)

    missing_files = [ext for ext in c.EXTENSIONS if not c.find_sample_file(ext)]
    print(f"Files missing in {c.SAMPLE_DIR}: {missing_files or 'none'}")

    driver, wait = c.start_browser()
    passed, failed = [], []

    try:
        c.login(driver, wait)
        for ext in c.EXTENSIONS:
            ok, msg = attach_file(driver, wait, ext)
            print(f"{ext:5} -> {'PASS' if ok else 'FAIL'} ({msg})")
            (passed if ok else failed).append(ext if ok else f"{ext} ({msg})")
    finally:
        driver.quit()

    total = len(c.EXTENSIONS)
    if failed:
        status = "Fail"
        actual = f"Attached {len(passed)}/{total} file types. Could not attach: " + ", ".join(failed)
    else:
        status = "Pass"
        actual = f"All {total} file types were attached successfully"

    c.write_result(TEST_CASE_ID, actual, status)
    print(f"\n{TEST_CASE_ID}: {status}")
    if status == "Fail":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
