"""
DMS-TC105
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/share_document/
2. Delete a master table fetch method
1. Master table method should be deleted & system should give proper confirmation message.
2. Single record won't be fetched & multiple record won't be set for the deleted methods.
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC105"


def delete_method(driver, wait):
    name = d.new_method(driver, wait)
    ok, message = d.delete_method(driver, wait, name)
    return ok, f"{message} ({name}). Fetching on the upload / search pages is not checked by the script"


SCENARIOS = [("Delete method", delete_method)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()