"""
Shared helpers for the My Documents (explorer) test scripts: open a category / doc-type by path,
choose Order By, read the list view page by page.
Keep this file in the same folder as common.py.
"""
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TREE = "left_cat_doc_explorer"
LIST = "#explorer_file_list_view"
NEXT = "#paginate_explorer li.page-item.next:not(.disabled) a"
DOCUMENTS = "#main-window .file-thumb, #main-window table tbody tr, #file_manager_content table tbody tr"
CHILDREN = "./ul/li/a[contains(@class,'jstree-anchor')]"  # direct children only


def name_of(anchor):
    return (anchor.get_attribute("textContent") or "").strip()


def child_anchors(scope):
    anchors = scope.find_elements(By.XPATH, CHILDREN)
    return [a for a in anchors if not name_of(a).lower().startswith("loading")]  # skip jsTree 'Loading ...' placeholder


def open_doc_type(driver, wait, path):
    """Follow the path in the My Documents tree (opening each category), then select the last item."""
    parts = [p.strip() for p in path.strip().strip("/").split("/") if p.strip()]
    driver.get(c.EXPLORER_URL)
    tree = wait.until(EC.presence_of_element_located((By.ID, TREE)))
    WebDriverWait(driver, 30).until(lambda drv: child_anchors(tree))  # tree items load by AJAX

    scope = tree
    target = None
    for i, part in enumerate(parts):
        anchors = child_anchors(scope)
        match = [a for a in anchors if name_of(a).lower() == part.lower()]
        if not match:
            names = [name_of(a) for a in anchors][:15]
            raise c.SetupError(f"'{part}' not found in the tree. Items there: {names}")
        target = match[0]
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
        if i < len(parts) - 1:
            node_id = target.find_element(By.XPATH, "..").get_attribute("id")  # the <li> of this category
            driver.execute_script(f"$('#{TREE}').jstree('open_node', arguments[0]);", node_id)

            def opened(drv):
                # jsTree redraws the node when it opens, so find it again on every check
                try:
                    node = drv.find_element(By.ID, node_id)
                    return node if child_anchors(node) else False
                except StaleElementReferenceException:
                    return False
            try:
                scope = WebDriverWait(driver, 20).until(opened)
            except Exception:
                raise c.SetupError(f"category '{part}' did not open, or it has nothing inside")

    # select through jsTree so its 'changed' event loads the documents and shows the grid/list icons
    leaf_id = target.find_element(By.XPATH, "..").get_attribute("id")
    driver.execute_script(f"var t = $('#{TREE}').jstree(true); t.deselect_all(); t.select_node(arguments[0]);", leaf_id)
    try:
        WebDriverWait(driver, 20).until(lambda drv: c.visible(drv, DOCUMENTS))
    except Exception:
        raise c.SetupError(f"'{path}' shows no documents, use a doc-type that has documents")
    time.sleep(2)


def choose_order(driver, wait, label):
    """Order By dropdown (bootstrap-select): open it and click the option, e.g. 'Name (A to Z)'."""
    button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-id='order_by']")))
    c.click(driver, button)
    option = wait.until(EC.element_to_be_clickable((
        By.XPATH, f"//button[@data-id='order_by']/following-sibling::div//span[@class='text'][normalize-space()='{label}']")))
    c.click(driver, option)
    time.sleep(3)
    shown = driver.find_element(By.CSS_SELECTOR, "button[data-id='order_by'] .filter-option").text.strip()
    if shown.lower() != label.lower():
        raise c.SetupError(f"could not choose '{label}' in Order By (it shows '{shown}')")


def page_rows(driver):
    """Cell texts of every row on the current page of the list view: [[type, name, uploaded by, uploaded at, ...], ...]."""
    rows = []
    for tr in driver.find_elements(By.CSS_SELECTOR, LIST + " tbody tr"):
        cells = [td.text.strip() for td in tr.find_elements(By.TAG_NAME, "td")]
        if len(cells) >= 4:
            rows.append(cells)
    return rows


def read_pages(driver, path, pages=3):
    """Read the list view of the first pages (clicks the next page button). Returns (rows, pages read)."""
    rows = []
    read = 0
    for _ in range(pages):
        rows += page_rows(driver)
        read += 1
        buttons = driver.find_elements(By.CSS_SELECTOR, NEXT)
        if not buttons or read == pages:
            break
        before = driver.find_element(By.CSS_SELECTOR, LIST + " tbody").text
        c.click(driver, buttons[0])
        try:
            WebDriverWait(driver, 15).until(
                lambda drv: drv.find_element(By.CSS_SELECTOR, LIST + " tbody").text != before)
        except Exception:
            break
        time.sleep(1)
    if read < 2:
        raise c.SetupError(f"'{path}' has only one page of documents, use one with more than one page")
    return rows, read