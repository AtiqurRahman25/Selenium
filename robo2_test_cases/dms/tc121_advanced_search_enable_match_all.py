"""
DMS-TC121
Advanced Search (Enable Match All)
1. Click on global search arrow icon
2. Select doc type
3. Give metadata
4. Enable "Match All"
5. Click on "Search"
System should only show only those documents which matched all meta field data
"""
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC121"


def find_search_field(driver, label_text):
    """Find a metadata input/textarea inside #dms_search_form by its label text or id/name."""
    field = c.find_field(driver, label_text)
    if field is not None:
        return field
    wanted = c.clean(label_text)
    for el in driver.find_elements(
        By.XPATH,
        "//form[@id='dms_search_form']//div[contains(@class, 'meta-data-wrap')]"
        "//*[(self::input or self::textarea) and not(ancestor::*[contains(@class, 'bs-searchbox')])]",
    ):
        if not el.is_displayed():
            continue
        el_id = c.clean(el.get_attribute("id") or "")
        el_name = c.clean(el.get_attribute("name") or "")
        container_text = ""
        try:
            container = el.find_element(
                By.XPATH, "ancestor::div[contains(@class, 'form-group') or contains(@class, 'fg-line')][1]"
            )
            container_text = c.clean(container.text.split(":", 1)[0])
        except Exception:
            pass
        if wanted in (el_id, el_name, container_text) or container_text.startswith(wanted):
            return el
    return None


def run_advanced_search(driver, wait, name, match_all=True, doc_type=None, extra=None):
    """Open Advanced Search, select doc-type, fill metadata fields in .meta-data-wrap, set Match All, and click Search."""
    if not c.visible(driver, "#dms_search_form"):
        c.click(driver, wait.until(EC.element_to_be_clickable(c.FILTER_BTN)))
    box = wait.until(EC.visibility_of_element_located((By.ID, "docname")))
    box.clear()
    box.send_keys(name or "")
    if doc_type:
        c.pick_select2_by_id(driver, wait, "documentType", doc_type)
    for field_label, value in (extra or []):
        field = WebDriverWait(driver, 10).until(lambda d, lbl=field_label: find_search_field(d, lbl))
        field.clear()
        field.send_keys(value)
    if driver.find_element(By.ID, "match_all").is_selected() != match_all:
        c.click(driver, driver.find_element(By.CSS_SELECTOR, "label[for='match_all'].ts-helper"))
    c.click(driver, driver.find_element(By.ID, "search_btn"))
    time.sleep(3)


def advanced(driver, wait):
    first = c.upload_document(driver, wait, "pdf")
    second = c.upload_document(driver, wait, "pdf")
    if len(first["values"]) >= 2 and len(second["values"]) >= 2:
        # field 1 has the value of the first document, field 2 has the value of the second one
        pairs = [(first["values"][0][0], first["values"][0][1]), (second["values"][1][0], second["values"][1][1])]
        name = None
    elif first["values"] and second["values"]:
        pairs = [(second["values"][0][0], second["values"][0][1])]
        name = first["name"]  # document name of the first + meta-data of the second
    else:
        raise c.SetupError("the doc-type has no text meta-data to search with")

    driver.get(c.EXPLORER_URL)
    run_advanced_search(driver, wait, name, match_all=True, doc_type=first["doc_type"], extra=pairs)
    text = c.body_text(driver)
    found_a = first["name"].lower() in text
    found_b = second["name"].lower() in text
    ok = not found_a and not found_b
    return ok, f"Match All on: first document {'shown' if found_a else 'not shown'}, second document {'shown' if found_b else 'not shown'} (expected neither document)"


SCENARIOS = [("Match All enabled", advanced)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
