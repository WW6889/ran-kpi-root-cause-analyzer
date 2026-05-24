# Engineering Assumptions

- The data is synthetic because real operator KPI data is confidential.
- Thresholds represent practical troubleshooting patterns, not vendor-specific acceptance criteria.
- RSRP below `-105 dBm` combined with low throughput is treated as likely coverage limitation.
- SINR below `5 dB` with normal RSRP and low CQI is treated as likely interference.
- PRB utilization above `85%` with high active user count is treated as capacity congestion.
- Handover success below `90%` with elevated call drop rate is treated as mobility degradation.
- Final field diagnosis would require topology, configuration history, alarms, traces, and drive-test evidence.

