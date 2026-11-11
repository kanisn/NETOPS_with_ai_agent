---
doc_id: RB-W4-BANDWIDTH-CAP
version: "1.0"
tenant: common
classification: internal
source: CCS synthetic wired operations handbook
---
# Bandwidth Cap and Slow File Copy

A low `bandwidth_mbps` setting limits bulk transfers such as file copies. Confirm the current/reference mismatch and degraded `throughput_mbps`; do not infer a cap from latency alone. Restore only the reference bandwidth, then verify throughput is at least 80 Mbps.
