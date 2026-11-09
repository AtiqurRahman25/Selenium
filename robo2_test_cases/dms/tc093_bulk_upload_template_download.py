"""
DMS-TC093
Bulk Upload Template  Download
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/bulk-upload/
2. Type & select a doc-type
3. Click on "Download" template
Selected doc-type bulk upload template should be downloaded
"""
import os

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC093"

DOC_TYPE = os.getenv("BULK_DOC_TYPE")  # search text of a doc-type for bulk upload


def template_download(driver, wait):
    path = d.download_template(driver, wait, DOC_TYPE)
    size = os.path.getsize(path)
    return size > 0, f"Template downloaded: {os.path.basename(path)} ({size} bytes)"


SCENARIOS = [("Template download", template_download)]


def main():
    c.need_env("BULK_DOC_TYPE", "(search text of a doc-type for bulk upload)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
