"""
DMS-TC021
Cancel Checkout Doc
1. Open a document that is checked-out
2. Click on "cancel check out"
3. Click on "Yes" button
1. Document should be checked in with proper confirmation message.
2. Check-out icon shouldn't show in explorer view for admin & the user whom do the check out.
(admin only: the second user part is not tested here)
"""
import common as c

TEST_CASE_ID = "DMS-TC021"


def cancel_check_out(driver, wait):
    info = c.upload_document(driver, wait)
    name = info["name"]

    c.open_document(driver, wait, name)
    ok, message = c.do(driver, wait, "check out", "yes")
    if not ok:
        raise c.SetupError(f"could not check out the test document ({message})")

    c.open_document(driver, wait, name)
    ok, message = c.do(driver, wait, "cancel check out", "yes")
    if not ok:
        return False, message

    driver.get(c.CHECKOUT_URL)
    still_listed = c.wait_text(driver, name, 4)
    return (not still_listed), (f"{message}. Removed from Checked Out Documents: {'yes' if not still_listed else 'NO'}")


SCENARIOS = [("Cancel check-out", cancel_check_out)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()