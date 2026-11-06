"""
DMS-TC081
Assign Access Group in Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "Assign Group" button
4. Select one or  multiple groups in "Access Groups" field
5. Click on "Save" button
1. Selected groups should be assigned in document type with confirmation message
2. Document type should be accessible for the user of assigned groups
"""
import time

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC081"

def assign(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)
    c.click_label(driver, wait, "assign group")
    time.sleep(1)
    group = c.pick_option(driver, "access groups")
    ok, message = c.do(driver, wait, "save")
    return ok, f"{message} ({name}, group '{group}')"


SCENARIOS = [("Assign access group", assign)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
