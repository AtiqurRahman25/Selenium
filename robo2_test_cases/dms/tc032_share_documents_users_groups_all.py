"""
DMS-TC032
Share Documents (Users)
1. Go to "Pending Documents/Document View" page 
2. Select single/multiple users
3. Click on "Share" button
Documents should be shared with selected users.

Share Documents (Groups)
1. Go to "Pending Documents/Document View" page 
2. Select single/multiple groups
3. Click on "Share" button
Documents should be shared with selected group users.

Share Documents (All User)
1. Go to "Pending Documents/Document View" page 
2. Select all user
3. Click on "Share" button
Documents should be shared with all users.
"""
import re
import openpyxl
from datetime import datetime
import common as c

TEST_CASE_ID = "DMS-TC032"


def run_three_rows(test_case_id, scenarios):
    """Custom runner for DMS-TC032 that writes each scenario result to its own consecutive Excel row."""
    c.check_excel_ready(test_case_id)
    wb = openpyxl.load_workbook(c.EXCEL_PATH)
    ws = wb[c.SHEET_NAME]
    
    # Find base row for DMS-TC032 in column A
    base_row, columns = c.find_row_and_columns(ws, test_case_id)
    if base_row is None:
        raise SystemExit(f"{test_case_id} not found in column A of sheet '{c.SHEET_NAME}'")

    driver, wait = c.start_browser()
    try:
        c.login(driver, wait)
        for idx, (label, scenario) in enumerate(scenarios):
            target_row = base_row + idx  # row 1, row 2, row 3 for Users, Groups, All users
            slug = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
            try:
                ok, msg = scenario(driver, wait)
            except c.SetupError as error:
                ok, msg = False, str(error)
                c.fail(driver, test_case_id, slug, str(error))
                break
            except Exception as error:
                ok, msg = False, c.short(error)
                c.fail(driver, test_case_id, slug, msg)

            if ok:
                c.save_shot(driver, test_case_id, slug, "PASS")
            else:
                ok, msg = c.fail(driver, test_case_id, slug, msg)

            status = "Pass" if ok else "Fail"
            print(f"{label:28} -> {status} ({msg})")

            # Write individual result to its respective row
            if columns["actual"]:
                ws.cell(target_row, columns["actual"]).value = msg
            if columns["status"]:
                ws.cell(target_row, columns["status"]).value = status
            if columns["evidence"]:
                cell = ws.cell(target_row, columns["evidence"])
                cell.value = "Evidence Doc"
                if c.EVIDENCE_LINK:
                    cell.hyperlink = c.EVIDENCE_LINK
                    cell.style = "Hyperlink"
            if columns["date"]:
                ws.cell(target_row, columns["date"]).value = datetime.now().strftime("%d-%b-%Y")
            if columns["tester"]:
                ws.cell(target_row, columns["tester"]).value = c.TESTER_NAME

        wb.save(c.EXCEL_PATH)
        print(f"\nSaved results across 3 rows starting from row {base_row} to: {c.EXCEL_PATH}")
    finally:
        driver.quit()


def share_with(kind):
    def scenario(driver, wait):
        info = c.upload_document(driver, wait, "pdf", share=kind)
        found = c.search_finds(driver, wait, info["name"], tries=3)
        if not found:
            return False, f"Uploaded with Share With '{info['shared_with']}', but document '{info['name']}' was not found in search"
        return True, f"Document '{info['name']}' uploaded and shared with '{info['shared_with']}' successfully"
    return scenario


SCENARIOS = [
    ("Users", share_with("users")),
    ("Groups", share_with("groups")),
    ("All users", share_with("all users")),
]


def main():
    run_three_rows(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()