"""
DMS-TC122
Advanced Search (Disable Match All)
1. Click on global search arrow icon
2. Select doc type
3. Give metadata
4. Disable "Match All"
5. Click on "Search"
System should show all documents which matched any meta field data. Maximum matched data should show first
"""
import common as c
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC122"

def advanced(driver, wait):
    first = c.upload_document(driver, wait, "pdf")
    second = c.upload_document(driver, wait, "pdf")
    if len(first["values"]) >= 2 and len(second["values"]) >= 2:
        # field 1 has the value of the first document, field 2 has the value of the second one
        pairs = [(first["values"][0][0], first["values"][0][1]), (second["values"][1][0], second["values"][1][1])]
        name = None
    elif first["values"] and second["values"]:
        pairs = [(second["values"][0][0], second["values"][0][1])]
        name = first["name"]  # document name of the first + meta-data of the second
    else:
        raise c.SetupError("the doc-type has no text meta-data to search with")

    driver.get(c.EXPLORER_URL)
    c.advanced_search(driver, wait, name, match_all=False, doc_type=first["doc_type"], extra=pairs)
    text = h.body_text(driver)
    found_a = first["name"].lower() in text
    found_b = second["name"].lower() in text
    ok = found_a and found_b
    return ok, f"Match All off: first document {'shown' if found_a else 'not shown'}, second document {'shown' if found_b else 'not shown'} (expected both documents)"


SCENARIOS = [("Match All disabled", advanced)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
