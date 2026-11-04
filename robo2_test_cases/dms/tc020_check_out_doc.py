"""
DMS-TC020
Check-Out Doc
1. Open a document
2. Click on check out
3. Click on "Yes" button
1. Document should be checked out with proper confirmation message.
2. A check-out icon should show in explorer view for admin & the user whom do the check out.
(admin only: the second user part is not tested here)
"""
import common as c

TEST_CASE_ID = "DMS-TC020"


def check_out(driver, wait):
    info = c.upload_document(driver, wait)
    name = info["name"]

    c.open_document(driver, wait, name)
    ok, message = c.do(driver, wait, "check out", "yes")
    if not ok:
        return False, message

    driver.get(c.CHECKOUT_URL)
    in_list = c.wait_text(driver, name)
    return in_list, f"{message}. Shown in Checked Out Documents: {'yes' if in_list else 'NO'}"


SCENARIOS = [("Check-out", check_out)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()