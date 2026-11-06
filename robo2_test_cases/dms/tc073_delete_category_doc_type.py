"""
DMS-TC073
Delete Category/Doc Type
1. Go to https://ecmv6.robo2mation.com/dms/document/root
2. Select a category/doc-type that doesn't have any document uploaded
3. Click on delete
Category/doc-type should be deleted with confirmation message
"""
import common as c
import dms_helper as d

TEST_CASE_ID = "DMS-TC073"

def delete_doc_type(driver, wait):
    name = d.new_doc_type(driver, wait)  # a new doc-type has no document
    ok, message = d.delete_category(driver, wait, name)
    return ok, f"{message} ({name})"


SCENARIOS = [("Delete doc-type", delete_doc_type)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
