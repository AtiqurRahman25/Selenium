"""
DMS-TC058
Sorting (Name Ascending) on My Docments
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
2. Select a doc-type which has document
1. Document should be shown as name wise ascending
2. Sorting should work for page changes
"""
import os

import common as c
import explorer_helper as e

TEST_CASE_ID = "DMS-TC058"

DOC_TYPE = os.getenv("EXPLORER_DOC_TYPE")  # path like /1 FC Test updated/aa/ (needs more than one page of documents)


def sorting(driver, wait):
    e.open_doc_type(driver, wait, DOC_TYPE)
    e.choose_order(driver, wait, "Name (A to Z)")
    wait.until(lambda drv: c.visible(drv, e.LIST))
    rows, pages = e.read_pages(driver, DOC_TYPE)

    names = [row[1] for row in rows]  # 2nd column = Document Name
    for i in range(len(names) - 1):
        if e.sort_name(names[i]) > e.sort_name(names[i + 1]):
            return False, (f"NOT Name ascending: '{names[i]}' is shown before '{names[i + 1]}'. "
                           f"{len(names)} documents checked over {pages} pages")
    return True, f"{len(names)} documents checked over {pages} pages: Name ascending"


SCENARIOS = [("Name ascending", sorting)]


def main():
    c.need_env("EXPLORER_DOC_TYPE", "(path like /1 FC Test updated/aa/, with more than one page of documents)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()