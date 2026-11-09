"""
DMS-TC124
Advanced Search (Enable Archive)
1. Click on global search arrow icon
2. Select doc type
3. Give metadata
4. Enable "Include Archive"
5. Click on "Search"
Searched result should be shown including archived docs
"""
import time

import common as c

TEST_CASE_ID = "DMS-TC124"

def include_archive(driver, wait):
    info = c.new_document(driver, wait)
    name = info["name"]
    ok, message = c.do(driver, wait, "archive", "yes")
    if not ok:
        raise c.SetupError(f"could not archive the test document ({message})")
    time.sleep(3)

    without = c.advanced_finds(driver, wait, name, doc_type=info["doc_type"])
    with_archive = c.advanced_finds(driver, wait, name, doc_type=info["doc_type"], include_archive=True)
    ok = with_archive and not without
    return ok, f"Archived document: found with Include Archive {'yes' if with_archive else 'NO'}, found without it {'YES' if without else 'no'}"


SCENARIOS = [("Include archive", include_archive)]


def main():
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
