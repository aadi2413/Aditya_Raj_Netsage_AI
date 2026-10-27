# Rule Checker — What It Is and Its Sample Output

## What this is

`rule_checker.py` is a plain Python script — **no AI involved at all**. It
scans the raw show-command text in each case and looks for a handful of
common, mechanical Cisco config mistakes using simple pattern matching:

| Check | What it looks for |
|---|---|
| `duplicate_ip` | The same IP address assigned to two different places |
| `wrong_mask` | A subnet mask that isn't a valid value |
| `gateway_mismatch` | A host's gateway address isn't in the same /24 as its own IP |
| `interface_down` | Any interface reported down/down or administratively down |
| `missing_vlan` | An access port still sitting on VLAN 1 (default) |
| `missing_route_or_helper` | Show output text noting an absent route, DHCP helper, or NAT statement |

This exists as a second, independent signal alongside the AI diagnosis —
it's deterministic (same input always gives the same output, no randomness,
no AI judgment involved), which is exactly what the brief means by
"Python script with deterministic checks."

## How it was run

```
python3 rule_checker.py cases.csv
```

## Actual output (real run against the 30-case dataset)

```
CASE    CHECKS TRIGGERED
----------------------------------------------------------------------
C001    missing_vlan
C002    -
C003    -
C004    -
C005    -
C006    interface_down
C007    -
C008    -
C009    missing_route_or_helper
C010    missing_route_or_helper
C011    -
C012    -
C013    -
C014    missing_route_or_helper
C015    -
C016    -
C017    missing_route_or_helper
C018    -
C019    -
C020    -
C021    -
C022    -
C023    missing_route_or_helper
C024    -
C025    -
C026    -
C027    -
C028    -
C029    -
C030    -

Summary (# cases where each check fired):
  missing_vlan                1
  interface_down              1
  missing_route_or_helper     5

7/30 cases had at least one deterministic check fire.
```

## How to read this

A dash (`-`) means none of the simple mechanical checks fired for that
case — that's expected and fine. Not every fault (e.g. a WPA2 password
mismatch, an ACL ordering problem) is something a basic text-pattern check
can catch; those need the AI's reasoning instead. The rule checker's job is
only to catch the *obvious, mechanical* stuff instantly, without needing AI
at all — which it did for 7 of the 30 cases here (VLAN 1 defaults,
downed interfaces, and missing route/helper/NAT statements).
