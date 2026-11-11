---
doc_id: RB-W5-EXCESSIVE-DELAY
version: "1.0"
tenant: common
classification: internal
source: CCS synthetic wired operations handbook
---
# Excessive Delay and Video Meeting Lag

High path delay causes visible video-meeting lag and can reduce effective throughput. Compare `delay_ms` with its reference and correlate it with `latency_ms`. Restore the reference TCLink delay only after excluding a failed path, then verify latency is at most 30 ms and all other KPIs pass.
