# Runbook library

여섯 개 Markdown 문서는 모두 synthetic wired NetOps 도메인 예시입니다. Runbook은 incident text와 검색어에 따라 Operation에 제공되는 조언입니다. 그것만으로 고장 원인, 실제 상태, 복구 성공을 입증하지 않습니다. Diagnosis Agent는 현재 상태를 read-only 도구로 확인하고, Runner가 별도로 preview → approval → apply → verify → 필요 시 rollback을 수행합니다.

## 현재 6개 문서

| `doc_id` / 파일 | 검색에 쓰일 상황 | 핵심 절차·변경 후보 | `classification` |
|---|---|---|---|
| `RB-N0-NO-ACTION` / [`n0_no_action.md`](n0_no_action.md) | 일시적 증상이 재현되지 않고 정상 가능성 | host 설정, path, 네 가지 KPI를 확인. 정상이라면 원인을 꾸며내거나 config를 바꾸지 않고 no-action 기록 | `public` |
| `RB-W1-SWITCH-REROUTE` / [`w1_switch_reroute.md`](w1_switch_reroute.md) | 중간 스위치나 경로 장애 | 현재 primary path가 down 장비를 통과하는지, 대체 경로의 **모든** 스위치/링크가 up인지 확인. 증거가 충분할 때만 `HOST-001.active_path=backup`; 고장 스위치를 다시 쓰지 않음. 4개 KPI 검증 | `internal` |
| `RB-W2-DEFAULT-GATEWAY` / [`w2_default_gateway.md`](w2_default_gateway.md) | 사내 서버로 연결 불가 | host `default_gateway`의 current/reference 비교; 관측된 정확한 reference IPv4 주소만 복구하고 reachability 및 KPI 검증 | `internal` |
| `RB-W3-PACKET-LOSS` / [`w3_packet_loss.md`](w3_packet_loss.md) | 음성/영상 회의의 끊김 | `loss_pct` 설정의 current/reference와 live packet-loss/throughput KPI를 함께 확인. exact reference 복구; packet loss ≤ 2% 검증 | `internal` |
| `RB-W4-BANDWIDTH-CAP` / [`w4_bandwidth_cap.md`](w4_bandwidth_cap.md) | 파일 복사·bulk transfer 저하 | `bandwidth_mbps` current/reference mismatch와 `throughput_mbps`를 확인. latency만 보고 bandwidth cap으로 추측하지 않음. exact reference 복구; throughput ≥ 80 Mbps 검증 | `internal` |
| `RB-W5-EXCESSIVE-DELAY` / [`w5_excessive_delay.md`](w5_excessive_delay.md) | 회의 응답이 늦거나 영상 지연 | `delay_ms` current/reference와 `latency_ms`를 비교하고 failed path를 먼저 배제. exact reference 복구; latency ≤ 30 ms 및 나머지 KPI 검증 | `internal` |

## 공통 메타데이터의 뜻

- `doc_id`: 검색 결과와 실행 provenance에 쓰이는 안정된 고유 ID. 이미 존재하는 ID를 재사용하지 않습니다.
- `version`: 원문 버전 문자열. 변경 의미가 있으면 함께 올립니다.
- `tenant`: 문서의 tenant 범위. 현재 예시는 모두 `common`입니다. 값이 기록된다는 사실은 D0 검색에서 실제 필터된다는 뜻이 아닙니다.
- `classification`: 공개 분류 값 `public` / `internal` / `restricted` 중 하나. 현재 D0 Runbook 검색은 이 분류를 필터 기준으로 적용하지 않습니다. 민감한 실제 운영 정보를 넣어도 된다는 허가가 아닙니다.
- `source`: 이 지침의 출처를 사람이 이해하도록 표시합니다. 검색 점수나 사실 검증 근거가 아닙니다.

## 수정하거나 새 runbook을 추가하는 사람을 위한 순서

1. 검색 질의가 기대하는 증상·KPI·config field를 본문에 명시하고, 일반 원인과 검사법을 설명합니다.
2. 필요한 경우 level-two heading을 두어 진단/복구/검증 단위로 chunk를 나눕니다. 각 절은 제목 없이 검색돼도 의미가 통하도록 씁니다.
3. 현재 관측으로 확인해야 할 사실과 조치 전 조건을 적습니다. Reference 값은 무조건 정답으로 주장하지 않고 현재 상태와 대조하도록 합니다.
4. 모든 필수 메타데이터를 두고, `doc_id` 고유성·허용 분류·본문 존재를 확인합니다.
5. 함수 구현은 [`stores.py`](../../src/ccs/knowledge/stores.py), 검색·Memory 계약은 [`test_instrumentation.py`](../../tests/test_instrumentation.py) 및 [`test_runtime_conditions.py`](../../tests/test_runtime_conditions.py)에서 확인합니다.

Runbook chunking은 HTML headings나 임의 크기 기반이 아니라 정확한 `## ` 시작 줄 기준입니다. 하나의 heading 아래 내용은 모두 한 chunk에 들어갑니다. Runbook 문서가 늘면 검색 top-k 때문에 관련 chunk가 결과 밖으로 밀릴 수 있습니다. 검색결과 수가 적거나 없다고 해서 문서가 없거나 원인이 없다고 결론 내리면 안 됩니다.
