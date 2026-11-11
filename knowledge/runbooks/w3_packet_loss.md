---
doc_id: RB-W3-PACKET-LOSS
version: "1.0"
tenant: common
classification: internal
source: CCS synthetic wired operations handbook
---
# Packet Loss and Choppy Calls

Sustained `packet_loss_pct` can make a voice or video call choppy even when the link remains reachable. Compare the host's `loss_pct` with its reference and correlate it with live packet-loss and throughput KPIs. Restore the exact reference value, which represents the TCLink loss setting, and verify packet loss is at most 2 percent.
