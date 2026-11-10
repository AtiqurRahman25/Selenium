"""
DMS-TC009	
Upload Document	
"1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Attach a document (image, media or office file), select doc-type, give all required meta-data value & give unique value to unique field.
3. Click on ""Save"" button"	
Documents should be uploaded with proper confirmation message
"""
import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC009"
ATTACH_URL = c.BASE_URL + "/dms/document/upload/standard_upload/"
PENDING_URL = c.BASE_URL + "/dms/document/upload/standard_upload/filesave/pendingmetalist/"
FILES_TO_UPLOAD = ["png", "mp3", "docx"]  # image, media, office file

# locators
FILE_INPUT = (By.CSS_SELECTOR, "input[type='file']")
DOC_TYPE_BOX = (By.CSS_SELECTOR, "span.select2-selection[aria-labelledby='select2-DocumentType-container']")
# the page has other select2 boxes too (Share With, Notify To...), so only use the Document Type drop-down
DOC_TYPE_RESULTS = "#select2-DocumentType-results"
DOC_TYPE_SEARCH_BOX = (By.XPATH, "//ul[@id='select2-DocumentType-results']/ancestor::span[contains(@class, 'select2-dropdown')]//input[contains(@class, 'select2-search__field')]")
DOC_TYPE_OPTION = DOC_TYPE_RESULTS + " li.select2-results__option"
# the page says: type 3 or more characters to find a document type. Set DOC_TYPE in .env to use a real name.
DOC_TYPE_SEARCH_TERMS = [os.getenv("DOC_TYPE")] if os.getenv("DOC_TYPE") else ["doc", "inv", "rep", "con", "ent", "ion", "ing"]
METADATA_PANEL = (By.ID, "add_meta_data")
UPLOAD_BTN = (By.ID, "submit_meta_data")
MESSAGE_BOX = ".toast, .alert, .swal2-popup, [role='alert'], .snackbar, .Toastify__toast, .mat-snack-bar-container, .ant-message, .growl-animated, [data-notify], [data-growl='container']"
SUCCESS_WORDS = ["success", "uploaded", "saved"]
ERROR_WORDS = ["error", "failed", "required", "already exists", "invalid"]


def body_text(driver):
    return driver.find_element(By.TAG_NAME, "body").text.lower()


def pending_row_icon(file_name):
    """The paperclip ('Attach document') icon in the visible list row of this file."""
    return (By.XPATH, f"//*[@id='list_view_container']//tr[@data-pending-doc-name={xpath_text(file_name)}]//i[contains(@class, 'add-item')]")


def clear_selected_files(driver):
    """The page remembers files already selected for the meta-data panel. Remove them first."""
    xpath = "//*[@id='selected_file_div']//*[contains(@class, 'deselect-row')]//i[contains(@class, 'delete-item')]"
    for _ in range(20):
        icons = driver.find_elements(By.XPATH, xpath)
        if not icons:
            return
        driver.execute_script("arguments[0].click();", icons[0])
        time.sleep(1)


def real_options(driver):
    """Visible drop-down options, without messages like 'Please enter 2 or more characters'."""
    skip = ("please enter", "searching", "no result", "loading")
    return [o for o in driver.find_elements(By.CSS_SELECTOR, DOC_TYPE_OPTION)
            if o.is_displayed() and o.text.strip() and not any(w in o.text.lower() for w in skip)]


def document_type_selected(driver):
    text = driver.find_element(By.ID, "select2-DocumentType-container").text.strip().lower()
    return bool(text) and "search for a document type" not in text


def results_message(driver):
    """Message inside the drop-down, e.g. 'Please enter 2 or more characters' or 'No results found'."""
    messages = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, DOC_TYPE_RESULTS + " .select2-results__message") if e.is_displayed()]
    return messages[0] if messages else ""


def search_finished(driver):
    message = results_message(driver).lower()
    return bool(real_options(driver)) or (message and "please enter" not in message and "searching" not in message)


def select_document_type(driver, wait):
    """Open the Document Type drop-down, type 3+ characters like a user and pick the first result."""
    wait.until(EC.element_to_be_clickable(DOC_TYPE_BOX)).click()
    search_box = wait.until(EC.visibility_of_element_located(DOC_TYPE_SEARCH_BOX))
    search_box.click()  # focus it, then type into the focused box
    for term in DOC_TYPE_SEARCH_TERMS:
        ActionChains(driver).key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).send_keys(Keys.BACKSPACE).perform()
        for letter in term:  # one letter at a time, so the search starts like it does for a user
            ActionChains(driver).send_keys(letter).perform()
            time.sleep(0.3)
        try:
            WebDriverWait(driver, 8).until(search_finished)
        except Exception:
            pass
        if not real_options(driver):
            print(f"   document type search '{term}' -> {results_message(driver) or 'nothing shown'}")
            continue  # try the next search text
        ActionChains(driver).send_keys(Keys.ENTER).perform()  # selects the highlighted first result
        time.sleep(1)
        if not document_type_selected(driver):
            options = real_options(driver)
            if options:
                driver.execute_script("arguments[0].click();", options[0])  
                time.sleep(1)
        if document_type_selected(driver):
            time.sleep(2)  
            return
    raise Exception("document type could not be selected")


def fill_required_fields(panel, driver, run_id):
    """Fill every empty required field (label with *) with a unique value."""
    for i, label in enumerate(panel.find_elements(By.XPATH, ".//label[contains(., '*')]")):
        if "document type" in label.text.lower():
            continue  # handled by select_document_type
        field = label.find_element(By.XPATH, "following::*[self::input or self::textarea][1]")
        if not field.is_displayed() or field.get_attribute("value"):
            continue  # hidden, or already filled (e.g. Uploaded At)
        field_id = field.get_attribute("id") or ""
        if "date" in field_id or "expires" in field_id:
            driver.execute_script("arguments[0].value = arguments[1];", field, datetime.now().strftime("%Y-%m-%d"))
        elif (field.get_attribute("type") or "").lower() == "number":
            field.send_keys(run_id + str(i))
        else:
            field.send_keys(f"AUTO_{run_id}_{i}")  # unique value for every field


def pick_required_dropdowns(panel, driver):
    """Required drop-downs (e.g. Checker) that still say 'Nothing selected': pick the first real option."""
    xpath = ".//label[contains(., '*')]/following-sibling::div[contains(@class, 'bootstrap-select')][1]/button[contains(@class, 'bs-placeholder') and not(@data-id='DocumentType')]"
    for button in panel.find_elements(By.XPATH, xpath):
        if not button.is_displayed():
            continue  # e.g. the hidden Document Type drop-down
        driver.execute_script("arguments[0].click();", button)
        time.sleep(1)
        options = button.find_elements(By.XPATH, "../div[contains(@class, 'dropdown-menu')]//li[not(contains(@class, 'disabled'))]/a")
        driver.execute_script("arguments[0].click();", options[0])


def wait_for_message(driver, text_before):
    """Wait for a new success or error word on the page. Returns (True/False, message text)."""
    def new_word(d):
        texts = [e.text.lower() for e in d.find_elements(By.CSS_SELECTOR, MESSAGE_BOX) if e.is_displayed() and e.text.strip()]
        texts.append(body_text(d))
        for text in texts:
            for word in SUCCESS_WORDS + ERROR_WORDS:
                if word in text and word not in text_before:
                    return word
        return None

    word = WebDriverWait(driver, 20).until(new_word)
    boxes = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, MESSAGE_BOX) if e.is_displayed() and e.text.strip()]
    return word in SUCCESS_WORDS, (boxes[0] if boxes else word)


def xpath_text(text):
    """Quote a text for XPath (file names can contain ' characters)."""
    if "'" not in text:
        return f"'{text}'"
    return "concat('" + text.replace("'", "', \"'\", '") + "')"


def popup_text(driver):
    boxes = [e.text.strip() for e in driver.find_elements(By.CSS_SELECTOR, MESSAGE_BOX) if e.is_displayed() and e.text.strip()]
    return " | ".join(boxes)


def short(error):
    return f"{type(error).__name__}: {str(error).splitlines()[0][:120]}"


def fail(driver, ext, message):
    shown = popup_text(driver)
    if shown:
        message += f" - page said: {shown}"
    c.save_shot(driver, TEST_CASE_ID, ext, "FAIL")
    with open(f"debug/{TEST_CASE_ID}_{ext}.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    return False, message


def upload_document(driver, wait, ext):
    """Returns (True/False, message)."""
    sample = c.find_sample_file(ext)
    if not sample:
        return False, "sample file missing"
    file_name, path = sample

    # 1. attach the file (it goes to the Pending Files list)
    driver.get(ATTACH_URL)
    wait.until(EC.presence_of_element_located(FILE_INPUT)).send_keys(path)
    time.sleep(3)

    # 2. click the paperclip icon of the file in the Pending Files list
    driver.get(PENDING_URL)
    try:
        wait.until(EC.presence_of_element_located((By.ID, "list_view_container")))
        clear_selected_files(driver)
        icon = wait.until(EC.element_to_be_clickable(pending_row_icon(file_name)))
        icon.click()
        time.sleep(1)
    except Exception as error:
        names = [r.get_attribute("data-pending-doc-name") for r in driver.find_elements(By.CSS_SELECTOR, "#list_view_container tr.pending-meta")]
        print(f"   looked for '{file_name}' -> {type(error).__name__}. Pending list has {len(names)} files: {names[:6]}")
        return fail(driver, ext, f"'{file_name}' not found in Pending Files list")

    # 3. document type + required meta-data
    try:
        select_document_type(driver, wait)
        run_id = datetime.now().strftime("%H%M%S")
        for attempt in range(3):
            try:  # the form can redraw itself after the document type is chosen, so look the fields up again
                panel = driver.find_element(*METADATA_PANEL)
                fill_required_fields(panel, driver, run_id)
                pick_required_dropdowns(panel, driver)
                break
            except StaleElementReferenceException:
                if attempt == 2:
                    raise
                time.sleep(2)
    except Exception as error:
        return fail(driver, ext, f"could not fill meta-data ({short(error)})")

    # 4. click Upload and check the confirmation message
    text_before = body_text(driver)
    try:
        driver.find_element(*UPLOAD_BTN).click()
        ok, message = wait_for_message(driver, text_before)
    except Exception:
        return fail(driver, ext, "no confirmation message after Upload")

    c.save_shot(driver, TEST_CASE_ID, ext, "PASS" if ok else "FAIL")
    return ok, message


def main():
    c.check_excel_ready(TEST_CASE_ID)

    driver = webdriver.Chrome()
    driver.maximize_window()
    wait = WebDriverWait(driver, 15)
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


if __name__ == "__main__":
    main()