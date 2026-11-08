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
    """Select a category or doc-type node in the Categorization tree (supports D3 SVG, jsTree, and HTML)."""
    time.sleep(2)
    q = c.xpath_text(name)

    def find_node(drv):
        xpaths = [
            f"//table[@id='all_doc_list']//tr[contains(@class, 'clickie')]/td[1][normalize-space(.)={q} or starts-with(normalize-space(.), concat({q}, ' ('))]",
            f"//*[name()='g' and contains(@class, 'node')][.//*[name()='text' and normalize-space(.)={q}]]",
            f"//*[name()='text' and normalize-space(.)={q}]",
            f"//*[name()='text' and contains(normalize-space(.), {q})]",
            f"//a[contains(@class, 'jstree-anchor') and normalize-space(.)={q}]",
            f"//*[self::td or self::span or self::div or self::a or self::li][normalize-space(.)={q}]",
        ]
        for xp in xpaths:
            els = [e for e in drv.find_elements(By.XPATH, xp) if e.is_displayed()]
            if els:
                return els[-1]
        return None

    node = WebDriverWait(driver, 10).until(find_node)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", node)
    try:
        circle = node.find_elements(By.XPATH, ".//*[name()='circle'] | ./preceding-sibling::*[name()='circle']")
        target = circle[0] if circle else node
        ActionChains(driver).move_to_element(target).click().perform()
    except Exception:
        c.click(driver, node)
    time.sleep(1)
    return node


def create_category(driver, wait, name, kind="doc-type", parent=None):
    """Categorization page: Add, choose category / doc-type, type the name, Save. Returns (True/False, message)."""
    driver.get(c.ROOT_URL)
    time.sleep(2)
    if parent:
        select_tree_item(driver, wait, parent)
    c.click_label(driver, wait, "add")
    time.sleep(1)
    try:
        target_label = "Document" if "doc" in kind.lower() else "Category"
        toggle = c.visible(driver, ".modal.in button.dropdown-toggle, .modal.show button.dropdown-toggle")
        if toggle:
            c.click(driver, toggle[0])
            time.sleep(0.5)
            opts = c.visible(driver, ".modal.in .dropdown-menu.open a, .modal.show .dropdown-menu.open a")
            match = [o for o in opts if target_label.lower() in o.text.lower()]
            if match:
                c.click(driver, match[0])
                time.sleep(0.5)
        else:
            kind_el = c.find_by_label(driver, kind)
            if kind_el and "deleted" not in (kind_el.get_attribute("href") or "").lower():
                c.click(driver, kind_el)
    except Exception:
        pass
    box = WebDriverWait(driver, 10).until(lambda drv: c.modal_text_input(drv) or c.find_field(drv, "name"))
    box.clear()
    box.send_keys(name)
    ok, msg = c.do(driver, wait, "save")
    time.sleep(1)
    return ok, msg


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
    driver.get(c.ROOT_URL)
    time.sleep(2)
    print(f"   [debug] URL after driver.get(ROOT_URL): {driver.current_url}")
    avail = c.visible(driver, "#available_categories")
    if avail:
        print("   [debug] Clicking #available_categories to switch back to Categorization tree")
        c.click(driver, avail[0])
        time.sleep(2)

    try:
        node = select_tree_item(driver, wait, name)
        print(f"   [debug] Selected tree node for {name!r}: tag=<{node.tag_name}> text={node.text!r}")
    except Exception:
        texts = [e.text.strip() for e in driver.find_elements(By.XPATH, "//*[name()='text' or self::a or self::button]") if e.is_displayed() and e.text.strip()]
        print(f"   [debug] Could not find node {name!r}! Visible texts on page: {texts[:30]}")
        raise

    def find_delete_btn(drv):
        for el in drv.find_elements(
            By.CSS_SELECTOR,
            "#delete, #delete_btn, #delete_category, #delete_doc_type, #remove_node, "
            "button[id*='delete' i], a[id*='delete' i], button[data-type*='delete' i], "
            "button[title*='Delete' i], a[title*='Delete' i], "
            "button[data-original-title*='Delete' i], a[data-original-title*='Delete' i], "
            "#content .fa-trash, #content .fa-trash-can, #content .fa-trash-o, #content .zmdi-delete",
        ):
            if not el.is_displayed():
                continue
            if el.find_elements(By.XPATH, "ancestor-or-self::*[@id='deleted_categories']"):
                continue
            info = " ".join(
                str(el.get_attribute(a) or "")
                for a in ("id", "class", "title", "data-original-title", "href")
            ).lower() + " " + (el.text or "").lower()
            if "deleted" not in info and "permanent" not in info and "search" not in info:
                return el
        return c.find_by_label(drv, "delete")

    def action():
        more = c.visible(driver, "#more_btn")
        if more and not c.visible(driver, "#delete_btn"):
            c.click(driver, more[0])
            time.sleep(0.5)
        btn = WebDriverWait(driver, 10).until(
            lambda drv: (c.visible(drv, "#delete_btn") or [None])[0] or find_delete_btn(drv)
        )
        c.click(driver, btn)
        time.sleep(1)
        c.confirm(driver, wait, "yes", seconds=15)

    try:
        return c.message_after(driver, action)
    except Exception as e:
        return False, f"Delete toast did not appear ({c.short(e)})"


def create_metadata(driver, wait, doc_type, display_name, data_type="text"):
    """Double click the doc-type, click Add, give name / display name / order / data type, Save."""
    driver.get(c.ROOT_URL)
    select_tree_item(driver, wait, doc_type)
    c.double_click_label(driver, wait, doc_type)
    time.sleep(2)
    c.click_label(driver, wait, "add")
    time.sleep(1)
    c.fill_field(driver, "name", display_name.lower().replace(" ", "_"))
    c.fill_field(driver, "display name", display_name)
    try:
        c.fill_field(driver, "order", "1")
    except Exception:
        pass
    c.pick_option(driver, "data type", data_type)
    return c.do(driver, wait, "save")


def new_metadata(driver, wait, doc_type, label="Meta"):
    display = datetime.now().strftime(f"AUTO {label} %H%M%S")
    ok, message = create_metadata(driver, wait, doc_type, display)
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
    driver.get(c.BULK_URL)
    wait.until(lambda drv: c.visible(drv, "span.select2-selection"))
    c.pick_select2(driver, wait, term[:5])
    time.sleep(1)


def download_template(driver, wait, term):
    """Bulk upload page: pick the doc-type, click Download template. Returns the downloaded file path."""
    pick_bulk_doc_type(driver, wait, term)
    before = set(os.listdir(c.DOWNLOAD_DIR))
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