# 초보자 용어집

[문서 목차](README.md) · [처음 실행](QUICKSTART.md)

| 용어 | 쉬운 의미 | 이 프로젝트에서의 사용 |
|---|---|---|
| Testbed | 반복 실험을 할 수 있게 만든 시험 환경 | 합성망, Agent, 도구, 기록, 평가기 |
| NetOps | 네트워크 운영 | 장애 조사·설정 복구·정상 여부 확인 |
| Agent | 목표를 받아 도구를 선택하며 일을 진행하는 구성요소 | Operation과 Diagnosis |
| LLM | 문맥을 읽고 구조화된 선택·응답을 만드는 언어 모델 | Live 모드에서 API 호출 |
| Mock | 실제 모델 판단 대신 정해진 응답/동작을 사용하는 검사 | 무료. 네트워크 wire 자체는 실제 localhost 통신 |
| Backend | 도구 뒤에서 실제 상태와 동작을 구현하는 부분 | 현재 SQLiteBackend |
| SQLite | 파일 하나로 사용할 수 있는 데이터베이스 | 합성망·검색·Memory·비용 장부 |
| MCP | Agent가 도구 목록·입출력을 주고받는 규약 | 설정 조회·변경·서비스 검사 |
| A2A | Agent 사이에서 작업을 전달하는 규약 | 진단 요청과 결과 반환 |
| Runbook | 운영자가 따를 수 있는 문제 해결 절차 | Markdown을 chunk로 나눠 검색 |
| RAG | 필요한 외부 자료를 검색해 모델 입력에 넣는 방식 | Runbook 검색 결과를 context로 전달 |
| FTS5 / BM25 | SQLite 전문 검색 기능 / 결과 관련성 점수 | 두 개의 별도 검색 엔진이 아니라 함께 사용 |
| Memory | 이전 사건의 확인된 정보 또는 참고 기록 | 조건을 만족한 기록 저장, 이후 검색 |
| Run | 한 번 실행한 실험 묶음 | 여러 fault·seed·repeat를 포함할 수 있음 |
| Episode | run 안의 사건 한 번 | 하나의 DB와 결과를 가짐 |
| Seed | 합성 데이터 생성 초기값 | LLM 자체의 완전한 재현 보장은 아님 |
| L1/L2/L3 | 이 프로젝트의 난이도 label | 다른 장비 방해 알람 0/1/2개 |
| KPI | 상태를 판단하는 수치 | 처리량·지연·손실·도달률. 현재 합성 값 |
| Preview token | 검토한 변경과 현재 상태를 묶는 표식 | 검토와 다른 변경·오래된 변경 방지 |
| Idempotency | 같은 변경 요청을 중복 실행해도 효과를 한 번으로 제한 | apply/status/rollback key |
| Rollback | 적용한 변경을 되돌리는 것 | 서비스 검사 실패 시 복구 시도 |
| Oracle | 모델의 주장과 별개로 실제 목표 달성을 판단하는 코드 | 최종 DB·정답 조건·금지 변경 검사 |
| Schema | 데이터의 필드·type·형식을 정한 약속 | Pydantic, tool JSON Schema |
| Artifact | 실행이 남긴 파일 | manifest, raw response, report 등 |
| Hash / seal | 파일 변경을 확인할 수 있는 지문 / 지문 묶음 | 무결성 검사. 전자서명이나 원본 사실의 자동 보증은 아님 |
| D0 / NullGate | 정보 보호 변환을 적용하지 않는 비교 기준 | 업무상 승인·역할 권한·검증은 유지 |
| Provenance | 정보가 어디서 왔고 어디로 갔는지의 이력 | 경계별 disclosure event와 ledger |
| CI | 코드 변경 때 자동으로 검사를 실행하는 흐름 | GitHub Actions의 무료 회귀검사 |
| Commit / push | 로컬 Git 이력 저장 / 원격 전송 | source 공개와 로컬 실행은 별개 |

용어가 같은 파일 이름에 쓰여도 의미를 구분하세요. 예를 들어 `memory.sqlite`는 Agent 이력이고 `cost-ledger.sqlite`는 API 비용 장부입니다. `ledger.json`은 정보 전달 계측 결과이며 비용 장부가 아닙니다.
