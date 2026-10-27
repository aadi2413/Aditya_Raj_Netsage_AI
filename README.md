# NetSage AI — Applied AI + Network Troubleshooting

An AI-assisted troubleshooter for Cisco-style Packet Tracer lab problems.
For each case, it takes a symptom and show-command output, and produces a
structured diagnosis (root cause, OSI layer, confidence, evidence, next
command, fix steps). Every AI answer is reviewed by a human before it's
trusted — the AI proposes, a human approves or corrects.

## Files in this folder

- **cases.csv** — the 30 troubleshooting cases (VLAN, Gateway, DHCP, DNS,
  Routing, ACL, NAT, Wireless), each with a symptom, topology note,
  show-command output, expected fault, OSI layer, and severity.
- **diagnose_prompt.md** — the exact prompt used for every case, including
  the required JSON output format and worked examples.
- **rule_checker.py** — a plain Python script (no AI) that scans the
  show-command output for common, mechanical config mistakes.
- **rule_checker_sample_output.md** — what the checker actually printed
  when run against all 30 cases.
- **Ai_analysis.xlsx** — the real AI diagnosis for all 30 cases, collected
  by pasting each case into Claude and saving its JSON reply.
- **human_review_log.csv** — the human review of all 30 AI answers:
  25 Accepted, 5 Edited (with an explanation for each correction).
- **dashboard.xlsx** — summary dashboard with category/severity/confidence
  breakdowns, AI vs human agreement rate (83.3%), and charts.

## Result summary

- 30 cases across 8 fault categories
- AI got the correct root cause on all 30 cases
- 5 answers were still edited by human review for confidence calibration
  or to improve the suggested next diagnostic step
- Final AI agreement rate: **83.3%** (25 Accepted / 5 Edited / 0 Rejected)
