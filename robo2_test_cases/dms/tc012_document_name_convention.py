"""
DMS-TC012	Document Name Convention	
"1. Go to https://ecmv6.robo2mation.com/dms/document/upload/standard_upload/filesave/pendingmetalist/
2. Attach a document (image, media or office file), select doc-type (which has document name convention), give all required meta-data value & give unique value to unique field.
3. Click on ""Save"" button"	
Document name should be auto selected with the combination of meta data as per configuration
"""
import re
import time
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC012"
DOC_TYPE = c.need_env("NAME_CONVENTION_DOC_TYPE", "(the doc-type that has a document name convention)")


def meta_values(driver):
    """Values typed into the meta-data boxes. Dates are skipped because the name may show them in another format."""
    for attempt in range(3):
        try:
            values = []
            panel = driver.find_element(*c.METADATA_PANEL)
            for field in panel.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='number'], textarea"):
                field_id = (field.get_attribute("id") or "").lower()
                value = field.get_attribute("value") or ""
                if (field.is_displayed() and value and field_id != "file_name"
                        and "date" not in field_id and "expires" not in field_id):
                    values.append(value)
            return values
        except StaleElementReferenceException:
            time.sleep(1)  # the form redraws itself while the name is built
    return []


def convention_of_selected_doc_type(driver):
    """The document name convention of the selected doc-type (e.g. 'raw_filename,_,name'), '' if it has none."""
    script = """
        try { var d = $('#DocumentType').select2('data')[0] || {};
              var c = d['data-convention'] || (d.element && d.element.dataset.convention) || d.document_name_convention || '';
              return Array.isArray(c) ? c.join(',') : String(c); }
        catch (e) { return ''; }"""
    value = (driver.execute_script(script) or "").strip()
    return "" if value.strip("[]'\" ,") in ("", "null", "undefined") else value


def convention_fields(convention):
    """Meta-data field names used in the convention (without the [x:y] slices, the separators and the built-in parts)."""
    names = []
    for part in convention.strip("[]'\" ").split(","):
        part = re.sub(r"\[\d+:\d+\]", "", part).strip()
        if part and part not in ("raw_filename", "upload_date", "_", "-") and re.search(r"[a-z]", part, re.I):
            names.append(part)
    return names


def fill_convention_fields(driver, fields):
    """Type a unique value into the empty meta-data text boxes the convention uses (even if they are not required)."""
    run_id = datetime.now().strftime("%H%M%S")
    for i, name in enumerate(fields):
        for box in driver.find_elements(By.CSS_SELECTOR, f".meta-data-gen-wrap [name='{name}']"):
            kind = (box.get_attribute("type") or "text").lower()
            if not box.is_displayed() or box.tag_name not in ("input", "textarea") or box.get_attribute("value"):
                continue
            if "date" in (box.get_attribute("class") or "") or kind == "date":
                continue  # dates are filled by fill_metadata_form when required
            box.send_keys(str(int(run_id) + i) if kind == "number" else f"AUTO{run_id}{i}")


def document_name_convention(driver, wait):
    # steps 1-2: attach a document, select the doc-type, fill the required meta-data (unique values)
    c.prepare_upload(driver, wait, "pdf", DOC_TYPE)
    selected = c.current_doc_type(driver)
    wanted = DOC_TYPE.strip().strip("/").split("/")[-1]
    if wanted.lower() != selected.lower():
        raise c.SetupError(f"doc-type '{DOC_TYPE}' was not selected (the page shows '{selected}')")

    convention = convention_of_selected_doc_type(driver)
    if not convention:
        raise c.SetupError(f"doc-type '{DOC_TYPE}' has no document name convention. Set NAME_CONVENTION_DOC_TYPE in .env "
                           f"to a doc-type that has one (full path like /Folder/Doc Type/ is best)")
    fill_convention_fields(driver, convention_fields(convention))

    # move the focus out of the last meta-data box so the name is built
    try:
        driver.find_element(By.ID, "file_name").click()
    except Exception:
        pass

    values = meta_values(driver)
    if not values:
        raise c.SetupError("no meta-data value was filled for this doc-type")

    # the name must be built from the meta-data values
    try:
        WebDriverWait(driver, 10).until(lambda d: any(v in c.field_value(d, "file_name") for v in values))
    except Exception:
        name = c.field_value(driver, "file_name")
        return False, f"Document name '{name}' does not contain the meta-data values {values} (convention {convention})"
    name = c.field_value(driver, "file_name")
    used = [v for v in values if v in name]

    # step 3: click Save and check the document is saved with that name
    ok, message = c.message_after(driver, lambda: c.click(driver, driver.find_element(*c.UPLOAD_BTN)))
    if not ok:
        return False, f"Document name was '{name}' but Save failed ({message})"
    if not c.search_finds(driver, wait, name, tries=5):
        return False, f"Document saved, but not found in search with the name '{name}'"

    return True, f"Document name auto-selected as '{name}' from meta-data {used} (convention {convention}); saved and found in search"


if __name__ == "__main__":
    c.run(TEST_CASE_ID, [("Document name convention", document_name_convention)])