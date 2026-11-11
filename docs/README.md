# 문서 읽는 길잡이

[프로젝트 처음으로](../README.md) · [소스 폴더](../src/README.md)

이 폴더는 프로그램을 설치·사용·수정·검증하는 방법을 설명합니다. 각 소스 폴더의 README와 이 문서를 함께 읽으면 전체 구조에서 개별 함수까지 내려갈 수 있습니다.

```mermaid
flowchart LR
  R[루트 README] --> Q[QUICKSTART: 설치와 무료 실행]
  Q --> W[WEB_CONSOLE: 화면 사용]
  W --> A[ARCHITECTURE: 코드 흐름]
  A --> F[소스 폴더 README]
  F --> C[reference: 함수 찾기]
```

## 사용자용 문서

| 파일 | 내용 | 읽는 시점 |
|---|---|---|
| [QUICKSTART.md](QUICKSTART.md) | Python 준비부터 첫 Mock 결과까지 | 처음 실행할 때 |
| [WEB_CONSOLE.md](WEB_CONSOLE.md) | 웹 시작·옵션·문서 관리·결과·문제 해결 | 화면을 사용할 때 |
| [GLOSSARY.md](GLOSSARY.md) | Agent, MCP, A2A, seed, Oracle 등 용어 | 모르는 용어를 만났을 때 |
| [WIRED_SCENARIOS.md](WIRED_SCENARIOS.md) | 6개 상황과 Mininet 이전 설계 | 실험 조건을 이해할 때 |
| [OBSERVABILITY.md](OBSERVABILITY.md) | CLI monitor와 상세 기록 | 어떤 단계가 수행됐는지 볼 때 |

## 개발자용 문서

| 파일 | 내용 | 연결되는 소스 |
|---|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | 프로세스·함수·데이터 연결 | [src/ccs](../src/ccs/README.md) |
| [MODULE_CONTRACTS.md](MODULE_CONTRACTS.md) | 모듈의 입력·출력 약속 | [소스 지도](../src/README.md) |
| [BACKEND.md](BACKEND.md) | 합성망 상태·도구·교체 경계 | [netops](../src/ccs/netops/README.md) |
| [PROTOCOLS.md](PROTOCOLS.md) | MCP/A2A transport·인증·실패 | [protocols](../src/ccs/protocols/README.md) |
| [INSTRUMENTATION.md](INSTRUMENTATION.md) | 이벤트·무결성·공개량·검색 | [core](../src/ccs/core/README.md), [knowledge](../src/ccs/knowledge/README.md) |
| [COMPATIBILITY.md](COMPATIBILITY.md) | 확인한 환경·버전·지원 범위 | [configs](../configs/README.md) |
| [reference/README.md](reference/README.md) | 자동 생성 함수 참조 읽는 법 | [Python 목록](reference/python_functions.md) |

## 결과와 저장소 관리

| 파일 | 내용 |
|---|---|
| [STATUS.md](STATUS.md) | 구현 완료/미완료 구분 |
| [RESULTS.md](RESULTS.md) | 공개 가능한 과거 집계 결과와 해석 범위 |
| [VALIDATION.md](VALIDATION.md) | 검증 방법·명령·기록의 한계 |
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | 현재 유선망 구현 범위 |
| [GITHUB_PREPARATION.md](GITHUB_PREPARATION.md) | 제외 파일 확인과 commit/push 순서 |

## 로컬 상세 기록과 공개 문서의 구분

기존 개발 폴더에는 `D0_LIVE_20261111.md`, `DIFFICULTY_COMPARISON_20261111.md`, `MININET_REVIEW_20261111.md`, `REVIEW_20261110.md`가 남아 있을 수 있습니다. 개인 실행 경로와 외부 원본 참조를 포함한 로컬 기록이므로 `.gitignore`에서 개별 제외합니다. 공개 clone에 없어도 정상이며, 공개 요약은 `RESULTS.md`를 읽습니다. 제외는 원본 삭제를 뜻하지 않습니다.

이 폴더의 설명용 코드 블록 자체가 실행되는 함수는 아닙니다. 실제 정의와 source line은 `reference/` 및 각 소스 폴더 README에서 찾습니다.
