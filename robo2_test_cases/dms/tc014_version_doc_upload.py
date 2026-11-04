"""
DMS-TC014	
Version Doc Upload	
"1. Open a document
2. Click on ""Add"" icon on version history
3. Select new version doc, can give file name extended part
4. Click on ""Save Changes
Version doc should be uploaded with proper confirmation message. Extended name should show.
"""
import common as c

TEST_CASE_ID = "DMS-TC014"

EXTENDED_NAME = "AUTO_v2"  # the extended part of the version file name


def version_upload(driver, wait):
    c.new_document(driver, wait)
    ok, message = c.add_version(driver, wait, EXTENDED_NAME)
    if not ok:
        return False, message
    c.show_versions(driver, wait, EXTENDED_NAME)
    shown = c.wait_text(driver, EXTENDED_NAME)
    return shown, f"{message}. Extended name '{EXTENDED_NAME}' " + ("shown in version history" if shown else "not shown in version history")

SCENARIOS = [("Version upload", version_upload)]

def main():
    c.run(TEST_CASE_ID, SCENARIOS)

if __name__ == "__main__":
    main()
