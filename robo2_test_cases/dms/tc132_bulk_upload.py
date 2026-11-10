"""
DMS-TC132
Bulk Upload
1. Go to https://ecmv6.robo2mation.com/dms/document/upload/bulk-upload/
2. Follow bulk upload steps and upload files (1MB-20MB)
3. Observe the file uploading and the upload record report
Document bulk upload should be done without any errors with the correct data
"""
import os
import random
import time
from datetime import datetime

from selenium.webdriver.common.by import By

import common as c
import dms_helper as d
import tc011_Multiple_Doc_Up_helper as h

TEST_CASE_ID = "DMS-TC132"

DOC_TYPE = os.getenv("BULK_DOC_TYPE")  # search text of a doc-type for bulk upload


def prepare_sample_file(ext, min_mb=1.1):
    """Make a unique copy of a sample file and ensure its size is within 1MB-20MB."""
    sample = c.find_sample_file(ext)
    if not sample:
        raise c.SetupError(f"no .{ext} sample file in {c.SAMPLE_DIR}")
    _, path = c.unique_copy(sample[1])
    sz = os.path.getsize(path)
    target_bytes = int(min_mb * 1024 * 1024)
    if sz < target_bytes:
        with open(path, "ab") as f:
            f.write(b"0" * (target_bytes - sz))
    return path


def fetch_metadata_and_unique_values(driver, doc_id):
    """Retrieve metadata field definitions and existing unique values for the doc-type."""
    script = """
    var callback = arguments[arguments.length - 1];
    var docId = arguments[0];
    Promise.all([
        fetch('/api/v1/dms/categorization/metafield/?doc_id=' + docId).then(r => r.json()),
        fetch('/api/v1/dms/documents/metadata_value/?doc_id=' + docId).then(r => r.json())
    ]).then(([meta, unique_vals]) => {
        callback({meta: meta, unique_vals: unique_vals});
    }).catch(err => callback({error: err.toString()}));
    """
    driver.set_script_timeout(15)
    info = driver.execute_async_script(script, doc_id)
    fields = {f["title"].lower(): f for f in info.get("meta", [])}
    unique_vals = info.get("unique_vals", {})
    return fields, unique_vals


def build_row(header, number, path, run_id, meta_fields, used_unique):
    """Generate a single CSV row with valid types matching the metadata definitions."""
    row = []
    for i, col in enumerate(header):
        clow = col.strip().lower()
        if "file" in clow:
            row.append(os.path.basename(path))
        elif clow == "status":
            row.append("")
        elif clow == "document_name":
            row.append(f"AUTO_BULK_{run_id}_{number}")
        elif clow in meta_fields:
            mf = meta_fields[clow]
            dtype = mf.get("data_type")
            is_unique = bool(mf.get("unique"))
            field_title = mf.get("title")

            if dtype == 1:  # Integer
                val = str(random.randint(100000, 999999))
                if is_unique:
                    while val in used_unique.get(field_title, set()):
                        val = str(random.randint(100000, 999999))
                    used_unique.setdefault(field_title, set()).add(val)
                row.append(val)
            elif dtype == 5:  # Decimal / Float
                val = f"{random.randint(10000, 99999)}.{random.randint(10, 99)}"
                if is_unique:
                    while val in used_unique.get(field_title, set()):
                        val = f"{random.randint(10000, 99999)}.{random.randint(10, 99)}"
                    used_unique.setdefault(field_title, set()).add(val)
                row.append(val)
            elif dtype == 3:  # Dropdown
                options = [line.strip() for line in (mf.get("default_text") or "").splitlines() if line.strip()]
                if not options:
                    options = ["A", "B", "C"]
                val = None
                for _ in range(100):
                    k = min(len(options), random.randint(2, 5) if mf.get("multiselect") else 1)
                    cand = ",".join(sorted(random.sample(options, k)))
                    if not is_unique or cand not in used_unique.get(field_title, set()):
                        val = cand
                        break
                if not val:
                    val = options[0]
                if is_unique:
                    used_unique.setdefault(field_title, set()).add(val)
                row.append(val)
            elif dtype == 4:  # Date
                row.append(datetime.now().strftime("%m/%d/%Y"))
            else:  # String / others
                mx = mf.get("max") or 20
                val = f"AUTO_{run_id}_{number}"[:mx]
                if is_unique:
                    while val in used_unique.get(field_title, set()):
                        val = f"A{random.randint(1000, 9999)}_{number}"[:mx]
                    used_unique.setdefault(field_title, set()).add(val)
                row.append(val)
        else:
            row.append(f"AUTO_{run_id}_{number}_{i}")
    return row


def bulk_upload(driver, wait):
    template = d.download_template(driver, wait, DOC_TYPE)
    header = d.template_header(template)
    doc_id = driver.find_element(By.ID, "document_type_bulk_upload").get_attribute("value")
    meta_fields, unique_vals = fetch_metadata_and_unique_values(driver, doc_id)

    run_id = datetime.now().strftime("%H%M%S")
    files = [prepare_sample_file(ext, min_mb=1.1) for ext in ["pdf", "ppt", "docx"]]

    used_unique = {k: set(str(v) for v in vals if v is not None) for k, vals in unique_vals.items()}
    rows = [build_row(header, idx, path, run_id, meta_fields, used_unique) for idx, path in enumerate(files)]

    csv_path = d.write_csv(os.path.join(c.DOWNLOAD_DIR, "AUTO_bulk.csv"), header, rows)
    ok, message = d.bulk_submit(driver, wait, DOC_TYPE, csv_path, files)
    time.sleep(5)
    report_error = "error" in h.body_text(driver)
    return ok and not report_error, f"{message}. " + ("Upload record shows an error" if report_error else "No error shown")


SCENARIOS = [("Bulk upload", bulk_upload)]


def main():
    c.need_env("BULK_DOC_TYPE", "(search text of a doc-type for bulk upload)")
    c.run(TEST_CASE_ID, SCENARIOS)


if __name__ == "__main__":
    main()
