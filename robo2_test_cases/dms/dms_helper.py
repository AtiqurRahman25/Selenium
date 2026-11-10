"""
Feature helpers for the DMS test scripts: watermark window, My Documents list and sorting, Categorization,
Master Table Method, Bulk Upload, saved search and maker / checker review.
The shared basics (login, Excel, upload a test document, click by label, run a test case) are in common.py.
Keep this file in the same folder as common.py.
"""
import os
import re
import shutil
import tempfile
import time
from datetime import datetime

from selenium.common.exceptions import NoAlertPresentException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import tc011_Multiple_Doc_Up_helper as h


# categorization
def select_tree_item(driver, wait, name):
    """Select a category, doc-type, or metadata row in #all_doc_list (or tree)."""
    time.sleep(1.5)
    q = c.xpath_text(name)

    def find_row(drv):
        # 1. Match the table row in #all_doc_list first (clicking the <tr> triggers row selection)
        rows = [
            r for r in drv.find_elements(By.XPATH, f"//table[@id='all_doc_list']//tbody//tr[contains(., {q})]")
            if r.is_displayed()
        ]
        if rows:
            return rows[0]
        # 2. Fallback to any matching label/cell
        return c.find_by_label(drv, name, slack=60)

    row = WebDriverWait(driver, 10).until(find_row)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", row)
    # Click the first <td> cell inside the row so DataTables/jQuery marks the row as selected
    cells = row.find_elements(By.TAG_NAME, "td")
    target = cells[0] if cells else row
    try:
        ActionChains(driver).move_to_element(target).click().perform()
    except Exception:
        c.click(driver, target)
    time.sleep(1)
    return row


def _click_more_menu_item(driver, wait, item_id_or_label):
    """Open the #more_btn dropdown if needed and click #delete_btn / #update_btn (or by label)."""
    more_btns = c.visible(driver, "#more_btn")
    if more_btns:
        menu = driver.find_elements(By.ID, "more_btn_dropdown")
        if not menu or not menu[0].is_displayed():
            c.click(driver, more_btns[0])
            time.sleep(0.5)
    by_id = c.visible(driver, f"#{item_id_or_label}")
    if by_id:
        c.click(driver, by_id[0])
        return
    c.click_label(driver, wait, item_id_or_label)


def create_category(driver, wait, name, kind="doc-type", parent=None):
    """Categorization page: Add, choose Category / Document, type the name, Save. Returns (True/False, message)."""
    driver.get(c.ROOT_URL)
    time.sleep(2)
    if parent:
        select_tree_item(driver, wait, parent)
        c.double_click_label(driver, wait, parent)
        time.sleep(1.5)

    add_btns = c.visible(driver, "#add_btn")
    if add_btns:
        c.click(driver, add_btns[0])
    else:
        c.click_label(driver, wait, "add")
    time.sleep(1)

    # Select 'Document' (for doc-type) or 'Category' in the bootstrap-select dropdown (#parent_cat_doc_field / #cat_doc_field)
    wanted_val = "doc" if "doc" in kind.lower() else "cat"
    wanted_txt = "Document" if wanted_val == "doc" else "Category"
    driver.execute_script(
        """
        var val = arguments[0];
        $('select[name="type"]:visible, #parent_cat_doc_field, #cat_doc_field').each(function() {
            $(this).val(val).trigger('change');
            if ($.fn.selectpicker) { $(this).selectpicker('refresh'); }
        });
        """,
        wanted_val,
    )
    try:
        toggle = c.visible(driver, ".modal.in button.dropdown-toggle, .modal.show button.dropdown-toggle")
        if toggle and wanted_txt.lower() not in (toggle[0].get_attribute("title") or "").lower():
            c.click(driver, toggle[0])
            time.sleep(0.5)
            opt = [
                a for a in c.visible(driver, ".modal.in .dropdown-menu.open li a, .modal.show .dropdown-menu.open li a")
                if wanted_txt.lower() in a.text.lower()
            ]
            if opt:
                c.click(driver, opt[0])
                time.sleep(0.5)
    except Exception:
        pass

    box = WebDriverWait(driver, 10).until(lambda drv: c.modal_text_input(drv) or c.find_field(drv, "name"))
    box.clear()
    box.send_keys(name)
    return c.do(driver, wait, "save")


def new_doc_type(driver, wait, parent=None):
    """Create a doc-type with a unique name. Returns its name, or raises SetupError."""
    name = datetime.now().strftime("AUTO_DT_%H%M%S")
    ok, message = create_category(driver, wait, name, "doc-type", parent)
    if not ok:
        raise c.SetupError(f"doc-type could not be created ({message})")
    return name


def input_with_value(driver, value):
    for box in c.visible(driver, "input"):
        if box.get_attribute("value") == value:
            return box
    return None


def delete_category(driver, wait, name):
    """Select the category/doc-type row on /dms/document/root, open More -> Delete, and confirm."""
    driver.get(c.ROOT_URL)
    time.sleep(2)
    select_tree_item(driver, wait, name)

    def action():
        _click_more_menu_item(driver, wait, "delete_btn")
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    return c.message_after(driver, action)


def next_metadata_order(driver):
    """Next free Order number: highest Order in the doc-type's meta-data list + 1 (1 when the list is empty)."""
    used = []
    for row in driver.find_elements(By.CSS_SELECTOR, "tr.clickie[data-type='meta']"):
        cells = row.find_elements(By.TAG_NAME, "td")
        # list columns: Title, Display Name, Order, Data Type, Unique, Required
        if len(cells) > 2 and cells[2].text.strip().isdigit():
            used.append(int(cells[2].text.strip()))
    return max(used) + 1 if used else 1


def set_metadata_order(driver, order):
    """Pick the Order value in the Add Meta field form (#meta_order, a bootstrap-select dropdown)."""
    driver.execute_script(
        """
        var s = document.getElementById('meta_order');
        s.value = arguments[0];
        if (window.$ && $.fn.selectpicker) { $(s).selectpicker('refresh'); }
        s.dispatchEvent(new Event('change', {bubbles: true}));
        """,
        str(order),
    )


def create_metadata(driver, wait, doc_type, display_name, data_type="String", order=None):
    """Double click the doc-type, click Add, fill Name / Display Name / Min / Max / Order, and Save.
    order=None uses the next free Order number, so a second meta-data never clashes with the first."""
    driver.get(c.ROOT_URL)
    time.sleep(2)
    row = select_tree_item(driver, wait, doc_type)
    # Double-click the row (or its first cell) to open the doc-type's metadata list
    cells = row.find_elements(By.TAG_NAME, "td")
    ActionChains(driver).double_click(cells[0] if cells else row).perform()
    time.sleep(2)

    # Orders already used by this doc-type (read before the Add form opens)
    if order is None:
        order = next_metadata_order(driver)

    add_btns = c.visible(driver, "#add_btn")
    if add_btns:
        c.click(driver, add_btns[0])
    else:
        c.click_label(driver, wait, "add")
    wait.until(EC.visibility_of_element_located((By.ID, "add_new_metafield")))
    time.sleep(1)

    # Map 'text' -> 'String' since #add_meta_type options are: Integer, Float, String, TextArea, Date, DropDown
    dtype_map = {"text": "String", "string": "String", "int": "Integer", "integer": "Integer", "textarea": "TextArea", "date": "Date", "float": "Float", "dropdown": "DropDown"}
    mapped_type = dtype_map.get(data_type.lower(), data_type)

    meta_name = re.sub(r"[^a-zA-Z0-9_]", "_", display_name.lower()).strip("_")
    c.fill_field(driver, "name", meta_name)
    c.fill_field(driver, "display name", display_name)

    try:
        c.pick_option(driver, "data type", mapped_type)
        time.sleep(0.5)
    except Exception:
        pass

    # Order must be unique inside the doc-type
    set_metadata_order(driver, order)

    # If Minimum and Maximum fields are visible (mandatory for String/Integer/Float), fill them!
    for fid, val in (("min_field", "1"), ("max_field", "50")):
        boxes = c.visible(driver, f"#{fid}")
        if boxes and not boxes[0].get_attribute("value"):
            boxes[0].clear()
            boxes[0].send_keys(val)

    save_btns = c.visible(driver, "#save_metafield")
    return c.message_after(driver, lambda: c.click(driver, save_btns[0])) if save_btns else c.do(driver, wait, "save")


def new_metadata(driver, wait, doc_type, label="Meta", order=None):
    display = datetime.now().strftime(f"AUTO {label} %H%M%S")
    ok, message = create_metadata(driver, wait, doc_type, display, order=order)
    if not ok:
        raise c.SetupError(f"meta-data could not be created ({message})")
    return display


# master table method
MTM_FORM = "#mtm_creation_main_form"

# Choose an option in a (bootstrap-select) drop-down: by option text or value, or the first real option
PICK_OPTION_JS = """
var s = document.querySelector(arguments[0]);
if (!s) { return ''; }
var want = (arguments[1] || '').toLowerCase();
var chosen = null;
for (var i = 0; i < s.options.length; i++) {
    var o = s.options[i];
    if (o.disabled || !o.value) { continue; }
    if (!want || o.text.trim().toLowerCase() === want || o.value.toLowerCase() === want) { chosen = o; break; }
}
if (!chosen) { return ''; }
s.value = chosen.value;
if (window.$) {
    $(s).trigger('change');
    if ($.fn.selectpicker) { $(s).selectpicker('refresh'); }
} else {
    s.dispatchEvent(new Event('change', {bubbles: true}));
}
return chosen.text.trim();
"""


# Names of the master tables in the drop-down of the method form
LIST_MASTER_TABLES_JS = """
return Array.from(document.querySelectorAll(arguments[0] + ' select[name="master_table"] option'))
    .filter(function(o) { return o.value && !o.disabled; })
    .map(function(o) { return o.text.trim(); });
"""


def mtm_choose(driver, name, want=None, seconds=10):
    """Choose an option of a drop-down of the method form. Waits, because some lists are filled after another pick."""
    css = f'{MTM_FORM} select[name="{name}"]'
    try:
        return WebDriverWait(driver, seconds, poll_frequency=0.5).until(
            lambda drv: drv.execute_script(PICK_OPTION_JS, css, want or ""))
    except TimeoutException:
        raise c.SetupError(f"the '{name}' drop-down of the method form has no option" + (f" '{want}'" if want else ""))


def mtm_field_visible(driver, name):
    return driver.execute_script(
        "var s = document.querySelector(arguments[0]); var box = s && s.closest('.col-container'); "
        "return !!box && box.offsetParent !== null;", f'{MTM_FORM} select[name="{name}"]')


def mtm_pick_master_table(driver):
    """Master Table: MTM_MASTER_TABLE from .env, or the first master table that has fields to match on."""
    wanted = os.getenv("MTM_MASTER_TABLE")
    if wanted:
        return mtm_choose(driver, "master_table", wanted)
    names = driver.execute_script(LIST_MASTER_TABLES_JS, MTM_FORM)
    for name in names[:15]:
        mtm_choose(driver, "master_table", name)
        try:
            mtm_choose(driver, "mtm_match_criteria_mt_field", seconds=4)  # the fields load after the table is chosen
            return name
        except c.SetupError:
            continue
    raise c.SetupError("no master table with fields was found for the method")


def mtm_pick_doc_type(driver, wait, term):
    """Document Type (Select2 search): type the name and click the matching result."""
    box = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f"{MTM_FORM} .method_form_document_type-container span.select2-selection")))
    c.click(driver, box)
    search = wait.until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, ".select2-container--open input.select2-search__field")))
    search.click()
    typed = term.strip().strip("/").split("/")[-1]
    for letter in typed[:30]:
        search.send_keys(letter)
        time.sleep(0.2)
    option_css = ".select2-container--open .select2-results__option"
    WebDriverWait(driver, 15).until(lambda drv: bool(c.select2_options(drv, option_css)))
    time.sleep(1.5)
    options = c.select2_options(driver, option_css)
    ActionChains(driver).move_to_element(options[c.best_option_index(options, term)]).click().perform()
    time.sleep(1)
    shown = driver.find_element(
        By.CSS_SELECTOR, f"{MTM_FORM} .method_form_document_type-container .select2-selection__rendered").text.lower()
    if not shown.strip() or "select document type" in shown:
        raise c.SetupError(f"document type '{typed}' could not be selected in the method form")


def form_problems(driver):
    """Validation messages shown on the page."""
    boxes = c.visible(driver, ".parsley-errors-list li, .parsley-custom-error-message, .validation-error-message")
    return " | ".join(box.text.strip() for box in boxes if box.text.strip())


def create_method(driver, wait, record_type="multiple record"):
    """Add Method: fill the method form (title, master table, document type, output type, match criteria,
    populate field) and Save. Returns (True/False, message, method name).
    .env (optional): MTM_DOC_TYPE (default 'aa', needs a drop-down meta-data field), MTM_MASTER_TABLE."""
    driver.get(c.MASTER_TABLE_URL)
    time.sleep(2)
    add_buttons = c.visible(driver, "#dms_method_add")
    if add_buttons:
        c.click(driver, add_buttons[0])
    else:
        c.click_label(driver, wait, "add method")
    wait.until(EC.visibility_of_element_located((By.ID, "mtm_creation_main_form")))
    time.sleep(1)

    name = datetime.now().strftime("AUTO_MT_%H%M%S")
    driver.find_element(By.CSS_SELECTOR, f'{MTM_FORM} input[name="method_name"]').send_keys(name)
    try:
        mtm_pick_master_table(driver)
        mtm_pick_doc_type(driver, wait, os.getenv("MTM_DOC_TYPE", "aa"))
        mtm_choose(driver, "mtm_output_type", "multiple" if "multiple" in record_type.lower() else "single")
        time.sleep(1)
        for field in ("mtm_fetch_all_record", "mtm_unique_fetch_record"):
            if mtm_field_visible(driver, field):
                mtm_choose(driver, field, "false")
        # match criteria: table field, operator, value type = meta data field, and the meta data field
        mtm_choose(driver, "mtm_match_criteria_mt_field")
        mtm_choose(driver, "mtm_match_criteria_operator")
        mtm_choose(driver, "mtm_match_criteria_value_type", "meta_data_field")
        mtm_choose(driver, "mtm_match_criteria_metadata_field")
        # populate field: table field -> meta data field
        mtm_choose(driver, "mtm_populate_mt_field")
        mtm_choose(driver, "mtm_populate_metadata_field")
        save = driver.find_element(By.ID, "save_mtm_dms")
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not saved. The form says: {form_problems(driver) or 'nothing'}")
    return ok, message, name


def new_method(driver, wait, record_type="multiple record"):
    ok, message, name = create_method(driver, wait, record_type)
    if not ok:
        raise c.SetupError(f"master table method could not be created ({message})")
    return name


def update_method(driver, wait, name, new_name):
    """Method list: click Edit on the method's card, change the Method Title, Save. Returns (True/False, message)."""
    card_xpath = (f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
                  f" and .//span[@title={c.xpath_text(name)}]]")
    try:
        card = WebDriverWait(driver, 10).until(lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None))
        c.click(driver, card.find_element(By.CSS_SELECTOR, "a.mtm_edit_button"))
        wait.until(EC.visibility_of_element_located((By.ID, "mtm_creation_main_form")))
        title = driver.find_element(By.CSS_SELECTOR, f'{MTM_FORM} input[name="method_name"]')
        # the saved values are filled in by JavaScript: wait for the title and for the last populate drop-down
        WebDriverWait(driver, 15).until(lambda drv: title.get_attribute("value") == name)
        WebDriverWait(driver, 15).until(lambda drv: drv.execute_script(
            "var s = document.querySelector(arguments[0]); return !!s && !!s.value;",
            f'{MTM_FORM} select[name="mtm_populate_metadata_field"]'))
    except TimeoutException:
        raise c.SetupError(f"the edit form of method '{name}' did not open or fill in")
    title.clear()
    title.send_keys(new_name)
    try:
        save = driver.find_element(By.ID, "save_mtm_dms")
        ok, message = c.message_after(driver, lambda: c.click(driver, save))
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not updated. The form says: {form_problems(driver) or 'nothing'}")
    listed = c.wait_text(driver, new_name, 8)
    return ok and listed, message + ("" if listed else f". '{new_name}' is not in the method list")


def delete_method(driver, wait, name):
    """Method list: open the card's settings (gear icon) if Delete is hidden, click Delete, confirm Yes.
    Returns (True/False, message). True when the system confirms and the method is gone from the list."""
    card_xpath = (f"//div[contains(concat(' ', normalize-space(@class), ' '), ' mtm-list-card ')"
                  f" and .//span[@title={c.xpath_text(name)}]]")
    try:
        card = WebDriverWait(driver, 10).until(lambda drv: next(iter(drv.find_elements(By.XPATH, card_xpath)), None))
        button = card.find_element(By.CSS_SELECTOR, "button.mtm_delete_button")
        if not button.is_displayed():
            c.click(driver, card.find_element(By.CSS_SELECTOR, "a.mtm_setting_button"))
            time.sleep(1)
    except TimeoutException:
        raise c.SetupError(f"method '{name}' was not found in the method list")

    def action():
        c.click(driver, button)
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    ok, message = c.message_after(driver, action)
    try:
        WebDriverWait(driver, 8).until(lambda drv: not drv.find_elements(By.XPATH, card_xpath))
        gone = True
    except TimeoutException:
        gone = False
    return ok and gone, message + (". Method removed from the list" if gone else ". Method still shown in the list")


# My Documents (explorer)
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}|\d{1,2}[-/ ][A-Za-z]{3}[-/ ,]+\d{4}|\d{1,2}/\d{1,2}/\d{4}")

DATE_FORMATS = ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%d/%m/%Y", "%d-%b, %Y", "%d %b, %Y", "%b %d, %Y")

SORT_LABELS = {
    ("name", False): ("name ascending", "name asc", "name (a-z)", "a-z"),
    ("name", True): ("name descending", "name desc", "name (z-a)", "z-a"),
    ("date", False): ("date ascending", "date asc", "oldest"),
    ("date", True): ("date descending", "date desc", "newest", "latest"),
}


def parse_date(text):
    match = DATE_PATTERN.search(text or "")
    if not match:
        return None
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(match.group(0).strip(), date_format)
        except ValueError:
            continue
    return None


def open_doc_type_in_explorer(driver, wait, doc_type):
    driver.get(c.EXPLORER_URL)
    c.click_label(driver, wait, doc_type)
    time.sleep(3)
    if not explorer_items(driver):
        c.double_click_label(driver, wait, doc_type)  # some trees open on double click
        time.sleep(3)


def explorer_items(driver):
    """(name, date text) of every document row shown in My Documents."""
    items = []
    for row in c.visible(driver, "table tbody tr, .list-group-item"):
        lines = [line.strip() for line in row.text.split("\n") if line.strip()]
        names = [line for line in lines if not DATE_PATTERN.search(line) and re.search(r"[A-Za-z]", line)]
        if names:
            items.append((names[0], row.text))
    return items


def explorer_pages(driver, pages=3):
    """Document rows of the first pages (clicks the next page button)."""
    items = []
    for _ in range(pages):
        items += explorer_items(driver)
        buttons = [b for b in c.visible(driver, "#pagination button.next") if b.is_enabled()]
        if not buttons:
            break
        before = h.body_text(driver)
        c.click(driver, buttons[0])
        time.sleep(2)
        if h.body_text(driver) == before:
            break
    return items


def choose_sort(driver, wait, key, descending):
    c.click_label(driver, wait, "sort")
    for label in SORT_LABELS[(key, descending)]:
        if c.find_by_label(driver, label):
            c.click_label(driver, wait, label)
            time.sleep(3)
            return
    raise Exception(f"sort option for {key} {'descending' if descending else 'ascending'} not found")


def check_sorting(items, key, descending):
    """Returns (True/False, text). key is 'name' or 'date'."""
    if len(items) < 2:
        return False, f"only {len(items)} documents shown, need at least 2"
    if key == "name":
        values = [name.lower() for name, _ in items]
    else:
        values = [parse_date(text) for _, text in items]
        if None in values:
            return False, "could not read the dates of the documents"
    ok = values == sorted(values, reverse=descending)
    return ok, f"{len(items)} documents checked over {'all shown pages' if len(items) > 10 else 'the page'}"


# watermark (Pending Documents page)
def open_watermark_modal(driver, wait):
    modal = driver.find_element(By.ID, "add_watermark_modal")
    if not modal.is_displayed():
        c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "add_watermark_button"))))
        wait.until(EC.visibility_of_element_located((By.ID, "add_watermark_modal")))
        time.sleep(1)


def open_watermark_tab(driver, wait, tab_id):
    open_watermark_modal(driver, wait)
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, tab_id))))
    time.sleep(1)


def create_text_watermark(driver, wait, text):
    """Custom Text tab: type the text (max 20 characters) and click Create. Returns (True/False, message)."""
    open_watermark_tab(driver, wait, "watermark_custom_text_tab")
    box = wait.until(EC.visibility_of_element_located((By.ID, "watermark_text")))
    box.clear()
    box.send_keys(text)
    button = wait.until(EC.element_to_be_clickable((By.ID, "create_custom_text_watermark_button")))
    return c.message_after(driver, lambda: c.click(driver, button))


# bulk upload
def pick_bulk_doc_type(driver, wait, term):
    """Bulk upload page: open the Document Type drop-down, type the doc-type name, pick the matching result."""
    driver.get(c.BULK_URL)
    select_id = "document_type_bulk_upload"
    box = wait.until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, f"span.select2-selection[aria-labelledby='select2-{select_id}-container']")))
    c.click(driver, box)
    search = wait.until(EC.visibility_of_element_located((
        By.XPATH,
        f"//ul[@id='select2-{select_id}-results']/ancestor::span[contains(@class, 'select2-dropdown')]"
        "//input[contains(@class, 'select2-search__field')]")))
    search.click()  # give the search box focus, so the typing reaches it
    typed = term.strip().strip("/").split("/")[-1]
    for letter in typed[:30]:
        search.send_keys(letter)
        time.sleep(0.2)

    option_css = f"#select2-{select_id}-results .select2-results__option"
    WebDriverWait(driver, 15).until(lambda drv: bool(c.select2_options(drv, option_css)))
    time.sleep(1.5)
    options = c.select2_options(driver, option_css)
    option = options[c.best_option_index(options, term)]
    ActionChains(driver).move_to_element(option).click().perform()
    time.sleep(1)

    shown = driver.find_element(By.ID, f"select2-{select_id}-container").text.lower()
    if not shown.strip() or "search for" in shown:
        raise c.SetupError(f"doc-type '{typed}' could not be selected for bulk upload")


def wait_new_download(before, started, seconds=30):
    """Newest finished file in DOWNLOAD_DIR that is new, or was written again (same name) since `started`."""
    end = time.time() + seconds
    while time.time() < end:
        found = []
        for name in os.listdir(c.DOWNLOAD_DIR):
            if name.endswith((".crdownload", ".tmp")):
                continue
            path = os.path.join(c.DOWNLOAD_DIR, name)
            if name not in before or os.path.getmtime(path) >= started - 1:
                found.append((os.path.getmtime(path), path))
        if found:
            return max(found)[1]
        time.sleep(1)
    return None


def download_template(driver, wait, term):
    """Bulk upload page: pick the doc-type, click Download template. Returns the downloaded file path."""
    pick_bulk_doc_type(driver, wait, term)
    # the download section is hidden until a doc-type is chosen, then filled by JavaScript
    wait.until(lambda drv: drv.find_element(By.ID, "download_template_section").is_displayed()
               and drv.find_element(By.ID, "download_template_section").get_attribute("innerHTML").strip())
    time.sleep(1)  # let the page attach its click handler to the link
    before = set(os.listdir(c.DOWNLOAD_DIR))
    for _ in range(2):  # click again once if nothing was downloaded
        started = time.time()
        buttons = c.visible(driver, "#download_template_section a, #download_template_section button, "
                                    "#download_template_section .btn")
        if buttons:
            c.click(driver, buttons[0])
        else:
            c.click_label(driver, wait, "download")
        path = wait_new_download(before, started, seconds=15)
        if path:
            return path
    raise Exception("template was not downloaded")


def template_header(path):
    import csv
    if not path.lower().endswith(".csv"):
        raise c.SetupError(f"the template is '{os.path.basename(path)}', this script reads CSV templates only")
    with open(path, newline="", encoding="utf-8-sig") as f:
        return next(csv.reader(f))


def write_csv(path, header, rows):
    import csv
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return path


def alert_message(driver, error=None):
    """Text of a JavaScript alert: from the exception when Selenium already closed it, or from the open alert."""
    text = getattr(error, "alert_text", None) or ""
    if not text:
        try:
            alert = driver.switch_to.alert
            text = alert.text
            alert.accept()
        except NoAlertPresentException:
            pass
    return (text or "").strip()


def bulk_submit(driver, wait, term, csv_path, files=()):
    """Pick the doc-type, attach the CSV, and start the upload.
    Returns (True/False, message): True when the upload went through, False when the page refused the file or
    reported errors. The message is what the page said (alert, popup, CSV data rows, Bulk Upload Report)."""
    pick_bulk_doc_type(driver, wait, term)
    # the CSV goes into #csv_file; #uploadable_files (last file input on the page) is for the documents
    csv_input = driver.find_element(By.ID, "csv_file")
    driver.execute_script("arguments[0].style.display='block'; arguments[0].style.visibility='visible';", csv_input)

    def section_shown(drv):
        return drv.find_element(By.ID, "csv_file_section").is_displayed()

    # the page either shows an alert / message, or reads the CSV and opens the "CSV File Data" section
    try:
        csv_input.send_keys(csv_path)
        time.sleep(1)
        alert = alert_message(driver)
        if alert:
            return False, f"alert: {alert}"
        WebDriverWait(driver, 10).until(lambda drv: section_shown(drv) or c.popup_text(drv))
    except UnexpectedAlertPresentException as error:
        return False, f"alert: {alert_message(driver, error)}"
    except TimeoutException:
        return False, "the CSV file was not accepted and the page showed no message"
    if not section_shown(driver):
        return False, c.popup_text(driver)

    if files:
        #uploadable_files picks a whole folder (it can not hold several files), so copy the files into one folder
        folder = tempfile.mkdtemp(prefix="AUTO_bulk_")
        for path in files:
            shutil.copy(path, folder)
        driver.find_element(By.ID, "uploadable_files").send_keys(folder)
        time.sleep(2)
    try:
        ok, message = c.message_after(driver, lambda: c.click(driver, driver.find_element(By.ID, "start_upload")))
    except UnexpectedAlertPresentException as error:
        ok, message = False, f"alert: {alert_message(driver, error)}"
    except TimeoutException:
        ok, message = False, c.popup_text(driver)
    rows = " ".join(driver.find_element(By.ID, "csv_file_data").text.split())
    report = " ".join(driver.find_element(By.ID, "download_report").text.split())
    text = " | ".join(part for part in (message, rows, report) if part)
    if re.search(r"error|fail|invalid|already|required", text.lower()):
        ok = False
    return ok, text


# saved search
def save_search(driver, wait, search_name, info):
    """Advanced search form: pick the doc type, give metadata, click Save Search, give the name, Save.
    `info` is the dict returned by c.upload_document()."""
    driver.get(c.EXPLORER_URL)
    if info["values"]:
        # doc type + metadata of the uploaded document (steps 2 and 3 of the test case)
        c.advanced_search(driver, wait, None, doc_type=info["doc_type"], extra=info["values"][:1], submit=False)
    else:
        # the doc type has no text meta-data: fall back to doc type + document name
        c.advanced_search(driver, wait, info["name"], doc_type=info["doc_type"], submit=False)

    def action():
        c.click(driver, driver.find_element(By.ID, "save_search_name"))
        name_box = WebDriverWait(driver, 10).until(lambda drv: c.modal_text_input(drv))
        name_box.send_keys(search_name)
        c.click_label(driver, wait, "save")
    return c.message_after(driver, action)


# maker / checker
def review_as_checker(driver, wait, name, action):
    """Second user opens Pending For Review and approves / rejects the document. Returns (True/False, message)."""
    def review():
        driver.get(c.REVIEW_URL)
        if not c.wait_text(driver, name, 10):
            return False, "document not listed for the checker"
        def click_action():
            c.click_near(driver, wait, name, action)
            box = c.modal_text_input(driver)
            if box is not None:
                box.send_keys("AUTO review")
            c.confirm_any(driver, wait)
        return c.message_after(driver, click_action)
    return c.as_other_user(driver, wait, review)