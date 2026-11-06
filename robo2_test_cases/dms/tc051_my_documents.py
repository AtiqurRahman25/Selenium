"""
DMS-TC051
My Documents
1. Go to https://ecmv6.robo2mation.com/dms/document/explorer/
Only permitted sub category/doc-type should be shown for general user
"""
import os
import time

import common as c
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC051"

VISIBLE_TYPE = os.getenv("OTHER_USER_VISIBLE_DOC_TYPE")  # a doc-type the general user is permitted to see
HIDDEN_TYPE = os.getenv("OTHER_USER_HIDDEN_DOC_TYPE")    # a doc-type the general user is NOT permitted to see


def permitted_only(driver, wait):
    def look():
        driver.get(c.EXPLORER_URL)
        time.sleep(4)
        return h.body_text(driver)
    text = c.as_other_user(driver, wait, look)
    sees_visible = VISIBLE_TYPE.lower() in text
    sees_hidden = HIDDEN_TYPE.lower() in text
    ok = sees_visible and not sees_hidden
    return ok, f"General user sees '{VISIBLE_TYPE}': {'yes' if sees_visible else 'NO'}. Sees '{HIDDEN_TYPE}': {'YES' if sees_hidden else 'no'}"


SCENARIOS = [("Permitted doc-types only", permitted_only)]


def main():
    c.need_other_user()
    c.need_env("OTHER_USER_VISIBLE_DOC_TYPE", "(a doc-type the second user can see)")
    c.need_env("OTHER_USER_HIDDEN_DOC_TYPE", "(a doc-type the second user can not see)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()

