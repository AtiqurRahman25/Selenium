"""
Feature helpers for the DMS test scripts: watermark window, My Documents list and sorting, Categorization,
Master Table Method, Bulk Upload, saved search and maker / checker review.
The shared basics (login, Excel, upload a test document, click by label, run a test case) are in common.py.
Keep this file in the same folder as common.py.
"""
import os
import re
import time
from datetime import datetime

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import tc011_Multiple_Doc_Up_helper as h


# ---------- categorization ----------
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


# ---------- master table method ----------
def create_method(driver, wait, record_type="multiple record"):
    """Add Method icon: choose the record type, fill the required fields, Save. Returns (True/False, message, method name)."""
    driver.get(c.MASTER_TABLE_URL)
    c.click_label(driver, wait, "add method")
    time.sleep(2)
    try:
        c.click_label(driver, wait, record_type)
    except Exception:
        pass
    name = datetime.now().strftime("AUTO_MT_%H%M%S")
    modals = driver.find_elements(By.XPATH, c.MODAL)
    panel = modals[0] if modals else driver.find_element(By.TAG_NAME, "body")
    h.fill_required_fields(panel, driver, name[-6:])
    h.pick_required_dropdowns(panel, driver)
    for field in panel.find_elements(By.XPATH, ".//label[contains(., '*')]/following::select[1]"):
        if field.is_displayed():
            c.pick_option(driver, c.clean(field.find_element(By.XPATH, "preceding::label[1]").text))
    box = c.find_field(driver, "method name") or c.find_field(driver, "name")
    if box is not None:
        box.clear()
        box.send_keys(name)
    ok, message = c.do(driver, wait, "save")
    return ok, message, name


def new_method(driver, wait, record_type="multiple record"):
    ok, message, name = create_method(driver, wait, record_type)
    if not ok:
        raise c.SetupError(f"master table method could not be created ({message})")
    return name


# ---------- My Documents (explorer) ----------
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


# ---------- watermark (Pending Documents page) ----------
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


# ---------- bulk upload ----------
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


def download_template(driver, wait, term):
    """Bulk upload page: pick the doc-type, click Download template. Returns the downloaded file path."""
    pick_bulk_doc_type(driver, wait, term)
    # the download section is hidden until a doc-type is chosen, then filled by JavaScript
    wait.until(lambda drv: drv.find_element(By.ID, "download_template_section").is_displayed()
               and drv.find_element(By.ID, "download_template_section").get_attribute("innerHTML").strip())
    before = set(os.listdir(c.DOWNLOAD_DIR))
    buttons = c.visible(driver, "#download_template_section a, #download_template_section button, "
                                "#download_template_section .btn")
    if buttons:
        c.click(driver, buttons[0])
    else:
        c.click_label(driver, wait, "download")
    name = c.wait_for_download(before)
    if not name:
        raise Exception("template was not downloaded")
    return os.path.join(c.DOWNLOAD_DIR, name)


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


def bulk_submit(driver, wait, term, csv_path, files=()):
    """Pick the doc-type, attach the CSV (and files), click Upload. Returns (True/False, message)."""
    pick_bulk_doc_type(driver, wait, term)
    c.attach_to_file_input(driver, wait, csv_path)
    for path in files:
        c.attach_to_file_input(driver, wait, path)
    time.sleep(2)
    return c.do(driver, wait, "upload")


# ---------- saved search ----------
def save_search(driver, wait, search_name, doc_name):
    """Advanced search form: fill the document name, click Save Search, give the name, Save."""
    driver.get(c.EXPLORER_URL)
    c.click(driver, wait.until(EC.element_to_be_clickable(c.FILTER_BTN)))
    box = wait.until(EC.visibility_of_element_located((By.ID, "docname")))
    box.send_keys(doc_name)

    def action():
        c.click(driver, driver.find_element(By.ID, "save_search_name"))
        name_box = WebDriverWait(driver, 10).until(lambda drv: c.modal_text_input(drv))
        name_box.send_keys(search_name)
        c.click_label(driver, wait, "save")
    return c.message_after(driver, action)


# ---------- maker / checker ----------
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