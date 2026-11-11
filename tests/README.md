# 테스트 가이드

`tests/`의 26개 `test_*.py` 파일은 CCS baseline의 단위·계약·통합 회귀검사입니다. pytest가 Python test function을 모으고 각 assertion/예외 검사를 실행합니다. 빠른 mock test도 별도 child process나 localhost MCP/A2A wire를 시작할 수 있으므로, “mock”이란 외부 모델 API 무료 검증 경로를 뜻하며 모든 테스트가 process-free라는 뜻은 아닙니다.

## 첫 실행

프로젝트는 Python `>=3.11`을 선언하고 저장소의 고정 버전 기준은 Python 3.14입니다. 테스트 의존성은 `requirements.lock`과 `pyproject.toml`의 `test` extra를 참조합니다. 환경 준비와 실행 경로는 [저장소 시작 안내](../README.md)에서 먼저 읽으세요. API Key 없이 회귀검사만 실행하려면 PowerShell에서 프로젝트 루트에 두고:

```powershell
$env:CCS_TEST_WORKING_ROOT = Join-Path 'D:\Codex\WorkingFiles' 'ccs-test-working'
$env:TEMP = $env:CCS_TEST_WORKING_ROOT
$env:TMP = $env:CCS_TEST_WORKING_ROOT
New-Item -ItemType Directory -Force -Path $env:CCS_TEST_WORKING_ROOT | Out-Null
python -B -m pytest -q --basetemp (Join-Path $env:CCS_TEST_WORKING_ROOT 'pytest-work')
```

이 경로는 격리된 test output을 D 드라이브에 두려는 권장 실행 방식입니다. pytest의 `--basetemp`는 fixture가 만든 `tmp_path`를 통제하고, [`tests/support_paths.py`](support_paths.py)의 `workspace_for()`는 모든 filesystem-writing test module에 별도 폴더를 제공합니다. `CCS_TEST_WORKING_ROOT`가 설정돼 있으면 이를 기준으로 `<module-name>/`을 만들고, 설정이 없으면 OS의 temporary directory 아래 `ccs-testbed-tests/`를 씁니다. `test_activity.py`는 이전 환경변수 `CCS_ACTIVITY_WORKING_ROOT`도 읽되, unified root가 설정되면 unified root가 우선합니다. 각 clone/병렬 작업에는 고유한 `CCS_TEST_WORKING_ROOT`를 지정하세요.

`test_network_view.py`가 테스트 전후에 재귀 삭제하는 경로도 `workspace_for("test_network_view")`가 반환한 모듈 전용 폴더입니다. 정리 전에 그 폴더의 parent가 선택된 root와 같은지 assert합니다. 따라서 이 테스트는 선택한 root 자체나 다른 module folder를 정리 대상으로 삼지 않습니다. `isolated_ai_config()`는 `ai.example.xml` 사본을 같은 모듈 폴더에 만들고 `budget.ledger_path`도 그 폴더 안의 별도 SQLite 파일로 지정합니다. 원본 공개 XML과 비밀 설정은 수정하지 않습니다. 로컬 Windows에서 위 명령을 사용하면 pytest의 fixture output과 module workspaces가 분리된 D 드라이브 경로 아래에 저장됩니다. GitHub Actions는 job별 격리된 runner temp path를 같은 환경변수로 넘길 수 있습니다([CI workflow](../.github/workflows/test.yml)).
## 테스트 지원 파일

| 파일 | 역할 |
|---|---|
| [`__init__.py`](__init__.py) | `tests`를 명시적인 Python package로 만들어 `tests.support_paths` import가 설치된 다른 `tests` package에 가려지지 않게 합니다. pytest가 실행할 test module은 아닙니다. |
| [`support_paths.py`](support_paths.py) | `work_root()`와 `workspace_for()`로 환경변수에 따른 격리 경로를 정하고, `isolated_ai_config()`로 public AI 예제 사본의 budget ledger를 각 module 폴더에 둡니다. |
## API 0과 expected result

일반 pytest 회귀검사는 provider credentials를 읽어 호출하는 live experiment가 아닙니다. Provider contract 검사에서는 scripted response, monkeypatch/mock transport를 사용하고, workflow E2E는 SQLite backend 및 실제 local child processes/local MCP·A2A wire를 사용할 수 있습니다. 따라서 정상 회귀 실행에서 기대하는 외부 paid model API call은 **0**입니다. 외부 서비스 접근이나 API Key가 필요한 실행은 별도 `run --mode live`이며 이 테스트 명령과 다릅니다.

성공하면 pytest는 초록/점 형태와 끝의 `N passed`를 출력하고 종료 코드 0을 냅니다. Windows symlink 권한 등 명시적 환경 제한은 skip으로 표시될 수 있습니다. **숫자 N을 문서에 고정하지 않습니다.** 테스트가 늘거나 조건부 skip이 생기면 달라집니다. 첫 실패가 나오면 pytest가 test file, test function, assertion/traceback을 보여주고 종료 코드는 nonzero입니다.

“positive”와 “negative”는 테스트가 성공/실패하는 구분이 아닙니다. 정상 동작 예시는 정상 상태/승인된 변경을 기대하고, rejection 예시는 잘못된 token/schema/route, 비승인 Memory write, traversal, out-of-order state 등에서 예외·거부·부작용 부재를 **assert**합니다. 그런 거부 assertion이 통과하면 해당 테스트는 `passed`입니다. 운영 결과 state 예시는 `COMPLETED`(runner 완주), `RECOVERED`(검증된 복구), `NO_CHANGE`, `ROLLED_BACK`, `DECLINED`, `ESCALATED`, `FAILED`, artifact 무결성 오류 등을 문맥에 맞춰 구분합니다. `COMPLETED`만으로 네트워크 복구 성공이 보장되지는 않습니다. 전체 의미는 [실행 결과 설명](../README.md) 및 [상태 보고서](../docs/STATUS.md)를 보세요.

## 모든 테스트 모듈

간단한 설명은 파일의 현재 이름과 주요 테스트 그룹을 따라 작성했습니다. 전체 Python module/function/symbol 이동 목록은 [Python function catalog](../docs/reference/python_functions.md#tests)에서 볼 수 있습니다. 아래는 함수 목록 전체를 복제하지 않고 각 파일의 테스트 범위를 요약합니다.

| 모듈 | 주요 테스트 그룹 |
|---|---|
| [`test_activity.py`](test_activity.py) | JSONL activity 기록/flush/resume, secret scrub, collision-free writer, tool call 인자·결과·duration 계측 |
| [`test_backend.py`](test_backend.py) | SQLite backend identity와 role별 tool surface, N0/W1-W5 시나리오, preview/version/idempotency/rollback/KPI/target·topology 계약 |
| [`test_config_budget.py`](test_config_budget.py) | AI/system XML schema·profile·secret-free export, XML external entity 및 오타/중복 거부, cache usage category, atomic budget reserve·settle/restart |
| [`test_event_communication.py`](test_event_communication.py) | Agent handoff에 실제 필드 표시, MCP client/server 방향 구분, transport 실패, 자격증명 비노출 |
| [`test_event_presentation.py`](test_event_presentation.py) | event를 안정된 화면 route/status로 변환하고 검색 질의·unknown event·runner event를 안전하게 표현 |
| [`test_instrumentation.py`](test_instrumentation.py) | NullGate event identity/causal merge, integrity seal, duplicate/incomplete pair, Runbook BM25, approved+verified Memory, offline ledger normalization |
| [`test_monitor.py`](test_monitor.py) | activity 읽기 정렬·redaction, 안전한 dashboard cursor/path, read-only methods, standalone HTML escaping·과거 run 처리 |
| [`test_network_view.py`](test_network_view.py) | wired network preview/cache, W1 run projection, read-only run files, mismatched snapshot 거부, pending/path traversal 보호 |
| [`test_observability_e2e.py`](test_observability_e2e.py) | 실제 Memory chain을 spanning한 event/seal, 관측된 failure terminal 상태 및 Memory 미저장 |
| [`test_pacing.py`](test_pacing.py) | force delay 입력 범위, 동시 control revision atomicity, zero-delay, delay change 중 기다림 해제/합집합 기록 |
| [`test_protocols.py`](test_protocols.py) | localhost wire의 MCP role/schema/auth, A2A card/task lifecycle, field validation, idempotency/payload mismatch, timeout, bad-token rejection |
| [`test_provider_contracts.py`](test_provider_contracts.py) | OpenAI Responses/Anthropic Messages adapter의 tool history/cache accounting, budget reserve/settle, timeout/error/malformed arguments |
| [`test_repository_tools.py`](test_repository_tools.py) | 공개 파일 검사에서 local AI config 제외, working tree가 정리된 뒤에도 staged blob의 secret 탐지, ignore된 로컬 설정 링크 차단 확인 |
| [`test_report_contract.py`](test_report_contract.py) | report outcome에 prose 대신 고정 enum을 요구, repair 재시도, 한도 초과시 계속 거부 |
| [`test_review_regressions.py`](test_review_regressions.py) | 서로 다른 execution setting pairing 방지, custom request/profile generation identity, nonexistent route field 및 invalid action proposal 차단 |
| [`test_run_analysis.py`](test_run_analysis.py) | 실제 mock artifact 분석 및 read-only 보장, outcome 구분, partial/malformed/unsealed run, wired topology와 endpoint/auth 조건 |
| [`test_run_finalization.py`](test_run_finalization.py) | finalization 실패를 unsealed terminal로 남김, 성공 seal, Windows 파일 공유 잠금 retry/회복/전파, 원래 abort 예외 재발생 |
| [`test_runbook_discovery.py`](test_runbook_discovery.py) | README가 Runbook discovery/snapshot/search 입력에서 제외되는지, 웹 catalog가 문서 README와 함께 6개 runbook을 로드하는지, 환경변수 기반 runtime path가 파일 생성 없이 계산되는지 확인 |
| [`test_runner_e2e.py`](test_runner_e2e.py) | 3-process wire에 걸친 Memory chain, 잘못된 조치 rollback, decline 무변경, budget failure, out-of-order state rejection |
| [`test_runtime_conditions.py`](test_runtime_conditions.py) | runbook 선택과 seed Memory provenance snapshot, 0 runbook 및 RAG-off mock 실행, parent/child real delay 계측 |
| [`test_seal_readonly.py`](test_seal_readonly.py) | sealed merge/artifact 손상 상태에서 report/compare가 기존 파일을 수정하지 않음 |
| [`test_web_console.py`](test_web_console.py) | web auth/origin/content limits, key secrecy, stale terminal index, soft memory clear, frozen run selection, config immutability, cancellation/cleanup, symlink rejection |
| [`test_web_lan.py`](test_web_lan.py) | LAN bind/allowlist/IP+token+origin 요구 조건 및 다른 origin POST 거부 |
| [`test_web_output_root.py`](test_web_output_root.py) | configured output root의 freeze/restart 안정성, legacy run 보존, client path injection 및 외부 callback root 거부 |
| [`test_web_startup_errors.py`](test_web_startup_errors.py) | listener bind failure를 구분, workspace 권한 오류를 오분류하지 않음, CLI가 secret/fallback 없이 실패 설명 |
| [`test_wired_catalog.py`](test_wired_catalog.py) | 과거 catalog는 archive되고 신규 run에서 재사용되지 않음; 지원하지 않는 scenario/target 거부 |

## 테스트 하나를 따라가는 법

1. 이 색인에서 모듈이 검증하는 contract를 찾습니다.
2. [Python function catalog](../docs/reference/python_functions.md#tests)에서 모듈 anchor를 열고 필요한 경우 test function anchor로 좁힙니다.
3. 해당 `test_*.py`의 fixture, arrange/action/assert 구조를 읽습니다. 테스트는 보통 입력/fixture를 만들고 코드를 호출한 뒤 기대값·오류·파일 변경 여부를 검사합니다.
4. 통합 흐름이면 구현의 `src/ccs/` 대응 모듈과 연결합니다. 실패 assertion은 정상적인 방어동작을 검사할 수 있으므로 trace에서 “테스트가 예상한 거부인지, 예상하지 못한 거부인지”를 구분합니다.







