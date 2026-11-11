# 수정하고 검증하는 순서

[처음으로](README.md) · [구조 지도](docs/ARCHITECTURE.md) · [검증 안내](docs/VALIDATION.md)

작은 변경부터 시작한다. 예를 들어 W4 설명 문구를 바꾸는 것과 네트워크 복구 판정식을 바꾸는 것은 필요한 검증이 다르다. 먼저 [폴더 지도](src/ccs/README.md)에서 책임 모듈을 찾고, 해당 README에서 관련 함수와 테스트를 확인한다.

## 변경 단계

1. [Quickstart](docs/QUICKSTART.md)로 별도 실행 환경을 준비한다.
2. 바꾸려는 동작과 정상·실패 조건을 한 문장으로 정한다.
3. 담당 파일만 수정하고 관련 문서·예제를 함께 갱신한다.
4. 동작에 맞는 최소 회귀검사를 수행한다. 원래 테스트를 무조건 약하게 바꾸지 않는다.
5. Python 함수나 웹 함수가 바뀌면 `tools/generate_reference.py`로 함수 문서를 갱신한다.
6. 전체 검사와 공개 전 검사를 통과한 뒤 diff를 검토한다.

실행 명령과 예상 결과는 [tests/README.md](tests/README.md), 등록 전 명령은 [GitHub 준비](docs/GITHUB_PREPARATION.md)에 있다. CI는 Mock·offline transport를 사용하며 Key나 유료 호출을 요구하지 않는다.

## 책임 경계를 지키기

| 변경 대상 | 같이 확인할 계약 |
|---|---|
| Backend | preview → approval → apply → verify → rollback, version/idempotency, 독립 Oracle |
| Agent/prompt | 역할별 허용 도구, 구조화 응답, 제한된 repair, 성공 outcome 정확 일치 |
| MCP/A2A | wire schema, 오류·중복 요청·timeout, client/server 양쪽 |
| Runbook | YAML frontmatter·검색 결과·snapshot. 폴더 README는 검색 대상에서 제외 |
| Memory | 초기 상태와 ON/OFF 조건, 실험 간 누적 여부, 개인정보 |
| 결과·보고서 | read-only 검증, seal, 실패·중단과 성공 통계의 분리 |
| 웹 | API 응답, token·경로 검증, 실제 UI 동작과 상태 표시 |
| 설치/경로 | 개인 설정 보존, 공개 예제만 있는 새 checkout에서 시작 가능 |

## 결과와 원본 보존

- 기존 실험 폴더에 덮어쓰지 말고 고유 출력 경로를 사용한다.
- 개인 XML·비용 장부·원시 대화를 commit하지 않는다.
- Mock 통과를 실제 LLM 성능으로, SQLite KPI를 실제 패킷 측정으로 설명하지 않는다.
- 소스 변경 전후 실험을 한 집단으로 합칠 때는 차이를 기록한다. 과거 성능 표는 그 실행 당시 버전의 결과다.
- 코드·프롬프트·runbook 변경은 함수 문서와 source hash에 영향을 줄 수 있다. 과거 snapshot을 새 파일로 교체하지 않는다.

## 설명과 리뷰

PR 설명에는 문제, 수정 후 동작, 검증 결과, 남은 제한을 적는다. 상세한 작업 일지보다 검토자가 재현할 수 있는 명령과 판정 기준이 중요하다. 사용자 문서는 한국어로 쓰되 함수·파일·API 이름은 실제 표기를 유지한다.

현재 license는 지정하지 않았다. 외부 기여를 받기 전에 저장소 소유자가 이용·기여 조건을 정해야 한다.
