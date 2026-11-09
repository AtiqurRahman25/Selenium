"""
DMS-TC095
Bulk Upload Template Upload
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/bulk-upload/
2. Type & select a doc-type
3. upload bulk upload template csv (correct data, few row data)
System should upload the documents with confirmation message

The test makes its own doc-type (two text meta-data, no unique / dropdown rules), so it can run again and again.
"""
import os
import time
from datetime import datetime

import common as c
import dms_helper as d
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC095"


def new_bulk_doc_type(driver, wait):
    """New doc-type with two text meta-data, published so it can be picked on the upload pages."""
    doc_type = d.new_doc_type(driver, wait)
    d.new_metadata(driver, wait, doc_type, "One")
    d.new_metadata(driver, wait, doc_type, "Two")
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, doc_type)
    c.message_after(driver, lambda: d._click_more_menu_item(driver, wait, "pub_per"))
    return doc_type


def bulk_upload(driver, wait):
    doc_type = new_bulk_doc_type(driver, wait)
    template = d.download_template(driver, wait, doc_type)
    header = d.template_header(template)
    run_id = datetime.now().strftime("%H%M%S")
    # copies with new content, because the system rejects a file it already has (checksum)
    files = [c.unique_copy(c.find_sample_file(ext)[1])[1] for ext in ["pdf", "txt"]]
    rows = []
    for number, path in enumerate(files):
        # every column gets a unique value, a column that looks like a file name gets the file
        rows.append([os.path.basename(path) if "file" in column.lower() else f"AUTO_{run_id}_{number}_{i}"
                     for i, column in enumerate(header)])
    csv_path = d.write_csv(os.path.join(c.DOWNLOAD_DIR, "AUTO_bulk.csv"), header, rows)
    ok, message = d.bulk_submit(driver, wait, doc_type, csv_path, files)
    time.sleep(5)
    report_error = "error" in h.body_text(driver)
    return ok and not report_error, f"{message}. " + ("Upload record shows an error" if report_error else "No error shown")


SCENARIOS = [("Valid template", bulk_upload)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()