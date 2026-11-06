"""
DMS-TC077
Deleted Category Permanent Deletion
1. Go to https://ecmv6.robo2mation.com/dms/document/deleted-root
2. Select a category/doc-type
3. Click on "Delete Permanently"
4. Click on "Yes" on confirmation modal
Selected category/doc-type should be permanently deleted
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC077"

def delete_permanently(driver, wait):
    name = d.new_doc_type(driver, wait)
    ok, message = d.delete_category(driver, wait, name)
    if not ok:
        raise c.SetupError(f"could not delete the doc-type ({message})")

    driver.get(c.DELETED_ROOT_URL)
    d.select_tree_item(driver, wait, name)
    ok, message = c.do(driver, wait, "delete permanently", "yes")
    if not ok:
        return False, message
    driver.get(c.DELETED_ROOT_URL)
    still_there = c.wait_text(driver, name, 4)
    return (not still_there), f"{message}. '{name}' " + ("is STILL in the deleted list" if still_there else "is gone from the deleted list")


SCENARIOS = [("Delete permanently", delete_permanently)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
