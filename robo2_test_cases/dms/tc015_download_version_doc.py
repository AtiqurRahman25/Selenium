"""
DMS-TC015
Download version doc
1. Open a document with version doc
2. Click on on version history
3. Click on "Download" icon
Version doc should be downloaded
"""
import os

import common as c

TEST_CASE_ID = "DMS-TC015"

EXTENDED_NAME = "AUTO_v2"


def version_download(driver, wait):
    c.new_document(driver, wait)
    ok, message = c.add_version(driver, wait, EXTENDED_NAME)
    if not ok:
        raise c.SetupError(f"version doc could not be added ({message})")
    c.show_versions(driver, wait, EXTENDED_NAME)
    before = set(os.listdir(c.DOWNLOAD_DIR))
    c.click_near(driver, wait, EXTENDED_NAME, "download")
    file_name = c.wait_for_download(before)
    if file_name:
        return True, f"Version doc downloaded: {file_name}"
    return False, "no file was downloaded after clicking the Download icon of the version"


SCENARIOS = [("Version download", version_download)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
