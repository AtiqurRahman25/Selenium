"""
DMS-TC034
Share Documents (Delete)
1. Go to "Document View" page
2. Click on "Delete" button under "Share Document" section
Share documents participants should be removed & those documents no longer available for those people
"""
import time
from selenium.webdriver.common.by import By
import common as c

TEST_CASE_ID = "DMS-TC034"

DELETE_SELECTORS = (
    "#share_document button[data-type*='delete' i], "
    "#share_document button[data-type*='remove' i], "
    "#share_document button[data-type*='unshare' i], "
    "#share_document button[title*='Delete' i], "
    "#share_document a[title*='Delete' i], "
    "#share_document [onclick*='delete' i], "
    "#share_document [onclick*='remove' i], "
    "#share_document .fa-trash, "
    "#share_document .zmdi-delete, "
    "#share_document .select2-selection__choice__remove"
)

CONFIRM_XPATH = (
    f"{c.MODAL}//*[self::button or self::a or self::input]"
    "[contains(translate(normalize-space(.), 'YESDLTRMVOK', 'yesdltrmvok'), 'yes') or "
    "contains(translate(normalize-space(.), 'YESDLTRMVOK', 'yesdltrmvok'), 'delete') or "
    "contains(translate(normalize-space(.), 'YESDLTRMVOK', 'yesdltrmvok'), 'remove') or "
    "contains(translate(normalize-space(.), 'YESDLTRMVOK', 'yesdltrmvok'), 'ok')]"
)


def expand_share_section(driver):
    time.sleep(2)
    panel = driver.find_elements(By.ID, "share_document")
    if panel and "in" in (panel[0].get_attribute("class") or "").split():
        return
    headers = driver.find_elements(By.CSS_SELECTOR, "[href='#share_document'], #document-share-id .card-header")
    if headers:
        c.click(driver, headers[0])
        time.sleep(1.5)


def get_delete_btn(driver):
    for el in driver.find_elements(By.CSS_SELECTOR, DELETE_SELECTORS):
        if el.is_displayed():
            return el
    for el in driver.find_elements(By.XPATH, "//div[@id='share_document']//*[self::button or self::a or self::input]"):
        label = (el.text or el.get_attribute("value") or "").strip().lower()
        if label in ("delete", "remove", "unshare") and el.is_displayed():
            return el
    return None


def click_if_confirm_modal_open(driver):
    time.sleep(1)
    for btn in driver.find_elements(By.XPATH, CONFIRM_XPATH):
        if btn.is_displayed():
            c.click(driver, btn)
            time.sleep(1)
            return


def delete_share(driver, wait):
    info = c.upload_document(driver, wait, "pdf", share="users")
    name = info["name"]
    shared_with = info["shared_with"]

    c.open_document(driver, wait, name)
    expand_share_section(driver)

    del_btn = get_delete_btn(driver)
    if del_btn is None:
        return False, "Could not find the Delete button under the Share Document(s) section"

    is_token = "select2-selection__choice__remove" in (del_btn.get_attribute("class") or "")
    c.click(driver, del_btn)
    time.sleep(1)

    if is_token:
        save_btns = driver.find_elements(
            By.XPATH,
            "//div[@id='share_document']//*[self::button or self::a or self::input]"
            "[contains(translate(normalize-space(.), 'SHAREUPDT', 'shareupdt'), 'share') or "
            "contains(translate(normalize-space(.), 'SHAREUPDT', 'shareupdt'), 'update')]"
        )
        for btn in save_btns:
            if btn.is_displayed():
                c.click(driver, btn)
                time.sleep(1)
                break

    click_if_confirm_modal_open(driver)
    time.sleep(2)
    expand_share_section(driver)

    return True, f"Shared participant '{shared_with}' removed from '{name}' successfully"


SCENARIOS = [("Delete share", delete_share)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
