"""
DMS Test Suite Runner
Runs all DMS Selenium test cases sequentially in isolated subprocesses.

Usage:
    # Run all DMS tests:
    python run_all_dms_tests.py

    # Preview tests that will run (without executing them):
    python run_all_dms_tests.py --dry-run

    # Start from a specific test case number (e.g. tc120 onwards):
    python run_all_dms_tests.py --start-from 120

    # Run only specific test cases:
    python run_all_dms_tests.py --only tc136 tc137 tc139

    # Skip specific test cases:
    python run_all_dms_tests.py --skip tc002 tc003
"""

import argparse
import os
import re
import subprocess
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def extract_tc_number(filename: str) -> int:
    """Extract numeric part of tc filename (e.g., 'tc042_...' -> 42)."""
    match = re.search(r"tc(\d+)", filename, re.IGNORECASE)
    return int(match.group(1)) if match else 999999


def discover_test_files() -> list[str]:
    """Find all runnable DMS test case files sorted numerically."""
    test_files = []
    for entry in os.listdir(SCRIPT_DIR):
        if not entry.endswith(".py"):
            continue
        lower = entry.lower()
        if not lower.startswith("tc"):
            continue
        if "helper" in lower:
            continue
        test_files.append(entry)

    test_files.sort(key=lambda f: (extract_tc_number(f), f))
    return test_files


def run_test(test_file: str) -> tuple[str, float, str]:
    """
    Run a single test script in an isolated subprocess.
    Returns: (status, duration_seconds, summary_snippet)
    """
    full_path = os.path.join(SCRIPT_DIR, test_file)
    cmd = [sys.executable, full_path]

    start_time = time.time()
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=SCRIPT_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding="utf-8",
            errors="replace",
        )

        output_lines = []
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            output_lines.append(line)

        proc.wait()
        duration = time.time() - start_time
        full_output = "".join(output_lines)

        # Determine status
        if proc.returncode != 0:
            status = "ERROR"
            snippet = f"Exit code {proc.returncode}"
        elif "-> FAIL" in full_output or ": Fail" in full_output:
            status = "FAIL"
            # Extract fail message if available
            fail_lines = [l.strip() for l in output_lines if "-> FAIL" in l or ": Fail" in l]
            snippet = fail_lines[-1] if fail_lines else "Test reported Fail"
        elif "-> PASS" in full_output or ": Pass" in full_output:
            status = "PASS"
            pass_lines = [l.strip() for l in output_lines if "-> PASS" in l or ": Pass" in l]
            snippet = pass_lines[-1] if pass_lines else "Test passed"
        else:
            status = "PASS"
            snippet = "Completed successfully"

        return status, duration, snippet

    except KeyboardInterrupt:
        raise
    except Exception as exc:
        duration = time.time() - start_time
        return "ERROR", duration, f"Execution failed: {exc}"


def parse_args():
    parser = argparse.ArgumentParser(description="Run all or selected DMS test cases.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List all test cases that would run without executing them.",
    )
    parser.add_argument(
        "--start-from",
        "-s",
        type=int,
        default=None,
        help="Start executing from this test case number (e.g. 120 for tc120).",
    )
    parser.add_argument(
        "--from-tc",
        type=str,
        default=None,
        help="Start executing from this test filename or prefix (e.g. tc120).",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        default=None,
        help="Run only specified test files or prefixes (e.g. tc136 tc137).",
    )
    parser.add_argument(
        "--skip",
        nargs="+",
        default=None,
        help="Skip specified test files or prefixes (e.g. tc002).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    all_tests = discover_test_files()

    if not all_tests:
        print("[!] No test files found in DMS directory.")
        return 1

    selected_tests = all_tests

    # Filter: --only
    if args.only:
        targets = [t.lower() for t in args.only]
        selected_tests = [
            f for f in selected_tests if any(t in f.lower() for t in targets)
        ]

    # Filter: --skip
    if args.skip:
        skips = [s.lower() for s in args.skip]
        selected_tests = [
            f for f in selected_tests if not any(s in f.lower() for s in skips)
        ]

    # Filter: --start-from
    if args.start_from is not None:
        selected_tests = [
            f for f in selected_tests if extract_tc_number(f) >= args.start_from
        ]

    # Filter: --from-tc
    if args.from_tc:
        from_str = args.from_tc.lower()
        idx = next((i for i, f in enumerate(selected_tests) if from_str in f.lower()), None)
        if idx is not None:
            selected_tests = selected_tests[idx:]
        else:
            print(f"[!] Test matching '{args.from_tc}' not found.")
            return 1

    print("=" * 80)
    print(f" DMS TEST SUITE RUNNER")
    print(f" Total Tests Selected: {len(selected_tests)} of {len(all_tests)} total")
    print("=" * 80)

    if args.dry_run:
        print("\n[DRY RUN] Selected test files:")
        for idx, f in enumerate(selected_tests, 1):
            print(f"  {idx:2d}. {f}")
        print("\nDry run completed.")
        return 0

    results = []
    overall_start = time.time()

    try:
        for idx, test_file in enumerate(selected_tests, 1):
            header = f"[{idx}/{len(selected_tests)}] Running: {test_file}"
            print("\n" + "-" * 80)
            print(header)
            print("-" * 80)

            status, duration, snippet = run_test(test_file)
            results.append((test_file, status, duration, snippet))

            print(f"--> {test_file} finished in {duration:.1f}s: [{status}]")

    except KeyboardInterrupt:
        print("\n[!] Test run aborted by user (KeyboardInterrupt).")

    overall_duration = time.time() - overall_start

    # Final Summary Report
    print("\n" + "=" * 80)
    print(" DMS TEST SUITE - EXECUTION SUMMARY")
    print("=" * 80)
    print(f"{'#':<4} {'Test File':<45} {'Status':<8} {'Time':<8}")
    print("-" * 80)

    pass_count = sum(1 for _, st, _, _ in results if st == "PASS")
    fail_count = sum(1 for _, st, _, _ in results if st == "FAIL")
    error_count = sum(1 for _, st, _, _ in results if st == "ERROR")

    for idx, (f, st, dur, _) in enumerate(results, 1):
        print(f"{idx:<4} {f:<45} {st:<8} {dur:>6.1f}s")

    print("=" * 80)
    total_run = len(results)
    mins = int(overall_duration // 60)
    secs = int(overall_duration % 60)
    print(
        f"Ran: {total_run} | Passed: {pass_count} | Failed: {fail_count} | Errors: {error_count}"
    )
    print(f"Total Execution Time: {mins}m {secs}s")
    print("=" * 80)

    return 0 if (fail_count == 0 and error_count == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
