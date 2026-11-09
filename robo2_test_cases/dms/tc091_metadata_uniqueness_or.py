"""
DMS-TC091
Metadata Uniqueness
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Double click on a doc-type
3. Click on "More" button
4. Click on "Uniqueness Check"
5. Add multiple field as "unique" & separating them with "OR"
System shouldn't allow to upload/edit document with same value on any of these fields & gave proper error message.
Notes: Only allowed to upload/edit if all of these fields value are unique
"""
import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import common as c
import dms_helper as d
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC091"
BUILDER = "doc_uniqueness_condition_builder"

# Choose a meta-data in a drop-down of the rule builder. Drop-downs that already hold an earlier field are skipped,
# so the second call fills the new row instead of changing the first one.
PICK_FIELD_JS = """
var names = arguments[0];
var used = arguments[1];
var root = document.getElementById(arguments[2]);
var selects = root ? root.querySelectorAll('select') : [];
function matches(opt, list) {
    var text = opt.text.trim().toLowerCase();
    var val = (opt.value || '').trim().toLowerCase();
    for (var k = 0; k < list.length; k++) {
        if (list[k] && (val === list[k] || text === list[k] || text.indexOf(list[k]) !== -1)) { return true; }
    }
    return false;
}
function fire(s) {
    if (window.$) {
        $(s).trigger('change');
        if ($.fn.selectpicker) { $(s).selectpicker('refresh'); }
    } else {
        s.dispatchEvent(new Event('change', {bubbles: true}));
    }
}
for (var i = 0; i < selects.length; i++) {
    var s = selects[i];
    var current = s.options[s.selectedIndex];
    if (current && matches(current, used)) { continue; }
    for (var j = 0; j < s.options.length; j++) {
        if (matches(s.options[j], names)) {
            s.value = s.options[j].value;
            fire(s);
            return true;
        }
    }
}
return false;
"""

# Set an and / or drop-down in the rule builder, if the builder has one
SET_OPERATOR_JS = """
var want = arguments[0];
var root = document.getElementById(arguments[1]);
var selects = root ? root.querySelectorAll('select') : [];
for (var i = 0; i < selects.length; i++) {
    var s = selects[i];
    for (var j = 0; j < s.options.length; j++) {
        if (s.options[j].text.trim().toLowerCase() === want) {
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
return false;
"""


def dump_modal(driver):
    """Save a screenshot and the modal HTML next to the script, to see what the builder looks like."""
    driver.save_screenshot("uniqueness_modal.png")
    html = driver.execute_script(
        "var m = document.getElementById('doc_uniqueness_modal'); return m ? m.outerHTML : '';")
    with open("uniqueness_modal.html", "w", encoding="utf-8") as f:
        f.write(html)


def open_uniqueness_modal(driver, wait):
    """More > Uniqueness Check, wait until the modal is open and the rule builder is filled."""
    d._click_more_menu_item(driver, wait, "doc_uniqueness_btn")
    wait.until(EC.visibility_of_element_located((By.ID, "doc_uniqueness_modal")))
    wait.until(lambda drv: drv.find_elements(By.CSS_SELECTOR, f"#{BUILDER} select"))


def field_names(display):
    return [display.lower(), re.sub(r"[^a-zA-Z0-9_]", "_", display.lower()).strip("_")]


def mark_unique(driver, display, used=()):
    """Pick this meta-data (by display name or name) in the rule builder."""
    used_names = [name for field in used for name in field_names(field)]
    if not driver.execute_script(PICK_FIELD_JS, field_names(display), used_names, BUILDER):
        raise c.SetupError(f"field '{display}' was not found in the uniqueness builder")


def add_operator(driver, operator):
    """Put the operator (and / or) between two fields: click an 'or' button, or add a row and set the drop-down."""
    parts = f"#{BUILDER} button, #{BUILDER} a, #{BUILDER} label, #{BUILDER} li, #{BUILDER} span"
    for item in c.visible(driver, parts):
        if item.text.strip().lower() == operator:
            c.click(driver, item)
            time.sleep(1)
            return
    for item in c.visible(driver, f"#{BUILDER} button, #{BUILDER} a"):
        if re.search(r"add|\+", item.text.lower() + " " + (item.get_attribute("class") or "").lower()):
            c.click(driver, item)
            time.sleep(1)
            break
    driver.execute_script(SET_OPERATOR_JS, operator, BUILDER)


def unique_doc_type(driver, wait, operator):
    """Doc-type with two text meta-data, Uniqueness Check on both fields with this operator, then publish."""
    doc_type = d.new_doc_type(driver, wait)
    first = d.new_metadata(driver, wait, doc_type, "One")
    second = d.new_metadata(driver, wait, doc_type, "Two")

    try:
        open_uniqueness_modal(driver, wait)
        mark_unique(driver, first)
        add_operator(driver, operator)
        mark_unique(driver, second, used=[first])
        save = driver.find_element(By.ID, "doc_uniqueness_save")
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except Exception as error:
        dump_modal(driver)
        raise c.SetupError(
            f"uniqueness check setup failed ({type(error).__name__}: {error}). "
            "Saved uniqueness_modal.html and uniqueness_modal.png")
    if not ok:
        raise c.SetupError(f"uniqueness check could not be saved ({message})")

    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, doc_type)
    c.message_after(driver, lambda: d._click_more_menu_item(driver, wait, "pub_per"))
    return doc_type, first, second


def upload_values(driver, wait, doc_type, values):
    """Upload a document with these meta-data values. Returns (True/False, message)."""
    c.prepare_upload(driver, wait, "pdf", doc_type)
    for label, value in values.items():
        c.fill_field(driver, label, value)
    c.set_document_name(driver, datetime.now().strftime("AUTO_%H%M%S%f"))
    return c.message_after(driver, lambda: c.click(driver, driver.find_element(*h.UPLOAD_BTN)))


def unique_or(driver, wait):
    doc_type, first, second = unique_doc_type(driver, wait, "or")
    run_id = datetime.now().strftime("%H%M%S")
    ok, message = upload_values(driver, wait, doc_type, {first: f"AUTO_A{run_id}", second: f"AUTO_B{run_id}"})
    if not ok:
        raise c.SetupError(f"first document did not upload ({message})")
    same_one, msg_one = upload_values(driver, wait, doc_type, {first: f"AUTO_A{run_id}", second: f"AUTO_C{run_id}"})
    all_new, msg_new = upload_values(driver, wait, doc_type, {first: f"AUTO_D{run_id}", second: f"AUTO_E{run_id}"})
    ok = (not same_one) and all_new
    return ok, (f"Same value in one field: {'rejected' if not same_one else 'ACCEPTED'} ({msg_one}). "
                f"All values new: {'accepted' if all_new else 'REJECTED'} ({msg_new})")


SCENARIOS = [("Unique fields with OR", unique_or)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()