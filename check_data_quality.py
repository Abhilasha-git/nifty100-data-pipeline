import subprocess
import sys


CHECKS = [
    ("Duplicate checks", "check_duplicates.py"),
    ("Cash-flow reconciliation", "check_cashflow.py"),
    ("Annual March coverage", "check_common_periods.py"),
]


def run_check(name, script):
    print("\n" + "=" * 70)
    print(name.upper())
    print("=" * 70)
    print(f"Running: python {script}\n")

    result = subprocess.run(
        [sys.executable, script],
        text=True,
    )

    if result.returncode != 0:
        print(f"\n[FAILED] {script} exited with code {result.returncode}")
        return False

    print(f"\n[PASSED] {script} completed successfully")
    return True


def main():
    print("=" * 70)
    print("DATA QUALITY VALIDATION")
    print("=" * 70)

    results = []

    for name, script in CHECKS:
        results.append((script, run_check(name, script)))

    print("\n" + "=" * 70)
    print("FINAL DATA QUALITY SUMMARY")
    print("=" * 70)

    all_passed = True

    for script, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status:>5}  {script}")

        if not passed:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("All validation scripts completed successfully.")
    else:
        print("One or more validation scripts failed.")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())