#!/usr/bin/env python3

import argparse
import json


def main():
    parser = argparse.ArgumentParser(
        description="Summarize a KiCad JSON DRC report for the autorouter gate"
    )
    parser.add_argument("report", help="KiCad JSON DRC report")
    args = parser.parse_args()

    with open(args.report, encoding="utf-8") as report_file:
        report = json.load(report_file)

    unconnected_items = report.get("unconnected_items", [])
    violations = report.get("violations", [])
    schematic_parity = report.get("schematic_parity", [])
    checked_violations = violations + schematic_parity

    dangling = sum(
        violation.get("type") == "track_dangling" for violation in violations
    )
    errors = sum(
        violation.get("severity") == "error" for violation in checked_violations
    )

    print(f"unconnected={len(unconnected_items)}")
    print(f"dangling={dangling}")
    print(f"errors={errors}")
    print(f"violations={len(checked_violations)}")


if __name__ == "__main__":
    main()
