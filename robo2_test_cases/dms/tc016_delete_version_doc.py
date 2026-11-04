"""
DMS-TC016
Delete version doc
1. Open a document with one or more version doc
2. Click on on version history
3. Click on "Delete" icon of version doc
Version doc should be deleted with proper confirmation message
"""
import common as c

TEST_CASE_ID = "DMS-TC016"

EXTENDED_NAME = "AUTO_v2"


def version_delete(driver, wait):
    c.new_document(driver, wait)
    ok, message = c.add_version(driver, wait, EXTENDED_NAME)
    if not ok:
        raise c.SetupError(f"version doc could not be added ({message})")
    c.show_versions(driver, wait, EXTENDED_NAME)
    ok, message = c.do_near(driver, wait, EXTENDED_NAME, "delete", "yes")
    return ok, message


SCENARIOS = [("Version delete", version_delete)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()