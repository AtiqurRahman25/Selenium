"""
DMS-TC094
Bulk Upload Template Upload
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/bulk-upload/
2. Type & select a doc-type
3. upload bulk upload template csv (blank/same value in unique metadata/wrong formated data/wrong type attachment)
System shouldn't allow to upload documents & give proper error in "Bulk Upload Report"
"""
import os

import common as c
import dms_helper as d
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC094"

DOC_TYPE = os.getenv("BULK_DOC_TYPE")  # search text of a doc-type for bulk upload


def rejected(label, make_file):
    """The page must not accept the file and must show an error."""
    def scenario(driver, wait):
        template = d.download_template(driver, wait, DOC_TYPE)
        header = d.template_header(template)
        path = make_file(header)
        ok, message = d.bulk_submit(driver, wait, DOC_TYPE, path)
        error_shown = (not ok) or "error" in h.body_text(driver)
        return error_shown, f"{label} file " + (f"was rejected: {message}" if error_shown else f"was ACCEPTED: {message}")
    return scenario


def blank_file(header):
    return d.write_csv(os.path.join(c.DOWNLOAD_DIR, "AUTO_blank.csv"), header, [[""] * len(header)])


def same_value_file(header):
    row = ["AUTO_SAME"] * len(header)
    return d.write_csv(os.path.join(c.DOWNLOAD_DIR, "AUTO_same.csv"), header, [row, row])


def wrong_format_file(header):
    return d.write_csv(os.path.join(c.DOWNLOAD_DIR, "AUTO_format.csv"), header, [["!!bad!!"] * len(header)])


def wrong_type_file(header):
    return c.find_sample_file("png")[1]  # an image instead of the csv


SCENARIOS = [("Blank data", rejected("Blank", blank_file)),
             ("Same unique value", rejected("Same value", same_value_file)),
             ("Wrong format data", rejected("Wrong format", wrong_format_file)),
             ("Wrong type attachment", rejected("Wrong type", wrong_type_file))]


def main():
    c.need_env("BULK_DOC_TYPE", "(search text of a doc-type for bulk upload)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
