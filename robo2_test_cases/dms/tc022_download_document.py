"""
DMS-TC022
Download Document
1. Open a document 
2. Click on "download"
Document should be downloaded
"""
import os

import common as c

TEST_CASE_ID = "DMS-TC022"

def download_document(driver, wait):
    c.new_document(driver, wait)
    before = set(os.listdir(c.DOWNLOAD_DIR))
    c.click_label(driver, wait, "download")
    file_name = c.wait_for_download(before)
    if file_name:
        return True, f"Document downloaded: {file_name}"
    return False, "no file was downloaded after clicking Download"


SCENARIOS = [("Download", download_document)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
