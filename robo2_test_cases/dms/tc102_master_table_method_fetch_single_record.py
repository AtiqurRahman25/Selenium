"""
DMS-TC102
Master Table Method (Fetch)
1. Go to https://ecmv6.robo2mation.com/dms/document/settings/share_document/
2. Click on "Add Method" icon
3. Create a "Single Record" master table fetch method
1. Single record master table method should be created successfully & system should give proper confirmation message.
2. When user try to upload documents, edit metadata, advanced search & my documents search then data should be fetched accordingly.
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC102"

def single_record(driver, wait):
    ok, message, name = d.create_method(driver, wait, "single record")
    return ok, f"{message} ({name}). Data fetching on the upload / search pages is not checked by the script"


SCENARIOS = [("Single record method", single_record)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
