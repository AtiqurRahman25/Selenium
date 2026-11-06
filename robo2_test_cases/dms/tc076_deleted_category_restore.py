"""
DMS-TC076
Deleted Category Restore
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category/doc-type
3. Click on "Restore Now"
4. Click on "Yes" on confirmation modal
Selected category/doc-type should be restored
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC076"

def restore_category(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)
    d.select_tree_item(driver, wait, name)
    ok, message = c.do(driver, wait, "restore now", "yes")
    if not ok:
        return False, message
    driver.get(c.ROOT_URL)
    back = c.wait_text(driver, name)
    return back, f"{message}. '{name}' " + ("is back in Categorization" if back else "is NOT back in Categorization")


SCENARIOS = [("Restore category", restore_category)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
