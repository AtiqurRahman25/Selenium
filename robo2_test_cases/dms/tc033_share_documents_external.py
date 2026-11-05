"""
DMS-TC033
Share Documents (External Share)
1. Go to "Pending Documents/Document View" page
2. Select public
3. Click on "Share" button
Documents should be shared with all system users & anyone with the link can access those documents.
"""
import time
import common as c

TEST_CASE_ID = "DMS-TC033"


def share_public(driver, wait):
    info = c.upload_document(driver, wait, "pdf", share="public")
    name = info["name"]

    # Verify the uploaded public document is searchable and accessible in Document View
    found = c.search_finds(driver, wait, name, tries=3)
    if not found:
        return False, f"Uploaded as '{info['shared_with']}', but document '{name}' was not found in search"

    c.open_document(driver, wait, name)
    time.sleep(2)

    # Expand the Share Document(s) panel if present so the screenshot captures the Public share state
    driver.execute_script("""
        document.querySelectorAll('.card-header, .panel-heading, a, div').forEach(function(el) {
            var t = (el.innerText || '').trim().toLowerCase();
            if (t === 'share document(s)' || t === 'share documents' || t === 'share') {
                el.click();
            }
        });
    """)
    time.sleep(1.5)

    return True, f"Document '{name}' uploaded and shared externally as '{info['shared_with']}' successfully"


SCENARIOS = [("Public share", share_public)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()