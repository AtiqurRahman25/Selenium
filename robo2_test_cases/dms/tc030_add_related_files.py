"""
DMS-TC030
Add Related Files
1. Open a document
2. Click on "Add" icon on related files
3. Check mark all needed files
4. Click on "Link" button
Related files should be linked with proper confirmation message and should view properly
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import common as c

TEST_CASE_ID = "DMS-TC030"


def link_related_file(driver, wait, other_name):
    """Open the #addRelated modal, tick `other_name`, and click the Link button."""
    c.click(driver, wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-type='related']"))))
    modal = wait.until(EC.visibility_of_element_located((By.ID, "addRelated")))
    time.sleep(1)

    inputs = [i for i in modal.find_elements(By.CSS_SELECTOR, "input[type='text'], input[type='search']") if i.is_displayed()]
    if inputs:
        inputs[0].clear()
        inputs[0].send_keys(other_name, Keys.ENTER)
        time.sleep(2)

    item = wait.until(
        EC.presence_of_element_located((
            By.XPATH,
            f"//div[@id='addRelated']//*[self::tr or self::li or contains(@class, 'list-group-item')][contains(., {c.xpath_text(other_name)})]"
        ))
    )
    driver.execute_script("""
        var item = arguments[0];
        var cb = item.querySelector("input[type='checkbox']");
        if (cb && !cb.checked) {
            var lbl = cb.id ? document.querySelector("label[for='" + cb.id + "']") : null;
            if (lbl) lbl.click(); else cb.click();
            if (!cb.checked) {
                cb.checked = true;
                cb.dispatchEvent(new Event('change', {bubbles: true}));
            }
        } else if (!cb) {
            item.click();
        }
    """, item)
    time.sleep(1)

    link_btn = modal.find_element(By.CSS_SELECTOR, "button[data-type='addLinkedFile']")
    return c.message_after(driver, lambda: c.click(driver, link_btn))


def is_related_shown(driver, name):
    """Wait for the post-link reload, expand the Related Files panel, and verify `name` is visible."""
    time.sleep(3)
    if c.wait_text(driver, name, 3):
        return True

    driver.execute_script("""
        var btn = document.querySelector("button[data-type='related']");
        if (btn) {
            var card = btn.closest('.card, .panel') || btn.parentElement.parentElement;
            if (card) {
                var toggle = card.querySelector('[data-toggle="collapse"], .card-header a, .card-header');
                if (toggle) toggle.click();
                card.querySelectorAll('.collapse').forEach(function(c) {
                    c.classList.add('in', 'show');
                    c.style.display = 'block';
                    c.style.height = 'auto';
                });
            }
        }
    """)
    time.sleep(2)
    return c.wait_text(driver, name, 5)


def add_related(driver, wait):
    first = c.upload_document(driver, wait, "pdf")
    second = c.upload_document(driver, wait, "txt")
    c.open_document(driver, wait, first["name"])

    ok, message = link_related_file(driver, wait, second["name"])
    if not ok:
        return False, message

    shown = is_related_shown(driver, second["name"])
    return shown, f"{message}. Related file '{second['name']}' " + ("shown in related files" if shown else "NOT shown in related files")


SCENARIOS = [("Add related file", add_related)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()