"""
DMS-TC060
Sorting (Date Ascending) on My Docments
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Select a doc-type which has document
1. Document should be shown as date wise ascending
2. Sorting should work for page changes
"""
import os
from datetime import datetime

import common as c
import explorer_helper as e

TEST_CASE_ID = "DMS-TC060"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (needs more than one page of documents)
DATE_FORMATS = ("%Y-%m-%d", "%d-%b-%Y", "%d %b %Y", "%d/%m/%Y", "%d-%b, %Y", "%d %b, %Y", "%b %d, %Y")


def parse_date(text):
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text.strip(), date_format)
        except ValueError:
            continue
    return None


def sorting(driver, wait):
    e.open_doc_type(driver, wait, DOC_TYPE)
    e.choose_order(driver, wait, "Date (Old to New)")
    wait.until(lambda drv: c.visible(drv, e.LIST))
    rows, pages = e.read_pages(driver, DOC_TYPE)

    dates = [parse_date(row[3]) for row in rows]  # 4th column = Uploaded At
    if None in dates:
        bad = [row[3] for row, date in zip(rows, dates) if date is None][:3]
        return False, f"could not read the Uploaded At dates (examples: {bad})"

    for i in range(len(dates) - 1):
        if dates[i] > dates[i + 1]:
            return False, (f"NOT Date ascending: '{rows[i][1]}' ({rows[i][3]}) is shown before "
                           f"'{rows[i + 1][1]}' ({rows[i + 1][3]}). {len(rows)} documents checked over {pages} pages")
    return True, f"{len(rows)} documents checked over {pages} pages: Date ascending"


SCENARIOS = [("Date ascending", sorting)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/, with more than one page of documents)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()