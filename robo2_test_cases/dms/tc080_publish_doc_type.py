"""
DMS-TC080
Publish Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a doc-type
3. Click on "publish" button
4. Select "published"
5. Click on "Save" button
1. Document type should be published with confirmation message
2. Document type should be accessible from permitted general user
"""
import time

import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC080"

def publish(driver, wait):
    name = d.new_doc_type(driver, wait)
    driver.get(c.ROOT_URL)
    d.select_tree_item(driver, wait, name)
    c.click_label(driver, wait, "publish")
    time.sleep(1)
    c.click_label(driver, wait, "published")
    ok, message = c.do(driver, wait, "save")
    return ok, f"{message} ({name}). Access for a permitted general user is not checked by the script"


SCENARIOS = [("Publish doc-type", publish)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
