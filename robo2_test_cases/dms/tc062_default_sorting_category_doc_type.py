"""
DMS-TC062
Default Sorting on My Docments Category/Doc-Type
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
By default category/doc-type should be shown as name wise ascending
"""
import re
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import common as c
import explorer_helper as e

TEST_CASE_ID = "DMS-TC062"


def sort_key(name):
    """The way the app orders names: lower case, spaces and symbols ignored."""
    return re.sub(r"[^a-z0-9]", "", name.lower())


def category_sorting(driver, wait):
    driver.get(c.EXPLORER_URL)
    tree = wait.until(EC.presence_of_element_located((By.ID, e.TREE)))
    WebDriverWait(driver, 30).until(lambda drv: e.child_anchors(tree))  # tree items load by AJAX
    time.sleep(2)

    names = [e.name_of(a) for a in e.child_anchors(tree)]  # first level of the tree only
    if len(names) < 2:
        return False, f"only {len(names)} category / doc-type names found on the page"

    for i in range(len(names) - 1):
        if sort_key(names[i]) > sort_key(names[i + 1]):
            return False, f"NOT sorted by name ascending: '{names[i]}' is shown before '{names[i + 1]}'. {len(names)} names checked"
    return True, f"{len(names)} categories / doc-types checked: sorted by name ascending"


SCENARIOS = [("Default category sorting", category_sorting)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()