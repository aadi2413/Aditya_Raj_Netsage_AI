"""
rule_checker.py — Deterministic (non-AI) checks over show-command output.

This is intentionally simple regex/string matching, NOT an AI call. Its job
is to catch the obvious, mechanical mistakes so the AI diagnosis has a
second, independent signal to be checked against (and so cases_project can
show "AI vs rule-checker vs human" agreement).

Usage:
    python3 rule_checker.py ../data/cases.csv
    python3 rule_checker.py ../data/cases.csv --json   # machine-readable output
"""
import csv
import re
import sys
import json
import argparse
from collections import defaultdict


def check_duplicate_ip(text):
    """Flag if the same IPv4 address appears assigned to two different interfaces/hosts."""
    ips = re.findall(r"ip address (\d+\.\d+\.\d+\.\d+)", text, re.IGNORECASE)
    ips += re.findall(r"IP Address:\s*(\d+\.\d+\.\d+\.\d+)", text, re.IGNORECASE)
    dupes = [ip for ip in set(ips) if ips.count(ip) > 1]
    if dupes:
        return f"Duplicate IP address detected: {', '.join(dupes)}"
    return None


def check_wrong_mask(text):
    """Flag masks that aren't valid contiguous subnet masks."""
    masks = re.findall(r"255(?:\.\d{1,3}){3}|0\.0\.0\.0", text)
    valid_masks = {
        "255.255.255.255", "255.255.255.254", "255.255.255.252",
        "255.255.255.248", "255.255.255.240", "255.255.255.224",
        "255.255.255.192", "255.255.255.128", "255.255.255.0",
        "255.255.254.0", "255.255.252.0", "255.255.248.0",
        "255.255.240.0", "255.255.224.0", "255.255.192.0",
        "255.255.128.0", "255.255.0.0", "255.0.0.0",
    }
    bad = [m for m in masks if m not in valid_masks and m != "0.0.0.0"]
    if bad:
        return f"Non-standard / invalid subnet mask found: {', '.join(set(bad))}"
    return None


def check_gateway_mismatch(text):
    """Flag when a host's Default Gateway doesn't fall in the same /24 as its own IP (heuristic)."""
    ip_match = re.search(r"IP Address:\s*(\d+\.\d+\.\d+\.\d+)", text)
    gw_match = re.search(r"Default Gateway:\s*(\d+\.\d+\.\d+\.\d+)", text)
    if ip_match and gw_match:
        ip_parts = ip_match.group(1).split(".")
        gw_parts = gw_match.group(1).split(".")
        if ip_parts[:3] != gw_parts[:3]:
            return f"Gateway {gw_match.group(1)} is not in the same /24 as host IP {ip_match.group(1)}"
    return None


def check_interface_down(text):
    """Flag interfaces reported down/down or administratively down."""
    hits = re.findall(r"(\S+)\s+\S+\s+(administratively down|down)\s+down", text, re.IGNORECASE)
    if hits:
        names = ", ".join(sorted(set(h[0] for h in hits)))
        return f"Interface(s) reported down: {names}"
    return None


def check_missing_vlan(text):
    """Flag when an access port is on VLAN 1 (default) — common misconfig, not always wrong but worth a flag."""
    if re.search(r"Access Mode VLAN:\s*1\s*\(default\)", text, re.IGNORECASE):
        return "Access port left on VLAN 1 (default) — verify this is intentional"
    return None


def check_missing_route(text):
    """Flag explicit comments in the sample output noting an absent route/helper/nat statement."""
    hints = re.findall(r"(no [\w '\.-]*(route|helper-address|nat inside|nat outside|default-router)[\w '\.-]*)",
                        text, re.IGNORECASE)
    if hints:
        return "Missing configuration noted: " + "; ".join(sorted(set(h[0].strip() for h in hints)))
    return None


CHECKS = [
    ("duplicate_ip", check_duplicate_ip),
    ("wrong_mask", check_wrong_mask),
    ("gateway_mismatch", check_gateway_mismatch),
    ("interface_down", check_interface_down),
    ("missing_vlan", check_missing_vlan),
    ("missing_route_or_helper", check_missing_route),
]


def run_checks_on_case(row):
    text = row.get("show_command_output", "") or ""
    findings = {}
    for name, fn in CHECKS:
        result = fn(text)
        if result:
            findings[name] = result
    return findings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cases_csv", help="Path to cases.csv")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON instead of a table")
    args = parser.parse_args()

    with open(args.cases_csv, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    all_results = []
    summary = defaultdict(int)

    for row in rows:
        findings = run_checks_on_case(row)
        all_results.append({"case_id": row["case_id"], "findings": findings})
        for key in findings:
            summary[key] += 1

    if args.json:
        print(json.dumps({"results": all_results, "summary": summary}, indent=2))
    else:
        print(f"{'CASE':<8}{'CHECKS TRIGGERED'}")
        print("-" * 70)
        for r in all_results:
            flags = ", ".join(r["findings"].keys()) if r["findings"] else "-"
            print(f"{r['case_id']:<8}{flags}")
        print("\nSummary (# cases where each check fired):")
        for key, count in summary.items():
            print(f"  {key:<28}{count}")
        cases_with_hits = sum(1 for r in all_results if r["findings"])
        print(f"\n{cases_with_hits}/{len(rows)} cases had at least one deterministic check fire.")


if __name__ == "__main__":
    main()
