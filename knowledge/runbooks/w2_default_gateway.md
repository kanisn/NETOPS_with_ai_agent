---
doc_id: RB-W2-DEFAULT-GATEWAY
version: "1.0"
tenant: common
classification: internal
source: CCS synthetic wired operations handbook
---
# Incorrect Default Gateway

Compare `default_gateway` current_value with reference_value on the affected host. A wrong gateway commonly leaves local addressing intact but makes off-subnet intranet services unreachable. Restore only the observed reference IPv4 address, then verify reachability and the remaining wired KPIs.
