"""
DMS-TC036
Share Documents (Email)
1. Go to "Document View" page
2. Click on "Email" button under "Share Document" section
3. Add participants (any valid mail & share doc person), subject & attachment
4. Click on "Send" button
Selected participants should get share doc mail with attachments & system should give proper confirmation message
"""
import os
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c

TEST_CASE_ID = "DMS-TC036"

EMAIL = os.getenv("SHARE_EMAIL")  # any valid mail address that can be checked afterwards


def share_by_email(driver, wait):
    c.new_document(driver, wait)

    # 1. Expand "Share Document(s)" accordion card on the right sidebar
    email_btn = driver.find_element(By.ID, "email_share_document")
    if not email_btn.is_displayed():
        header = driver.find_element(By.CSS_SELECTOR, "#document-share-id .card-header")
        c.click(driver, header)
        wait.until(EC.visibility_of(email_btn))
        time.sleep(1)

    # 2. (Step 3 requirement: "share doc person") Select a user in 'Share With' (#shared_docs)
    # so 'Selected_Users_&_Groups' in the email modal has a valid participant as well
    driver.execute_script("""
        var s = document.getElementById('shared_docs');
        if (s) {
            var opt = s.querySelector('optgroup[label="Users"] option') || s.querySelector('option[value="all-2"]');
            if (opt) { opt.selected = true; }
            if (window.$) { $(s).trigger('change'); }
        }
    """)
    time.sleep(0.5)

    # 3. Click "Email" button under "Share Document(s)" section
    c.click(driver, email_btn)
    modal = wait.until(EC.visibility_of_element_located((By.ID, "email_share_document_modal")))
    time.sleep(1.5)

    # 4. Add EMAIL participant into '#to' (handles both Select2 search input and underlying <select id="to">)
    s2_inputs = modal.find_elements(By.CSS_SELECTOR, "input.select2-search__field")
    if s2_inputs and s2_inputs[0].is_displayed():
        s2_inputs[0].send_keys(EMAIL, Keys.ENTER)
    else:
        driver.execute_script("""
            var to = document.getElementById('to');
            if (to) {
                var opt = new Option(arguments[0], arguments[0], true, true);
                to.appendChild(opt);
                if (window.$) { $(to).trigger('change'); }
            }
        """, EMAIL)
    time.sleep(0.5)

    # 5. Fill Subject (#subject) and Body (#body)
    subj = modal.find_element(By.ID, "subject")
    if not (subj.get_attribute("value") or "").strip():
        subj.clear()
        subj.send_keys("AUTO share test")

    body = modal.find_element(By.ID, "body")
    if not (body.get_attribute("value") or "").strip():
        body.send_keys("Please find the shared document attached.")

    # 6. Select Attachment in Bootstrap selectpicker (#attachment)
    # Wait up to 5s for the modal JS to populate the attachment options, then select all/first
    WebDriverWait(driver, 5).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "#attachment option")) > 0
    )
    driver.execute_script("""
        var att = document.getElementById('attachment');
        if (att && att.options.length > 0) {
            for (var i = 0; i < att.options.length; i++) {
                if (att.options[i].value) {
                    att.options[i].selected = true;
                }
            }
            if (window.$) {
                if ($.fn.selectpicker) { $(att).selectpicker('refresh'); }
                $(att).trigger('change');
            }
        }
    """)
    time.sleep(0.5)

    # 7. Click "Send" (#send_email_share_document_modal) and wait for confirmation message
    send_btn = driver.find_element(By.ID, "send_email_share_document_modal")
    ok, message = c.message_after(driver, lambda: c.click(driver, send_btn))
    return ok, f"{message} (mail delivery to {EMAIL} must be checked in the mailbox)"


SCENARIOS = [("Share by email", share_by_email)]


def main():
    c.need_env("SHARE_EMAIL", "(a valid mail address)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()