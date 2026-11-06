"""
DMS-TC075
Deleted Category Map
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category
3. Click on "See Map"
Selected categories map will be shown
"""
import time

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC075"

def see_map(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)
    d.select_tree_item(driver, wait, name)
    c.click_label(driver, wait, "see map")
    time.sleep(2)
    popups = [e.text for e in c.visible(driver, ".modal.in, .modal.show, .swal2-modal, svg, canvas") if e.text.strip()]
    if any(name.lower() in text.lower() for text in popups):
        return True, f"Map of '{name}' is shown"
    return False, "no map showing the selected category was found"


SCENARIOS = [("See map", see_map)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
