"""
DMS-TC031
Delete Related Files
1. Open a document
2. Click on related files
3. Click on "Delete" icon
4. Click on "Yes, Unlink" button
Related files should be unlinked with proper confirmation message
"""
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import common as c

TEST_CASE_ID = "DMS-TC031"


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


def expand_related_panel(driver):
    """Wait for post-link reload and expand the Related Files panel on the right sidebar."""
    time.sleep(3)
    driver.execute_script("""
        var btn = document.querySelector("button[data-type='related']");
        if (btn) {
            var card = btn.closest('.card, .panel') || btn.parentElement.parentElement;
            if (card) {
                var toggle = card.querySelector('[data-toggle="collapse"], .card-header a, .card-header');
                if (toggle && !card.querySelector('.collapse.in, .collapse.show')) {
                    toggle.click();
                }
                card.querySelectorAll('.collapse').forEach(function(c) {
                    c.classList.add('in', 'show');
                    c.style.display = 'block';
                    c.style.height = 'auto';
                });
            }
        }
    """)
    time.sleep(2)


def unlink_related_file(driver, wait, other_name):
    """Find the delete/unlink icon next to `other_name` in Related Files, click it, and confirm."""
    expand_related_panel(driver)

    del_btn = driver.execute_script("""
        var name = arguments[0];
        var btn = document.querySelector("button[data-type='related']");
        var root = (btn && (btn.closest('.card, .panel') || btn.parentElement.parentElement)) || document;

        var rows = Array.from(root.querySelectorAll('tr, li, .list-group-item, .lv-item, div')).filter(function(el) {
            var t = (el.innerText || '').trim();
            return t.indexOf(name) !== -1 && el.querySelectorAll('a, button, i').length > 0;
        });
        // Pick the most specific (smallest) container holding both the file name and action icons
        rows.sort(function(a, b) { return (a.innerText || '').length - (b.innerText || '').length; });
        var row = rows[0];
        if (!row) return null;

        var candidates = Array.from(row.querySelectorAll('button, a, i, span')).filter(function(el) {
            var html = (el.outerHTML || '').toLowerCase();
            return html.indexOf('delete') !== -1 ||
                   html.indexOf('unlink') !== -1 ||
                   html.indexOf('remove') !== -1 ||
                   html.indexOf('trash') !== -1 ||
                   html.indexOf('close') !== -1 ||
                   html.indexOf('times') !== -1;
        });
        if (candidates.length > 0) return candidates[0];

        // Fallback: last clickable icon/button in the row (excluding the filename link itself)
        var clickables = Array.from(row.querySelectorAll('button, a, i')).filter(function(el) {
            return (el.innerText || '').trim().indexOf(name) === -1 && el.offsetParent !== null;
        });
        return clickables[clickables.length - 1] || null;
    """, other_name)

    if del_btn is None:
        return c.do_near(driver, wait, other_name, "delete", "yes")

    def action():
        c.click(driver, del_btn)
        time.sleep(1)
        c.confirm_any(driver, wait, ("yes", "unlink", "delete", "ok"))

    return c.message_after(driver, action)


def delete_related(driver, wait):
    first = c.upload_document(driver, wait, "pdf")
    second = c.upload_document(driver, wait, "txt")
    c.open_document(driver, wait, first["name"])

    ok, message = link_related_file(driver, wait, second["name"])
    if not ok:
        raise c.SetupError(f"could not link the related file ({message})")

    ok, message = unlink_related_file(driver, wait, second["name"])
    if not ok:
        return False, message

    expand_related_panel(driver)
    gone = not c.wait_text(driver, second["name"], 3)
    return gone, f"{message}. Related file " + ("removed from the list" if gone else "still shown in the list")


SCENARIOS = [("Delete related file", delete_related)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()