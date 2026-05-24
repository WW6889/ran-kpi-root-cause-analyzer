# Engineering Assumptions

- The data is synthetic because real operator KPI data is confidential.
- Thresholds represent practical troubleshooting patterns, not vendor-specific acceptance criteria.
- RSRP below `-108 dBm` is treated as strong coverage evidence. RSRP between `-108 dBm` and `-105 dBm` is weak coverage evidence.
- SINR below `5 dB` with normal RSRP and low CQI is treated as likely interference.
- PRB utilization above `85%`, high active user count, high latency, and low throughput per user together indicate capacity congestion.
- Handover success below `90%` with elevated call drop rate indicates mobility degradation, especially when RRC setup remains healthy.
- Final field diagnosis would require topology, configuration history, alarms, traces, and drive-test evidence.

## KPI Relationship Notes

- Coverage and interference can both reduce throughput. The RCA engine therefore scores multiple symptoms instead of assigning causes from a single KPI.
- Low SINR with normal RSRP is a stronger interference pattern than low SINR with weak RSRP, because weak RSRP may itself reduce link quality.
- Congestion should produce load symptoms: high PRB utilization, high user count, increased latency, and low throughput per user.
- Mobility degradation should show handover/drop symptoms and should not be inferred from throughput alone.

## What This Project Does Not Claim

- It does not claim vendor-specific root-cause accuracy.
- It does not model full RF propagation or real network topology.
- It does not replace traces, drive tests, OSS counters, alarms, or configuration review.
