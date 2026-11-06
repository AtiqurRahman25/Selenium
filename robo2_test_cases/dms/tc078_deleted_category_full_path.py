"""
DMS-TC078
Deleted Category Full Path
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
Categories/Doc-type full path should be shown
"""
from datetime import datetime

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC078"

def full_path(driver, wait):
    parent = datetime.now().strftime("AUTO_PARENT_%H%M%S")
    ok, message = d.create_category(driver, wait, parent, "category")
    if not ok:
        raise c.SetupError(f"could not create the parent category ({message})")
    child = d.new_doc_type(driver, wait, parent=parent)  # inside the parent, so the full path has two parts
    ok, message = d.delete_category(driver, wait, child)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)
    row = c.find_by_label(driver, child, slack=300)
    if row is None:
        return False, f"'{child}' not found in the deleted list"
    text = row.text
    ok = parent.lower() in text.lower()
    return ok, f"Deleted doc-type is shown as '{' '.join(text.split())}'" + ("" if ok else f" (the parent '{parent}' is missing from the path)")


SCENARIOS = [("Full path", full_path)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
