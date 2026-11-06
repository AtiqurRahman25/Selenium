"""
DMS-TC055
Grid View on My Documents
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Click on "grid" icon
3. Click on "document" icon
4. Click on "view" icon
1. Document list should be shown in grid view
2. Document should be opened in new tab
3. Document quick view modal should be opened
"""
import os
import time

from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC055"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (or just the name)
TREE = "left_cat_doc_explorer"
DOCUMENTS = "#main-window .file-thumb, #main-window table tbody tr, #file_manager_content table tbody tr"
CHILDREN = "./ul/li/a[contains(@class,'jstree-anchor')]"  # direct children only


def child_anchors(scope):
    anchors = scope.find_elements(By.XPATH, CHILDREN)
    return [a for a in anchors if not name_of(a).lower().startswith("loading")]  # skip jsTree 'Loading ...' placeholder


def name_of(anchor):
    return (anchor.get_attribute("textContent") or "").strip()


def open_doc_type(driver, wait, path):
    """Follow the path in the My Documents tree (opening each category), then click the last item."""
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

    # select the doc-type through jsTree so its 'changed' event loads the documents and shows the grid/list icons
    leaf_id = target.find_element(By.XPATH, "..").get_attribute("id")
    driver.execute_script(f"var t = $('#{TREE}').jstree(true); t.deselect_all(); t.select_node(arguments[0]);", leaf_id)
    try:
        WebDriverWait(driver, 20).until(
            lambda drv: c.visible(drv, "#grid_view") and c.visible(drv, DOCUMENTS))
    except Exception:
        raise c.SetupError(f"'{path}' shows no documents, use a doc-type that has documents")
    time.sleep(1)


def grid_view(driver, wait):
    open_doc_type(driver, wait, DOC_TYPE)

    # 1. grid icon -> documents shown as cards (div.file-thumb), not as the list table
    c.click(driver, wait.until(EC.element_to_be_clickable((By.ID, "grid_view"))))
    time.sleep(2)
    cards = c.visible(driver, "div.file-thumb a.ci-avatar")
    list_table = c.visible(driver, "#explorer_file_list_view")
    if not cards or list_table:
        return False, "documents are not shown in grid view after clicking the grid icon"

    # 2. document icon -> opens in a new tab
    main_tab = driver.current_window_handle
    old_tabs = driver.window_handles
    c.click(driver, cards[0])
    time.sleep(3)
    opened_tab = len(driver.window_handles) > len(old_tabs)
    if opened_tab:
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()
    driver.switch_to.window(main_tab)

    # 3. view (preview) icon -> quick view modal
    preview = c.visible(driver, "div.file-thumb a.quick_view")
    if not preview:
        return False, "Grid view shown, but the view (preview) icon was not found"
    c.click(driver, preview[0])
    time.sleep(2)
    quick_view = bool(c.visible(driver, ".modal.in, .modal.show"))

    ok = opened_tab and quick_view
    return ok, f"Grid view shown. Document opened in new tab: {'yes' if opened_tab else 'NO'}. Quick view modal opened: {'yes' if quick_view else 'NO'}"


SCENARIOS = [("Grid view", grid_view)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()