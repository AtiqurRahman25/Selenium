"""
DMS-TC057
Default Sorting on My Documents
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Select a doc-type which has document
1. By default document should be shown as date wise descending
2. Sorting should work for page changes
"""
import os
import time
from datetime import datetime

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC057"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (needs more than one page of documents)
PAGES = 3  # how many pages to check
TREE = "left_cat_doc_explorer"
LIST = "#explorer_file_list_view"
NEXT = "#paginate_explorer li.page-item.next:not(.disabled) a"
DOCUMENTS = "#main-window .file-thumb, #main-window table tbody tr, #file_manager_content table tbody tr"
CHILDREN = "./ul/li/a[contains(@class,'jstree-anchor')]"  # direct children only
DATE_FORMATS = ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%d/%m/%Y", "%d-%b, %Y", "%d %b, %Y", "%b %d, %Y")


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

    # select through jsTree so its 'changed' event loads the documents
    leaf_id = target.find_element(By.XPATH, "..").get_attribute("id")
    driver.execute_script(f"var t = $('#{TREE}').jstree(true); t.deselect_all(); t.select_node(arguments[0]);", leaf_id)
    try:
        WebDriverWait(driver, 20).until(lambda drv: c.visible(drv, DOCUMENTS))
    except Exception:
        raise c.SetupError(f"'{path}' shows no documents, use a doc-type that has documents")
    time.sleep(2)


def parse_date(text):
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), date_format)
        except ValueError:
            continue
    return None


def page_rows(driver):
    """(document name, uploaded at text) of every row on the current page of the list view."""
    rows = []
    for tr in driver.find_elements(By.CSS_SELECTOR, LIST + " tbody tr"):
        cells = tr.find_elements(By.TAG_NAME, "td")
        if len(cells) >= 4:
            rows.append((cells[1].text.strip(), cells[3].text.strip()))
    return rows


def sorting(driver, wait):
    open_doc_type(driver, wait, DOC_TYPE)
    wait.until(lambda drv: c.visible(drv, LIST))  # the list view is the default view

    rows = []
    pages = 0
    for _ in range(PAGES):
        rows += page_rows(driver)
        pages += 1
        buttons = driver.find_elements(By.CSS_SELECTOR, NEXT)
        if not buttons or pages == PAGES:
            break
        before = driver.find_element(By.CSS_SELECTOR, LIST + " tbody").text
        c.click(driver, buttons[0])
        try:
            WebDriverWait(driver, 15).until(
                lambda drv: drv.find_element(By.CSS_SELECTOR, LIST + " tbody").text != before)
        except Exception:
            break
        time.sleep(1)

    if pages < 2:
        raise c.SetupError(f"'{DOC_TYPE}' has only one page of documents, use one with more than one page")

    dates = [parse_date(text) for _, text in rows]
    if None in dates:
        bad = [text for (_, text), date in zip(rows, dates) if date is None][:3]
        return False, f"could not read the Uploaded At dates (examples: {bad})"

    for i in range(len(dates) - 1):
        if dates[i] < dates[i + 1]:
            return False, (f"NOT Date descending (default): '{rows[i][0]}' ({rows[i][1]}) is shown before "
                           f"'{rows[i + 1][0]}' ({rows[i + 1][1]}). {len(rows)} documents checked over {pages} pages")
    return True, f"{len(rows)} documents checked over {pages} pages: Date descending (default)"


SCENARIOS = [("Date descending (default)", sorting)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/, with more than one page of documents)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()