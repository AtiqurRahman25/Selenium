"""
DMS-TC103
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/share_document/
2. Update a "Multiple Record" master table fetch method
1. Multiple record master table method should be updated successfully & system should give proper confirmation message.
2. Multiple records should be set on the dropdown fields of the metadataa on upload documents, edit metadata, advanced search & my documents search
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC103"


def update(driver, wait):
    name = d.new_method(driver, wait, "multiple record")
    new_name = name + "_UPD"
    ok, message = d.update_method(driver, wait, name, new_name)
    return ok, f"{message} ({name} -> {new_name}). Dropdown values on the upload / search pages are not checked by the script"


SCENARIOS = [("Update multiple record method", update)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()