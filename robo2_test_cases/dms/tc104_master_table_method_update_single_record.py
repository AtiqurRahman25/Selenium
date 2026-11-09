"""
DMS-TC104
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/share_document/
2. Update a "Single Record" master table fetch method
1. Single record master table method should be updated & system should give proper confirmation message.
2. When user try to upload documents, edit metadata, advanced search & my documents search then data should be fetched accordingly.
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC104"


def update(driver, wait):
    name = d.new_method(driver, wait, "single record")
    new_name = name + "_UPD"
    ok, message = d.update_method(driver, wait, name, new_name)
    return ok, f"{message} ({name} -> {new_name}). Fetching on the upload / search pages is not checked by the script"


SCENARIOS = [("Update single record method", update)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()