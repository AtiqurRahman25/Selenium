"""
DMS-TC090
Metadata Uniqueness
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Double click on a doc-type
3. Click on "More" button
4. Click on "Uniqueness Check"
5. Add a single field as "unique"
System shouldn't allow to upload/edit document with same value on this field & gave proper error message.
"""
import re
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC090"
BUILDER = "doc_uniqueness_condition_builder"

# Choose a meta-data in a drop-down inside the rule builder (works for bootstrap-select too)
PICK_FIELD_JS = """
var names = arguments[0];
var root = document.getElementById(arguments[1]);
var selects = root ? root.querySelectorAll('select') : [];
for (var i = 0; i < selects.length; i++) {
    var s = selects[i];
    for (var j = 0; j < s.options.length; j++) {
        var text = s.options[j].text.trim().toLowerCase();
        var val = (s.options[j].value || '').trim().toLowerCase();
        for (var k = 0; k < names.length; k++) {
            if (names[k] && (val === names[k] || text === names[k] || text.indexOf(names[k]) !== -1)) {
                s.value = s.options[j].value;
                if (window.$) {
                    $(s).trigger('change');
                    if ($.fn.selectpicker) { $(s).selectpicker('refresh'); }
                } else {
                    s.dispatchEvent(new Event('change', {bubbles: true}));
                }
                return true;
            }
        }
    }
}
return false;
"""


def open_uniqueness_modal(driver, wait):
    """More > Uniqueness Check, wait until the modal is open and the rule builder is filled."""
    d._click_more_menu_item(driver, wait, "doc_uniqueness_btn")
    wait.until(EC.visibility_of_element_located((By.ID, "doc_uniqueness_modal")))
    wait.until(lambda drv: drv.find_elements(By.CSS_SELECTOR, f"#{BUILDER} select"))


def mark_unique(driver, display):
    """Pick this meta-data (by display name or name) in the rule builder."""
    names = [display.lower(), re.sub(r"[^a-zA-Z0-9_]", "_", display.lower()).strip("_")]
    if not driver.execute_script(PICK_FIELD_JS, names, BUILDER):
        raise c.SetupError(f"field '{display}' was not found in the uniqueness builder")


def unique_doc_type(driver, wait):
    """Create a doc-type with a text meta-data field, set Uniqueness Check on it, and publish the doc-type."""
    doc_type = d.new_doc_type(driver, wait)
    field = d.new_metadata(driver, wait, doc_type, "One")

    open_uniqueness_modal(driver, wait)
    mark_unique(driver, field)
    save = driver.find_element(By.ID, "doc_uniqueness_save")
    ok, message = c.message_after(driver, lambda: c.click(driver, save))
    if not ok:
        raise c.SetupError(f"uniqueness check could not be saved ({message})")

    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, doc_type)
    c.message_after(driver, lambda: d._click_more_menu_item(driver, wait, "pub_per"))
    return doc_type, field


def upload_values(driver, wait, doc_type, values):
    """Upload a document with these meta-data values. Returns (True/False, message)."""
    c.prepare_upload(driver, wait, "pdf", doc_type)
    for label, value in values.items():
        c.fill_field(driver, label, value)
    c.set_document_name(driver, datetime.now().strftime("AUTO_%H%M%S%f"))
    return c.message_after(driver, lambda: c.click(driver, driver.find_element(*c.UPLOAD_BTN)))


def single_field(driver, wait):
    doc_type, field = unique_doc_type(driver, wait)
    value = datetime.now().strftime("AUTO_U%H%M%S")
    ok, message = upload_values(driver, wait, doc_type, {field: value})
    if not ok:
        raise c.SetupError(f"first document did not upload ({message})")
    ok, message = upload_values(driver, wait, doc_type, {field: value})
    return (not ok), f"Second document with the same '{field}' value " + (
        f"was rejected: {message}" if not ok else f"was accepted: {message}"
    )


SCENARIOS = [("Single unique field", single_field)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()