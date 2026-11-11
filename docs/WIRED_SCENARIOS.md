# 업무 상황으로 보는 유선 네트워크 시나리오

현재 카탈로그는 `wired-v1`이며 W1–W5와 N0, 총 6개다. Agent는 사용자의 증상을 접수하고 관측 근거로 진단·변경·검증한다. 화면의 회의·파일 전송 이야기는 네트워크 장애의 업무 영향을 설명한다. 현재 SQLite KPI는 합성 값이며 회의 애플리케이션의 실제 영상 품질을 측정한 결과가 아니다.

| ID | 사용자 상황 | 네트워크 원인 | 해결 목표 |
|---|---|---|---|
| W1 | 중간 스위치가 멈췄어요 | 주 경로의 중간 스위치와 연결 단절 | 고장 구간을 유지한 채 정상 대체 경로로 우회 |
| W2 | 사내 서버에 접속할 수 없어요 | 잘못된 기본 게이트웨이 | 올바른 게이트웨이로 연결 복구 |
| W3 | 회의가 자꾸 끊겨요 | 전송 경로의 패킷 손실 설정 | 손실률을 운영 기준으로 복원 |
| W4 | 파일 전송이 너무 느려요 | 잘못 적용된 대역폭 상한 | 전송 처리량 회복 |
| W5 | 대화가 한 박자씩 늦어요 | 경로에 추가된 과도한 지연 | 왕복 지연 감소 |
| N0 | 신고는 들어왔지만 지금은 정상이에요 | 현재 서비스는 정상 | 측정 근거를 확인하고 변경 없이 종료 |

W1의 성공은 고장 스위치가 정상으로 바뀌었다는 뜻이 아니다. Agent가 정상 대체 경로를 골라 서비스가 복구되어야 한다. 설정 reference와 다른 경로라도 실제 경로가 살아 있으면 복구로 판정한다. W2–W5는 증상에 맞는 설정과 기준 값을 확인하며, N0는 네트워크 상태가 바뀌지 않아야 한다.

## L1·L2·L3 난이도와 반복 조건

| 선택 | 현재 코드에서 달라지는 것 | 달라지지 않는 것 |
|---|---|---|
| L1 | 관련 없는 추가 알람 0개 | 해당 시나리오의 장애 원인·목표 |
| L2 | 다른 장비의 추가 WARN 알람 1개 | 같은 fault/seed의 정답 조치 |
| L3 | 다른 장비의 추가 WARN 알람 2개 | 같은 fault/seed의 정답 조치 |

L2/L3는 Ethernet의 Layer 2/3이 아니다. 사람이 작업 중 다른 장비의 알림도 받는 상황과 비슷하다. 다만 Agent가 대상 장비만 조회하면 그 알람은 전달되지 않는다. 실제 입력 노출 여부를 따로 확인해야 하며, 과거 측정은 [RESULTS](RESULTS.md)에 구분했다.

`seed`는 합성 데이터와 요청 표현의 초기값이다. `repeat`는 한 run 안에서 사건을 반복하는 횟수다. Memory ON에서는 이전 episode의 기록이 다음 episode에 영향을 줄 수 있으므로, 반복 수를 늘리는 것과 독립 표본을 늘리는 것을 같게 해석하지 않는다.

실제 생성 코드는 [bench 폴더 설명](../src/ccs/bench/README.md), 최종 판정은 [evaluation 폴더 설명](../src/ccs/evaluation/README.md), 첫 실행은 [Quickstart](QUICKSTART.md)로 이어진다.

## Mininet으로 이전할 때

모든 시나리오는 Ethernet host/switch/router, 대체 경로, Linux routing과 traffic control로 구성 가능한 범위를 사용한다. Network Tools → NetworkBackend 계약을 유지하고, SQLiteBackend를 MininetBackend로 대체한다. MCP handler에 직접 shell command를 넣지 않는다.

| ID | 장애 주입 | 조치와 실제 확인 |
|---|---|---|
| W1 | 주 경로 스위치의 연결 포트를 down으로 설정 | 두 경로가 있는 topology에서 route/OpenFlow path를 backup으로 변경; 실패 포트가 down인 상태에서 ping·iperf 연결 확인 |
| W2 | client namespace의 default route를 잘못된 next hop으로 변경 | 유효한 router interface로 default route 복원; server subnet ping·TCP 연결 확인 |
| W3 | 선택한 TCLink egress에 loss 설정 | 해당 loss 복원; ping 손실률 및 UDP iperf 수신 손실 측정 |
| W4 | 선택한 TCLink egress의 bw를 낮춤 | bw 복원; TCP iperf 처리량 비교 |
| W5 | 선택한 TCLink egress에 delay 추가 | delay 복원; ping RTT 비교 |
| N0 | 장애 없이 정상 상태 유지 | 같은 probe를 반복하고 설정·route·flow table의 불필요한 변경이 없는지 확인 |

이는 **이전 설계**다. 이번 Windows 실행에는 Mininet 프로세스나 실제 traffic generator가 포함되지 않는다. 이전 시 Linux VM과 고정 topology, probe 길이·warm-up·허용 오차를 정하고 `preview/apply/version/idempotency/rollback/verify` conformance를 통과해야 한다. SQLite 합성 시간/KPI와 Mininet 실측 결과는 별도 backend 집단으로 비교한다.

Mininet의 [공식 Walkthrough](https://mininet.org/walkthrough/)는 host network namespace, link up/down, ping, iperf, custom topology를 설명한다. [TCIntf API](https://mininet.org/api/classmininet_1_1link_1_1TCIntf.html)는 bandwidth, delay, loss traffic-control 설정을 제공한다. 위 시나리오 매핑은 이 기능을 바탕으로 한 설계다.

## 결과 읽기

결과 분석은 접수된 상황 → 관측 원인 → 적용 조치 → 같은 대상의 KPI 변화 순서로 보여준다. `throughput_mbps`, `latency_ms`, `packet_loss_pct`, `reachability_pct`를 비교하며, 보고서의 문장만으로 성공을 판정하지 않는다. 실제 최종 DB와 독립 Oracle의 허용 변경·서비스 검증을 사용한다.

진행 기록은 통신의 출발지·목적지·요청/응답을 표시한다. 진단 위임을 선택하면 `incident`, 선택한 `context.runbooks`, `context.history`, 추가 context, `constraints`와 메시지 식별 정보를 실제 전달 값으로 확인할 수 있다. MCP client와 server→backend 실행은 별도 기록이며 내부 작업은 내부 처리로 표시한다.
