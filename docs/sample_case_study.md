# Sample Case Study

## Scenario

`Cell_004` and `Cell_009` show throughput degradation during busy-hour windows.

## Observation

The report flags high PRB utilization, high active users, increased latency, and lower throughput per user.

## Root Cause

The likely root cause is capacity congestion rather than weak coverage. RSRP and SINR remain within normal operating ranges while load-related KPIs degrade.

## Recommended Checks

- Verify traffic distribution across neighboring cells.
- Inspect scheduler behavior during busy hour.
- Review load-balancing parameters and recent configuration changes.
- Check whether carrier expansion, sector split, or capacity tuning is justified.
