"""
DMS-TC019
Edit Metadata
1. Open a document
2. Click on on edit metadata
3. Update necessary meta data
4. Click on "Save Changes" button
Metadata should be updated with proper confirmation message
"""
import time
from selenium.webdriver.common.by import By

import common as c

TEST_CASE_ID = "DMS-TC019"


def edit_metadata(driver, wait):
    c.new_document(driver, wait, doc_type="1 FC Test updated/aa")
    time.sleep(2)

    # 1. Click Edit Metadata (check label first, then the floating icon on the Meta Data panel)
    if c.find_by_label(driver, "edit metadata") is not None:
        c.click_label(driver, wait, "edit metadata")
    else:
        edit_btns = driver.find_elements(
            By.XPATH,
            "//*[normalize-space(text())='Meta Data']/ancestor::*[position()<=3]//*[self::button or self::a or self::i] | "
            "//*[contains(@title, 'Edit') or contains(@data-original-title, 'Edit') or contains(@class, 'edit')]"
        )
        for btn in edit_btns:
            if btn.is_displayed():
                c.click(driver, btn)
                break

    time.sleep(2)

    # 2. Find editable metadata fields (excluding quick search and Ask Effy chat)
    fields = [
        f for f in c.visible(driver, "input[type='text'], input[type='number'], textarea")
        if f.is_enabled()
        and not f.get_attribute("readonly")
        and "date" not in (f.get_attribute("id") or "").lower()
        and "search" not in (f.get_attribute("id") or "").lower()
        and "search" not in (f.get_attribute("placeholder") or "").lower()
        and "effy" not in (f.get_attribute("placeholder") or "").lower()
        and "question" not in (f.get_attribute("placeholder") or "").lower()
    ]

    ours = [f for f in fields if (f.get_attribute("value") or "").startswith("AUTO_")]
    if not (ours or fields):
        return False, "no editable meta-data field found"

    target = (ours or fields)[0]
    outer = (target.get_attribute("outerHTML") or "").lower()
    # If the chosen field requires digits only, append '9'; otherwise append '_EDIT'
    if any(w in outer for w in ("digits", "number", "integer", "numeric")):
        target.send_keys("9")
    else:
        target.send_keys("_EDIT")

    if c.find_by_label(driver, "save changes") is not None:
        return c.do(driver, wait, "save changes")
    return c.do(driver, wait, "save")


SCENARIOS = [("Edit metadata", edit_metadata)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()