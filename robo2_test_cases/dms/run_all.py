"""
Run the DMS test scripts one after another, with one terminal command.

    python run_all.py                 run every tcXXX_*.py file
    python run_all.py tc014 tc022     run only the files whose name starts with these

Each test runs in its own process (its own Chrome window), so one broken test
cannot stop the others. Output of every test is saved in logs/<test file>.log
Keep the Excel file closed while this runs.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
LOG_DIR = FOLDER / "logs"
TIMEOUT_SECONDS = 600  # give up on one test after 10 minutes


def find_tests(filters):
    files = sorted(FOLDER.glob("tc*.py"))
    files = [f for f in files if not f.stem.endswith("_helper")]  # helpers are not tests
    if filters:
        files = [f for f in files if any(f.name.startswith(text) for text in filters)]
    return files


def run_one(file):
    """Run one test file. Returns (status, seconds)."""
    log_path = LOG_DIR / f"{file.stem}.log"
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}  # page text can contain special characters
    start = time.time()
    with open(log_path, "w", encoding="utf-8") as log:
        try:
            result = subprocess.run(
                [sys.executable, file.name],
                cwd=FOLDER, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=TIMEOUT_SECONDS,
            )
            status = "PASS" if result.returncode == 0 else "FAIL"
        except subprocess.TimeoutExpired:
            status = "TIMEOUT"
    return status, time.time() - start


def main():
    tests = find_tests(sys.argv[1:])
    if not tests:
        print("No test files found.")
        return 1

    LOG_DIR.mkdir(exist_ok=True)
    print(f"Running {len(tests)} test(s). Logs are in: {LOG_DIR}\n")

    results = []
    for number, file in enumerate(tests, start=1):
        print(f"[{number}/{len(tests)}] {file.stem} ... ", end="", flush=True)
        status, seconds = run_one(file)
        print(f"{status} ({seconds:.0f}s)")
        results.append((file.stem, status))

    not_passed = [(name, status) for name, status in results if status != "PASS"]
    print(f"\nPassed: {len(results) - len(not_passed)}   Not passed: {len(not_passed)}")
    for name, status in not_passed:
        print(f"  {status:8} {name}   (see logs/{name}.log)")

    return 1 if not_passed else 0


if __name__ == "__main__":
    sys.exit(main())