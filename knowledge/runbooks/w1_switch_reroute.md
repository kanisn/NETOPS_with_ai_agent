---
doc_id: RB-W1-SWITCH-REROUTE
version: "1.0"
tenant: common
classification: internal
source: CCS synthetic wired operations handbook
---
# Intermediate Switch Failure and Safe Reroute

## Diagnosis
Confirm that the host's selected `active_path` crosses a switch or link whose live topology status is `down`. Inspect the complete alternate path and require its intermediate switch and every link to be `up`. The ordinary reference can remain `primary`; a live equipment failure can justify a temporary `backup` path.

## Recovery
Preview only `HOST-001.active_path=backup` when the primary path is failed and the backup is healthy. Do not re-enable or rewrite the failed switch as part of the host reroute.

## Verification
Verify all four wired KPIs. Recovery requires throughput, latency, packet loss, and reachability to pass while the failed primary switch remains down.
