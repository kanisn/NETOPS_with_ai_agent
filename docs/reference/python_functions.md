# Python 파일·함수 전체 참조

[루트 안내](../../README.md) · [문서 목차](../README.md) · [참조 읽는 법](README.md)

현재 소스에서 **Python 81개 파일, 함수·메서드 645개, 클래스 63개**를 읽어 만든 목록입니다. 테스트와 문서 관리 도구도 포함합니다.

이 문서는 함수의 위치와 입력, 원문 설명을 찾는 사전입니다. 처음에는 [전체 실행 흐름](../ARCHITECTURE.md)을 읽고 해당 폴더 README에서 역할을 익힌 뒤 필요한 항목만 찾아보세요.

- `async`: 다른 작업의 응답을 기다릴 수 있는 비동기 함수입니다.
- `메서드`: 클래스 인스턴스의 동작입니다. `self`는 그 인스턴스를 뜻합니다.
- `_`로 시작하는 이름은 내부용이라는 관례이며 접근 보안 장치는 아닙니다.
- 중첩 함수는 다른 함수 안에서 만들어지는 callback/handler입니다.
- 호출 표현은 AST에 직접 적힌 이름만 보여 줍니다. 동적 dispatch, HTTP/A2A/MCP 경계, 실행 순서를 자동으로 증명하지 않습니다.
- docstring은 소스의 설명을 그대로 인용합니다. 설명이 없는 작은 내부 함수는 폴더 README의 상위 흐름과 소스를 함께 확인하세요.

<a id="application"></a>
## 애플리케이션

| 모듈 | 함수·메서드 | 클래스 |
|---|---:|---:|
| [ccs.__init__](#module-ccs-__init__) | 0 | 0 |
| [ccs.__main__](#module-ccs-__main__) | 0 | 0 |
| [ccs.agent_runtime](#module-ccs-agent_runtime) | 9 | 1 |
| [ccs.bench.__init__](#module-ccs-bench-__init__) | 0 | 0 |
| [ccs.bench.scenarios](#module-ccs-bench-scenarios) | 9 | 0 |
| [ccs.budget](#module-ccs-budget) | 7 | 2 |
| [ccs.cli](#module-ccs-cli) | 3 | 0 |
| [ccs.config](#module-ccs-config) | 8 | 4 |
| [ccs.contracts](#module-ccs-contracts) | 0 | 6 |
| [ccs.core.__init__](#module-ccs-core-__init__) | 0 | 0 |
| [ccs.core.bus](#module-ccs-core-bus) | 7 | 1 |
| [ccs.core.events](#module-ccs-core-events) | 1 | 1 |
| [ccs.core.gateway](#module-ccs-core-gateway) | 4 | 4 |
| [ccs.core.integrity](#module-ccs-core-integrity) | 7 | 0 |
| [ccs.evaluation.__init__](#module-ccs-evaluation-__init__) | 0 | 0 |
| [ccs.evaluation.ledger](#module-ccs-evaluation-ledger) | 6 | 0 |
| [ccs.evaluation.oracle](#module-ccs-evaluation-oracle) | 2 | 0 |
| [ccs.event_communication](#module-ccs-event_communication) | 3 | 0 |
| [ccs.event_presentation](#module-ccs-event_presentation) | 9 | 0 |
| [ccs.knowledge.__init__](#module-ccs-knowledge-__init__) | 0 | 0 |
| [ccs.knowledge.stores](#module-ccs-knowledge-stores) | 20 | 2 |
| [ccs.llm](#module-ccs-llm) | 9 | 4 |
| [ccs.monitor](#module-ccs-monitor) | 27 | 3 |
| [ccs.monitor_i18n](#module-ccs-monitor_i18n) | 0 | 0 |
| [ccs.netops.__init__](#module-ccs-netops-__init__) | 0 | 0 |
| [ccs.netops.backend](#module-ccs-netops-backend) | 3 | 1 |
| [ccs.netops.errors](#module-ccs-netops-errors) | 0 | 7 |
| [ccs.netops.sqlite_backend](#module-ccs-netops-sqlite_backend) | 42 | 1 |
| [ccs.netops.tools](#module-ccs-netops-tools) | 2 | 0 |
| [ccs.network_view](#module-ccs-network_view) | 16 | 1 |
| [ccs.observability](#module-ccs-observability) | 8 | 1 |
| [ccs.pacing](#module-ccs-pacing) | 13 | 0 |
| [ccs.paths](#module-ccs-paths) | 2 | 0 |
| [ccs.processes](#module-ccs-processes) | 4 | 1 |
| [ccs.progress](#module-ccs-progress) | 5 | 1 |
| [ccs.protocols.__init__](#module-ccs-protocols-__init__) | 0 | 0 |
| [ccs.protocols._auth](#module-ccs-protocols-_auth) | 5 | 1 |
| [ccs.protocols.a2a](#module-ccs-protocols-a2a) | 9 | 2 |
| [ccs.protocols.errors](#module-ccs-protocols-errors) | 0 | 5 |
| [ccs.protocols.mcp](#module-ccs-protocols-mcp) | 14 | 1 |
| [ccs.reporting](#module-ccs-reporting) | 5 | 0 |
| [ccs.run_analysis](#module-ccs-run_analysis) | 31 | 0 |
| [ccs.runner](#module-ccs-runner) | 18 | 1 |
| [ccs.scenario_catalog](#module-ccs-scenario_catalog) | 0 | 0 |
| [ccs.services](#module-ccs-services) | 3 | 0 |
| [ccs.studio_markup](#module-ccs-studio_markup) | 0 | 0 |
| [ccs.studio_script](#module-ccs-studio_script) | 0 | 0 |
| [ccs.studio_styles](#module-ccs-studio_styles) | 0 | 0 |
| [ccs.tool_access](#module-ccs-tool_access) | 3 | 2 |
| [ccs.web_console](#module-ccs-web_console) | 61 | 4 |
| [ccs.web_ui](#module-ccs-web_ui) | 1 | 0 |

<a id="tests"></a>
## tests

| 모듈 | 함수·메서드 | 클래스 |
|---|---:|---:|
| [tests.__init__](#module-tests-__init__) | 0 | 0 |
| [tests.support_paths](#module-tests-support_paths) | 3 | 0 |
| [tests.test_activity](#module-tests-test_activity) | 8 | 1 |
| [tests.test_backend](#module-tests-test_backend) | 11 | 0 |
| [tests.test_config_budget](#module-tests-test_config_budget) | 10 | 0 |
| [tests.test_event_communication](#module-tests-test_event_communication) | 7 | 0 |
| [tests.test_event_presentation](#module-tests-test_event_presentation) | 6 | 0 |
| [tests.test_instrumentation](#module-tests-test_instrumentation) | 14 | 0 |
| [tests.test_monitor](#module-tests-test_monitor) | 10 | 0 |
| [tests.test_network_view](#module-tests-test_network_view) | 10 | 0 |
| [tests.test_observability_e2e](#module-tests-test_observability_e2e) | 3 | 0 |
| [tests.test_pacing](#module-tests-test_pacing) | 7 | 0 |
| [tests.test_protocols](#module-tests-test_protocols) | 16 | 0 |
| [tests.test_provider_contracts](#module-tests-test_provider_contracts) | 22 | 0 |
| [tests.test_report_contract](#module-tests-test_report_contract) | 13 | 2 |
| [tests.test_repository_tools](#module-tests-test_repository_tools) | 4 | 0 |
| [tests.test_review_regressions](#module-tests-test_review_regressions) | 10 | 1 |
| [tests.test_run_analysis](#module-tests-test_run_analysis) | 10 | 0 |
| [tests.test_run_finalization](#module-tests-test_run_finalization) | 21 | 1 |
| [tests.test_runbook_discovery](#module-tests-test_runbook_discovery) | 3 | 0 |
| [tests.test_runner_e2e](#module-tests-test_runner_e2e) | 7 | 0 |
| [tests.test_runtime_conditions](#module-tests-test_runtime_conditions) | 5 | 0 |
| [tests.test_seal_readonly](#module-tests-test_seal_readonly) | 3 | 0 |
| [tests.test_web_console](#module-tests-test_web_console) | 20 | 0 |
| [tests.test_web_lan](#module-tests-test_web_lan) | 4 | 0 |
| [tests.test_web_output_root](#module-tests-test_web_output_root) | 15 | 0 |
| [tests.test_web_startup_errors](#module-tests-test_web_startup_errors) | 7 | 1 |
| [tests.test_wired_catalog](#module-tests-test_wired_catalog) | 2 | 0 |

<a id="tools"></a>
## 관리 도구

| 모듈 | 함수·메서드 | 클래스 |
|---|---:|---:|
| [tools.check_repository](#module-tools-check_repository) | 7 | 0 |
| [tools.generate_reference](#module-tools-generate_reference) | 11 | 0 |

<a id="module-ccs-__init__"></a>
## `ccs.__init__`

[소스 파일](../../src/ccs/__init__.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: CCS synthetic NetOps baseline. No disclosure protection is implemented.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-__main__"></a>
## `ccs.__main__`

[소스 파일](../../src/ccs/__main__.py) · [이 폴더 설명](../../src/ccs/README.md)

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-agent_runtime"></a>
## `ccs.agent_runtime`

[소스 파일](../../src/ccs/agent_runtime.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Agent decisions, isolated from the network backend and evaluator.

<a id="class-ccs-agent_runtime-AgentFailure"></a>
### `AgentFailure`

**클래스** · [정의 위치 L9](../../src/ccs/agent_runtime.py#L9)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-agent_runtime-prompt"></a>
### `prompt`

**함수** · [정의 위치 L11](../../src/ccs/agent_runtime.py#L11)

```python
prompt(system, role)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(system.prompts / f'{role}.txt').read_text`

</details>

<a id="fn-ccs-agent_runtime-call_model"></a>
### `call_model`

**비동기 함수** · [정의 위치 L14](../../src/ccs/agent_runtime.py#L14)

```python
async call_model(conv, schemas, retries)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `conv.feedback`, `conv.next`, `range`

</details>

<a id="fn-ccs-agent_runtime-collect_context"></a>
### `collect_context`

**비동기 함수** · [정의 위치 L21](../../src/ccs/agent_runtime.py#L21)

```python
async collect_context(ai, system, request, gateway, runbooks, memory, run_dir, *, mode, profile_override=None, trace_id=None, cause=None, rag_enabled=True)
```

> The live Operation Agent selects search queries, repetitions and delegation content.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`' '.join`, `AgentFailure`, `Conversation`, `Path`, `activity.emit`, `activity_for_episode`, `ai.keys.values`, `call.arguments.get`, `call_model`, `context['history'].extend`, `context['runbooks'].extend`, `conv.close`, `conv.result`, `dict`, `gateway.pass_through`, `isinstance`, `len`, `memory.search`, `object_tool`, `prompt`, `range`, `runbooks.search`, `schemas.append`, `str`, `type`

</details>

<a id="fn-ccs-agent_runtime-diagnose"></a>
### `diagnose`

**비동기 함수** · [정의 위치 L119](../../src/ccs/agent_runtime.py#L119)

```python
async diagnose(ai, system, payload, tools, run_dir, *, mode, profile_override=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `Conversation`, `DiagnosisRequest.model_validate`, `DiagnosisResult`, `DiagnosisResult.model_validate`, `DiagnosisResult.model_validate(call.arguments).model_dump`, `Path`, `ProposedChange`, `_CAUSE_BY_PARAM.get`, `a.get`, `activity.emit`, `activity_for_episode`, `ai.keys.values`, `all`, `any`, `call_model`, `complete`, `config.get`, `conv.close`, `conv.result`, `int`, `item.get`, `min`, `model_tool`, `next`, `nodes.get`, `nodes.get(active_switch, {}).get`, `nodes.get(backup_switch, {}).get`, `prompt`, `range`, `read`, `request.constraints.get`, `request.incident.get`, `request.model_dump`, `target.startswith`, `tools.list_tools`, `topology.get`, `type`, `x.get`

</details>

<a id="fn-ccs-agent_runtime-diagnose-complete"></a>
### `diagnose.complete`

**함수 (중첩 handler)** · [정의 위치 L129](../../src/ccs/agent_runtime.py#L129)

```python
diagnose.complete(value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`activity.emit`, `value.get`

</details>

<a id="fn-ccs-agent_runtime-diagnose-read"></a>
### `diagnose.read`

**비동기 함수 (중첩 handler)** · [정의 위치 L135](../../src/ccs/agent_runtime.py#L135)

```python
async diagnose.read(name, arguments)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `tools.call`

</details>

<a id="fn-ccs-agent_runtime-select_change"></a>
### `select_change`

**비동기 함수** · [정의 위치 L199](../../src/ccs/agent_runtime.py#L199)

```python
async select_change(ai, system, diagnosis, run_dir, *, mode, profile_override=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `Conversation`, `Path`, `ProposedChange.model_json_schema`, `ProposedChange.model_validate`, `ProposedChange.model_validate(change).model_dump`, `ValueError`, `activity.emit`, `activity_for_episode`, `ai.keys.values`, `call_model`, `conv.close`, `conv.result`, `diagnosis.get`, `object_tool`, `prompt`, `range`, `type`

</details>

<a id="fn-ccs-agent_runtime-compose_report"></a>
### `compose_report`

**비동기 함수** · [정의 위치 L228](../../src/ccs/agent_runtime.py#L228)

```python
async compose_report(ai, system, facts, run_dir, *, mode, profile_override=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `Conversation`, `Path`, `Report`, `Report.model_json_schema`, `Report.model_validate`, `ValueError`, `activity.emit`, `activity_for_episode`, `ai.keys.values`, `call_model`, `conv.close`, `conv.result`, `facts.get`, `facts.get('diagnosis', {}).get`, `prompt`, `range`, `report.model_dump`, `str`, `type`

</details>

<a id="fn-ccs-agent_runtime-propose_memory"></a>
### `propose_memory`

**비동기 함수** · [정의 위치 L270](../../src/ccs/agent_runtime.py#L270)

```python
async propose_memory(ai, system, report, run_dir, *, mode, profile_override=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentFailure`, `Conversation`, `Path`, `activity.emit`, `activity_for_episode`, `ai.keys.values`, `call.arguments.get`, `call_model`, `conv.close`, `conv.result`, `isinstance`, `object_tool`, `prompt`, `range`, `type`

</details>

<a id="module-ccs-bench-__init__"></a>
## `ccs.bench.__init__`

[소스 파일](../../src/ccs/bench/__init__.py) · [이 폴더 설명](../../src/ccs/bench/README.md)

> 소스의 모듈 설명: Deterministic authoring scenarios for the synthetic NetOps world.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-bench-scenarios"></a>
## `ccs.bench.scenarios`

[소스 파일](../../src/ccs/bench/scenarios.py) · [이 폴더 설명](../../src/ccs/bench/README.md)

> 소스의 모듈 설명: Create deterministic wired W1--W5 and N0 SQLite worlds.

<a id="fn-ccs-bench-scenarios-_json"></a>
### `_json`

**함수** · [정의 위치 L38](../../src/ccs/bench/scenarios.py#L38)

```python
_json(value: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`

</details>

<a id="fn-ccs-bench-scenarios-_config"></a>
### `_config`

**함수** · [정의 위치 L41](../../src/ccs/bench/scenarios.py#L41)

```python
_config(db: sqlite3.Connection, target: str, param: str, value: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_json`, `db.execute`

</details>

<a id="fn-ccs-bench-scenarios-_set_injected_config"></a>
### `_set_injected_config`

**함수** · [정의 위치 L44](../../src/ccs/bench/scenarios.py#L44)

```python
_set_injected_config(db: sqlite3.Connection, target: str, param: str, value: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_json`, `db.execute`

</details>

<a id="fn-ccs-bench-scenarios-_create_normal_world"></a>
### `_create_normal_world`

**함수** · [정의 위치 L47](../../src/ccs/bench/scenarios.py#L47)

```python
_create_normal_world(db: sqlite3.Connection, seed: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_config`, `db.executemany`, `flows.append`, `range`, `str`

</details>

<a id="fn-ccs-bench-scenarios-_inject_fault"></a>
### `_inject_fault`

**함수** · [정의 위치 L87](../../src/ccs/bench/scenarios.py#L87)

```python
_inject_fault(db: sqlite3.Connection, fault_id: str, target: str) -> tuple[str, str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `_set_injected_config`, `db.execute`

</details>

<a id="fn-ccs-bench-scenarios-_request_text"></a>
### `_request_text`

**함수** · [정의 위치 L110](../../src/ccs/bench/scenarios.py#L110)

```python
_request_text(fault_id: str, target: str, ticket_id: str, rng: random.Random) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`rng.choice`

</details>

<a id="fn-ccs-bench-scenarios-_observations"></a>
### `_observations`

**함수** · [정의 위치 L122](../../src/ccs/bench/scenarios.py#L122)

```python
_observations(db: sqlite3.Connection, fault_id: str, target: str, difficulty: str, seed: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`db.execute`, `db.execute("SELECT value FROM metadata WHERE key='logical_clock'").fetchone`, `int`, `len`, `random.Random`, `range`, `rng.shuffle`

</details>

<a id="fn-ccs-bench-scenarios-_registry"></a>
### `_registry`

**함수** · [정의 위치 L143](../../src/ccs/bench/scenarios.py#L143)

```python
_registry(db: sqlite3.Connection, seed: int) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`db.execute`, `enumerate`, `registry.append`

</details>

<a id="fn-ccs-bench-scenarios-create_world"></a>
### `create_world`

**함수** · [정의 위치 L153](../../src/ccs/bench/scenarios.py#L153)

```python
create_world(path: Path, seed: int=1, fault_id: str='W4', target: str='HOST-001', difficulty: str='L1') -> dict[str, Any]
```

> Create a fresh wired DB and return evaluator-only scenario metadata.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `SQLiteBackend`, `ValueError`, `_create_normal_world`, `_inject_fault`, `_observations`, `_registry`, `_request_text`, `allowed_changes.append`, `backend.snapshot`, `db.close`, `db.commit`, `db.execute`, `db.execute("SELECT value FROM metadata WHERE key='logical_clock'").fetchone`, `db.executescript`, `db.rollback`, `difficulty.strip`, `difficulty.strip().upper`, `fault_id.strip`, `fault_id.strip().upper`, `int`, `isinstance`, `path.exists`, `path.parent.mkdir`, `path.unlink`, `random.Random`, `sorted`, `sqlite3.connect`, `target.strip`, `target.strip().upper`

</details>

<a id="module-ccs-budget"></a>
## `ccs.budget`

[소스 파일](../../src/ccs/budget.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Shared cumulative cost reservations, using integer nano-USD and SQLite transactions.

<a id="class-ccs-budget-BudgetExceeded"></a>
### `BudgetExceeded`

**클래스** · [정의 위치 L8](../../src/ccs/budget.py#L8)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-budget-nanos"></a>
### `nanos`

**함수** · [정의 위치 L11](../../src/ccs/budget.py#L11)

```python
nanos(value: Decimal) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(value * Decimal(10 ** 9)).to_integral_value`, `Decimal`, `ValueError`, `int`, `value.is_finite`

</details>

<a id="fn-ccs-budget-token_cost"></a>
### `token_cost`

**함수** · [정의 위치 L15](../../src/ccs/budget.py#L15)

```python
token_cost(profile, input_tokens: int, output_tokens: int, cached_tokens: int=0, cache_write_tokens: int=0) -> Decimal
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Decimal`, `ValueError`, `min`

</details>

<a id="class-ccs-budget-BudgetLedger"></a>
### `BudgetLedger`

**클래스** · [정의 위치 L20](../../src/ccs/budget.py#L20)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-budget-BudgetLedger-__init__"></a>
### `BudgetLedger.__init__`

**메서드** · [정의 위치 L21](../../src/ccs/budget.py#L21)

```python
BudgetLedger.__init__(self, path: Path, limit_usd: Decimal)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `db.execute`, `nanos`, `self.connect`, `self.path.parent.mkdir`

</details>

<a id="fn-ccs-budget-BudgetLedger-connect"></a>
### `BudgetLedger.connect`

**메서드** · [정의 위치 L28](../../src/ccs/budget.py#L28)

```python
BudgetLedger.connect(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`connection.close`, `sqlite3.connect`

</details>

<a id="fn-ccs-budget-BudgetLedger-reserve"></a>
### `BudgetLedger.reserve`

**메서드** · [정의 위치 L34](../../src/ccs/budget.py#L34)

```python
BudgetLedger.reserve(self, estimate: Decimal, model: str, role: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetExceeded`, `db.execute`, `db.execute('SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM calls').fetchone`, `nanos`, `self.connect`, `uuid.uuid4`

</details>

<a id="fn-ccs-budget-BudgetLedger-settle"></a>
### `BudgetLedger.settle`

**메서드** · [정의 위치 L44](../../src/ccs/budget.py#L44)

```python
BudgetLedger.settle(self, identity: str, cost: Decimal | None, status: str='completed')
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `db.execute`, `db.execute('SELECT reserved,status FROM calls WHERE id=?', (identity,)).fetchone`, `nanos`, `self.connect`

</details>

<a id="fn-ccs-budget-BudgetLedger-summary"></a>
### `BudgetLedger.summary`

**메서드** · [정의 위치 L52](../../src/ccs/budget.py#L52)

```python
BudgetLedger.summary(self) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Decimal`, `db.execute`, `self.connect`, `str`

</details>

<a id="module-ccs-cli"></a>
## `ccs.cli`

[소스 파일](../../src/ccs/cli.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: User-facing CLI. Mock is the default; live requests require --mode live.

<a id="fn-ccs-cli-parser"></a>
### `parser`

**함수** · [정의 위치 L15](../../src/ccs/cli.py#L15)

```python
parser()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`argparse.ArgumentParser`, `cli.add_argument`, `cli.add_subparsers`, `commands.add_parser`, `compare.add_argument`, `cost.add_argument`, `monitor.add_argument`, `report.add_argument`, `run.add_argument`, `web.add_argument`, `web_workspace`

</details>

<a id="fn-ccs-cli-main"></a>
### `main`

**함수** · [정의 위치 L52](../../src/ccs/cli.py#L52)

```python
main(argv=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(directory / 'manifest.json').is_file`, `BudgetLedger`, `BudgetLedger(ai.ledger_path, ai.budget_usd).summary`, `DashboardServer`, `DashboardServer(directory, port=args.port).start`, `ValueError`, `WebConsoleServer`, `ai.keys.items`, `ai.profile`, `ai.profiles.values`, `ai_path.exists`, `args.faults.split`, `args.run_dir.resolve`, `args.seeds.split`, `asyncio.run`, `bool`, `compare_runs`, `importlib.metadata.version`, `int`, `isinstance`, `json.dumps`, `load_ai`, `load_system`, `min`, `parser`, `parser().parse_args`, `print`, `run`, `server.stop`, `str`, `system.runbooks.exists`, `time.sleep`, `token_cost`, `tuple`, `type`, `verify_seal`, `viewers.get`, `viewers.pop`, `viewers.pop('console').stop`, `viewers['console'].stop`, `viewers['server'].stop`, `webbrowser.open`

</details>

<a id="fn-ccs-cli-main-created"></a>
### `main.created`

**함수 (중첩 handler)** · [정의 위치 L111](../../src/ccs/cli.py#L111)

```python
main.created(directory)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ConsoleProgress`, `ConsoleProgress(directory, detailed=args.progress == 'detailed').start`, `DashboardServer`, `DashboardServer(directory).start`, `print`, `str`, `webbrowser.open`

</details>

<a id="module-ccs-config"></a>
## `ccs.config`

[소스 파일](../../src/ccs/config.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Strict XML configuration; secret contents never appear in validation errors.

<a id="class-ccs-config-ConfigurationError"></a>
### `ConfigurationError`

**클래스** · [정의 위치 L9](../../src/ccs/config.py#L9)

상속/계약: `ValueError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-config-Profile"></a>
### `Profile`

**클래스** · [정의 위치 L13](../../src/ccs/config.py#L13)

상속/계약: 별도 상속 없음

선언된 필드: `id`, `provider`, `model`, `reasoning_effort`, `max_output_tokens`, `input_rate`, `cached_rate`, `output_rate`, `cache_write_rate`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-config-AIConfig"></a>
### `AIConfig`

**클래스** · [정의 위치 L25](../../src/ccs/config.py#L25)

상속/계약: 별도 상속 없음

선언된 필드: `active_profile`, `profiles`, `keys`, `agent_profiles`, `timeout`, `schema_retries`, `max_input_bytes`, `budget_usd`, `ledger_path`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-config-AIConfig-profile"></a>
### `AIConfig.profile`

**메서드** · [정의 위치 L36](../../src/ccs/config.py#L36)

```python
AIConfig.profile(self, role: str, override: str | None=None) -> Profile
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ConfigurationError`, `self.agent_profiles.get`

</details>

<a id="fn-ccs-config-AIConfig-public"></a>
### `AIConfig.public`

**메서드** · [정의 위치 L42](../../src/ccs/config.py#L42)

```python
AIConfig.public(self) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asdict`, `asdict(p).items`, `isinstance`, `self.profiles.items`, `str`

</details>

<a id="class-ccs-config-SystemConfig"></a>
### `SystemConfig`

**클래스** · [정의 위치 L50](../../src/ccs/config.py#L50)

상속/계약: 별도 상속 없음

선언된 필드: `project_root`, `output_root`, `runbooks`, `prompts`, `host`, `tool_port`, `diagnosis_port`, `startup_timeout`, `request_timeout`, `diagnosis_tool_budget`, `context_steps`, `max_agent_steps`, `read_retries`, `approval`, `memory_enabled`, `memory_k`, `runbook_k`, `seeds`, `faults`, `difficulty`, `target`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-config-SystemConfig-public"></a>
### `SystemConfig.public`

**메서드** · [정의 위치 L73](../../src/ccs/config.py#L73)

```python
SystemConfig.public(self) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asdict`, `asdict(self).items`, `isinstance`, `str`

</details>

<a id="fn-ccs-config-_root"></a>
### `_root`

**함수** · [정의 위치 L76](../../src/ccs/config.py#L76)

```python
_root(path: Path, tag: str)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ConfigurationError`, `ET.parse`, `ET.parse(path).getroot`, `ValueError`, `node.get`

</details>

<a id="fn-ccs-config-_path"></a>
### `_path`

**함수** · [정의 위치 L85](../../src/ccs/config.py#L85)

```python
_path(value: str, base: Path) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(base / path).resolve`, `Path`, `Path(value).expanduser`, `path.is_absolute`

</details>

<a id="fn-ccs-config-_shape"></a>
### `_shape`

**함수** · [정의 위치 L89](../../src/ccs/config.py#L89)

```python
_shape(element, attributes, children=(), optional_attributes=())
```

> Reject typos and duplicate singleton elements before reading any values.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `set`, `sorted`

</details>

<a id="fn-ccs-config-load_ai"></a>
### `load_ai`

**함수** · [정의 위치 L96](../../src/ccs/config.py#L96)

```python
load_ai(path: Path) -> AIConfig
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(key.text or '').strip`, `AIConfig`, `ConfigurationError`, `Decimal`, `Path`, `Path(path).resolve`, `Profile`, `ValueError`, `_path`, `_root`, `_shape`, `a.get`, `agents.get`, `any`, `config.budget_usd.is_finite`, `config.profile`, `float`, `int`, `key.get`, `len`, `list`, `n.is_finite`, `os.environ.get`, `provider.find`, `root.find`, `str`

</details>

<a id="fn-ccs-config-load_system"></a>
### `load_system`

**함수** · [정의 위치 L145](../../src/ccs/config.py#L145)

```python
load_system(path: Path) -> SystemConfig
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ConfigurationError`, `Path`, `Path(__file__).resolve`, `SystemConfig`, `ValueError`, `_path`, `_root`, `_shape`, `any`, `e['faults'].split`, `e['seeds'].split`, `float`, `int`, `root.find`, `root.find('protection').get`, `set`, `tuple`

</details>

<a id="module-ccs-contracts"></a>
## `ccs.contracts`

[소스 파일](../../src/ccs/contracts.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Provider-independent Agent payload contracts.

<a id="class-ccs-contracts-Contract"></a>
### `Contract`

**클래스** · [정의 위치 L5](../../src/ccs/contracts.py#L5)

상속/계약: `BaseModel`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-contracts-ProposedChange"></a>
### `ProposedChange`

**클래스** · [정의 위치 L8](../../src/ccs/contracts.py#L8)

상속/계약: `Contract`

선언된 필드: `target`, `param`, `value`, `reason`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-contracts-DiagnosisRequest"></a>
### `DiagnosisRequest`

**클래스** · [정의 위치 L14](../../src/ccs/contracts.py#L14)

상속/계약: `Contract`

선언된 필드: `schema_version`, `task_id`, `trace_id`, `message_id`, `idempotency_key`, `incident`, `context`, `constraints`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-contracts-DiagnosisResult"></a>
### `DiagnosisResult`

**클래스** · [정의 위치 L24](../../src/ccs/contracts.py#L24)

상속/계약: `Contract`

선언된 필드: `root_cause`, `evidence`, `proposed_change`, `confidence`, `notes`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-contracts-Report"></a>
### `Report`

**클래스** · [정의 위치 L31](../../src/ccs/contracts.py#L31)

상속/계약: `Contract`

선언된 필드: `summary`, `root_cause`, `action`, `outcome`, `evidence`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-contracts-MemoryRecord"></a>
### `MemoryRecord`

**클래스** · [정의 위치 L38](../../src/ccs/contracts.py#L38)

상속/계약: `Contract`

선언된 필드: `record_id`, `scope_id`, `tenant_id`, `purpose`, `written_at`, `expires_at`, `source_event_ids`, `verified_outcome`, `payload`, `items`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-ccs-core-__init__"></a>
## `ccs.core.__init__`

[소스 파일](../../src/ccs/core/__init__.py) · [이 폴더 설명](../../src/ccs/core/README.md)

> 소스의 모듈 설명: D0 gateway, event bus, and artifact integrity primitives.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-core-bus"></a>
## `ccs.core.bus`

[소스 파일](../../src/ccs/core/bus.py) · [이 폴더 설명](../../src/ccs/core/README.md)

> 소스의 모듈 설명: Append-only, per-process disclosure event bus.

<a id="fn-ccs-core-bus-canonical_json_bytes"></a>
### `canonical_json_bytes`

**함수** · [정의 위치 L22](../../src/ccs/core/bus.py#L22)

```python
canonical_json_bytes(value: Any) -> bytes
```

> Return the exact JSON representation used for blob integrity checks.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`, `json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':')).encode`

</details>

<a id="class-ccs-core-bus-EventBus"></a>
### `EventBus`

**클래스** · [정의 위치 L34](../../src/ccs/core/bus.py#L34)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Write one JSONL shard and immutable payload blobs for one process.  A writer ID is a single-writer ownership boundary. Callers may change ``episode_id`` between sequential episodes; the bus then advances the deterministic ``episode_seq`` used by offline merging.

<a id="fn-ccs-core-bus-EventBus-__init__"></a>
### `EventBus.__init__`

**메서드** · [정의 위치 L42](../../src/ccs/core/bus.py#L42)

```python
EventBus.__init__(self, run_dir: Path, writer_id: str, run_id: str, episode_id: str)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `ValueError`, `_NUMBERED_EPISODE.fullmatch`, `_WRITER_ID.fullmatch`, `int`, `isinstance`, `match.group`, `max`, `self._blobs_dir.mkdir`, `self._episode_sequences.values`, `self._events_dir.mkdir`, `self._load_existing_shard`, `threading.Lock`

</details>

<a id="fn-ccs-core-bus-EventBus-episode_id"></a>
### `EventBus.episode_id`

**메서드** · [정의 위치 L73](../../src/ccs/core/bus.py#L73)

```python
EventBus.episode_id(self) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-core-bus-EventBus-episode_id-2"></a>
### `EventBus.episode_id`

**메서드** · [정의 위치 L77](../../src/ccs/core/bus.py#L77)

```python
EventBus.episode_id(self, value: str) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_NUMBERED_EPISODE.fullmatch`, `int`, `match.group`, `max`, `self._episode_sequences.values`

</details>

<a id="fn-ccs-core-bus-EventBus-shard_path"></a>
### `EventBus.shard_path`

**메서드** · [정의 위치 L91](../../src/ccs/core/bus.py#L91)

```python
EventBus.shard_path(self) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-core-bus-EventBus-_load_existing_shard"></a>
### `EventBus._load_existing_shard`

**메서드** · [정의 위치 L94](../../src/ccs/core/bus.py#L94)

```python
EventBus._load_existing_shard(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`DisclosureEvent.model_validate_json`, `ValueError`, `enumerate`, `line.strip`, `max`, `self._episode_sequences.get`, `self._shard_path.exists`, `self._shard_path.open`

</details>

<a id="fn-ccs-core-bus-EventBus-emit"></a>
### `EventBus.emit`

**메서드** · [정의 위치 L115](../../src/ccs/core/bus.py#L115)

```python
EventBus.emit(self, stage: str, payload: Any, source: str, sink: str, *, causation_event_id: str | None=None, transport: str='local', status: str='succeeded', **metadata: Any) -> str
```

> Persist a payload and event, returning the new event ID.  The blob is committed before the JSONL event. A crash can therefore leave an orphan blob, which the integrity gate rejects, but cannot leave an event that appeared valid before its blob existed.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`DisclosureEvent`, `ValueError`, `blob_handle.fileno`, `blob_handle.flush`, `blob_handle.write`, `canonical_json_bytes`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `datetime.now(timezone.utc).isoformat().replace`, `event.model_dump_json`, `event_handle.fileno`, `event_handle.flush`, `event_handle.write`, `hashlib.sha256`, `hashlib.sha256(payload_bytes).hexdigest`, `len`, `metadata.pop`, `os.fsync`, `os.replace`, `self._shard_path.open`, `str`, `uuid.uuid4`, `uuid.uuid5`, `writing_path.exists`, `writing_path.open`, `writing_path.unlink`

</details>

<a id="module-ccs-core-events"></a>
## `ccs.core.events`

[소스 파일](../../src/ccs/core/events.py) · [이 폴더 설명](../../src/ccs/core/README.md)

> 소스의 모듈 설명: Strict event schema shared by the bus and the offline validator.

<a id="class-ccs-core-events-DisclosureEvent"></a>
### `DisclosureEvent`

**클래스** · [정의 위치 L27](../../src/ccs/core/events.py#L27)

상속/계약: `BaseModel`

선언된 필드: `schema_version`, `event_id`, `trace_id`, `span_id`, `parent_span_id`, `causation_event_id`, `run_id`, `episode_id`, `episode_seq`, `task_id`, `writer_id`, `local_seq`, `attempt`, `stage`, `source`, `sink`, `authenticated_principal`, `principal_role`, `purpose`, `payload_ref`, `payload_digest`, `payload_size`, `transport`, `gate_id`, `decision`, `status`, `ts_logical`, `ts_utc`, `metadata`

> A single measured disclosure crossing.  Payload bytes are deliberately absent. ``payload_ref`` points to the restricted blob store and ``payload_digest`` protects those exact bytes.

<a id="fn-ccs-core-events-DisclosureEvent-_valid_utc_timestamp"></a>
### `DisclosureEvent._valid_utc_timestamp`

**메서드** · [정의 위치 L68](../../src/ccs/core/events.py#L68)

```python
DisclosureEvent._valid_utc_timestamp(cls, value: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `datetime.fromisoformat`, `field_validator`, `value.replace`

</details>

<a id="module-ccs-core-gateway"></a>
## `ccs.core.gateway`

[소스 파일](../../src/ccs/core/gateway.py) · [이 폴더 설명](../../src/ccs/core/README.md)

> 소스의 모듈 설명: Protection-free D0 gateway.

<a id="class-ccs-core-gateway-GateTrace"></a>
### `GateTrace`

**클래스** · [정의 위치 L12](../../src/ccs/core/gateway.py#L12)

상속/계약: 별도 상속 없음

선언된 필드: `action`, `rule_ids`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-core-gateway-Gate"></a>
### `Gate`

**클래스** · [정의 위치 L17](../../src/ccs/core/gateway.py#L17)

상속/계약: `Protocol`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-core-gateway-Gate-decide"></a>
### `Gate.decide`

**메서드** · [정의 위치 L18](../../src/ccs/core/gateway.py#L18)

```python
Gate.decide(self, event: dict[str, Any], payload: Any) -> tuple[Any, GateTrace]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-core-gateway-NullGate"></a>
### `NullGate`

**클래스** · [정의 위치 L21](../../src/ccs/core/gateway.py#L21)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> D0 gate: permit the exact input object without copying or mutation.

<a id="fn-ccs-core-gateway-NullGate-decide"></a>
### `NullGate.decide`

**메서드** · [정의 위치 L26](../../src/ccs/core/gateway.py#L26)

```python
NullGate.decide(self, event: dict[str, Any], payload: Any) -> tuple[Any, GateTrace]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`GateTrace`

</details>

<a id="class-ccs-core-gateway-Gateway"></a>
### `Gateway`

**클래스** · [정의 위치 L30](../../src/ccs/core/gateway.py#L30)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-core-gateway-Gateway-__init__"></a>
### `Gateway.__init__`

**메서드** · [정의 위치 L31](../../src/ccs/core/gateway.py#L31)

```python
Gateway.__init__(self, bus: EventBus, gate: Gate | None=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`NullGate`

</details>

<a id="fn-ccs-core-gateway-Gateway-pass_through"></a>
### `Gateway.pass_through`

**메서드** · [정의 위치 L35](../../src/ccs/core/gateway.py#L35)

```python
Gateway.pass_through(self, stage: str, payload: Any, source: str, sink: str, **metadata: Any) -> tuple[Any, str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`dict`, `getattr`, `list`, `self.bus.emit`, `self.gate.decide`, `type`

</details>

<a id="module-ccs-core-integrity"></a>
## `ccs.core.integrity`

[소스 파일](../../src/ccs/core/integrity.py) · [이 폴더 설명](../../src/ccs/core/README.md)

> 소스의 모듈 설명: Offline artifact integrity gate and deterministic causal merge.

<a id="fn-ccs-core-integrity-_load_terminal_episodes"></a>
### `_load_terminal_episodes`

**함수** · [정의 위치 L29](../../src/ccs/core/integrity.py#L29)

```python
_load_terminal_episodes(run_dir: Path, events: list[DisclosureEvent], errors: list[str]) -> set[str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`episode.get`, `errors.append`, `event.metadata.get`, `isinstance`, `json.loads`, `manifest.get`, `manifest_path.exists`, `manifest_path.read_text`, `str`, `str(episode.get('status', '')).lower`, `str(manifest.get('status', '')).lower`, `terminal.add`, `terminal.update`

</details>

<a id="fn-ccs-core-integrity-_event_sort_key"></a>
### `_event_sort_key`

**함수** · [정의 위치 L63](../../src/ccs/core/integrity.py#L63)

```python
_event_sort_key(event: DisclosureEvent) -> tuple[Any, ...]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-core-integrity-_topological_order"></a>
### `_topological_order`

**함수** · [정의 위치 L67](../../src/ccs/core/integrity.py#L67)

```python
_topological_order(events: list[DisclosureEvent], dependencies: dict[str, set[str]]) -> list[DisclosureEvent] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`children[parent].add`, `defaultdict`, `dependencies.items`, `indegree.items`, `len`, `ordered.append`, `ready.append`, `ready.pop`, `ready.sort`, `sorted`

</details>

<a id="fn-ccs-core-integrity-_validate_terminal_pairs"></a>
### `_validate_terminal_pairs`

**함수** · [정의 위치 L93](../../src/ccs/core/integrity.py#L93)

```python
_validate_terminal_pairs(events: list[DisclosureEvent], terminal_episodes: set[str], errors: list[str]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`by_id.get`, `children[event.causation_event_id].append`, `defaultdict`, `errors.append`, `len`, `response_stage.get`, `{'G4.ret': 'G4.call', 'G5.res': 'G5.req'}.get`

</details>

<a id="fn-ccs-core-integrity-_validate_events"></a>
### `_validate_events`

**함수** · [정의 위치 L125](../../src/ccs/core/integrity.py#L125)

```python
_validate_events(run_dir: Path, *, materialize_merge: bool) -> dict[str, Any]
```

> Validate event artifacts, optionally creating ``events_merged.jsonl``.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Counter`, `DisclosureEvent.model_validate`, `TypeError`, `_load_terminal_episodes`, `_topological_order`, `_validate_terminal_pairs`, `actual_blobs.get`, `blob_path.read_bytes`, `blobs_dir.exists`, `blobs_dir.glob`, `by_id.get`, `by_id.setdefault`, `by_span.get`, `by_span.setdefault`, `defaultdict`, `dependencies[event.event_id].add`, `enumerate`, `episode_sequences.items`, `episode_sequences[event.episode_id].add`, `errors.append`, `event.model_dump_json`, `event_ids.add`, `events.append`, `events_dir.exists`, `events_dir.glob`, `handle.fileno`, `handle.flush`, `handle.write`, `hashlib.sha256`, `hashlib.sha256(blob_bytes).hexdigest`, `isinstance`, `json.loads`, `len`, `line.strip`, `list`, `merged_path.exists`, `merged_path.parent.mkdir`, `merged_path.unlink`, `next`, `os.fsync`, `os.replace`, `path.relative_to`, `path.relative_to(run_dir).as_posix`, `payload_refs.items`, `range`, `set`, `shard_path.read_text`, `shard_path.read_text(encoding='utf-8').splitlines`, `shard_sequences.items`, `shard_sequences[event.writer_id].append`, `sorted`, `span_ids.add`, `str`, `writer_sequences.add`, `writing_path.exists`, `writing_path.open`, `writing_path.unlink`

</details>

<a id="fn-ccs-core-integrity-validate_events"></a>
### `validate_events`

**함수** · [정의 위치 L291](../../src/ccs/core/integrity.py#L291)

```python
validate_events(run_dir: Path) -> dict[str, Any]
```

> Validate event artifacts without creating, replacing, or deleting files.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_validate_events`

</details>

<a id="fn-ccs-core-integrity-validate_and_merge"></a>
### `validate_and_merge`

**함수** · [정의 위치 L297](../../src/ccs/core/integrity.py#L297)

```python
validate_and_merge(run_dir: Path) -> dict[str, Any]
```

> Validate event artifacts and create ``events_merged.jsonl`` when valid.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_validate_events`

</details>

<a id="module-ccs-evaluation-__init__"></a>
## `ccs.evaluation.__init__`

[소스 파일](../../src/ccs/evaluation/__init__.py) · [이 폴더 설명](../../src/ccs/evaluation/README.md)

> 소스의 모듈 설명: Independent evaluation helpers.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-evaluation-ledger"></a>
## `ccs.evaluation.ledger`

[소스 파일](../../src/ccs/evaluation/ledger.py) · [이 폴더 설명](../../src/ccs/evaluation/README.md)

> 소스의 모듈 설명: Offline sensitive-item matching over validated restricted payload blobs.

<a id="fn-ccs-evaluation-ledger-_registry_item"></a>
### `_registry_item`

**함수** · [정의 위치 L22](../../src/ccs/evaluation/ledger.py#L22)

```python
_registry_item(raw: dict[str, Any], index: int) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `ValueError`, `any`, `isinstance`, `list`, `raw.get`

</details>

<a id="fn-ccs-evaluation-ledger-_deduplicate_registry"></a>
### `_deduplicate_registry`

**함수** · [정의 위치 L48](../../src/ccs/evaluation/ledger.py#L48)

```python
_deduplicate_registry(registry: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]
```

> Collapse exact bindings without treating a per-world ID as global.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'\x1f'.join`, `'\x1f'.join((*descriptor, normalized_value)).encode`, `ValueError`, `_normal_value`, `_registry_item`, `by_binding.get`, `enumerate`, `hashlib.sha256`, `hashlib.sha256('\x1f'.join((*descriptor, normalized_value)).encode('utf-8')).hexdigest`, `label_by_value.get`, `len`, `set`, `sorted`

</details>

<a id="fn-ccs-evaluation-ledger-_normal_value"></a>
### `_normal_value`

**함수** · [정의 위치 L86](../../src/ccs/evaluation/ledger.py#L86)

```python
_normal_value(field: str, value: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`''.join`, `character.isdigit`, `field.casefold`, `ipaddress.ip_address`, `ipaddress.ip_address(value.strip()).compressed.casefold`, `re.sub`, `re.sub('\\s+', '', value).casefold`, `value.casefold`, `value.strip`, `value.strip().casefold`

</details>

<a id="fn-ccs-evaluation-ledger-_match_count"></a>
### `_match_count`

**함수** · [정의 위치 L100](../../src/ccs/evaluation/ledger.py#L100)

```python
_match_count(field: str, registry_value: str, candidate: str) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'[\\s().+\\-]*'.join`, `_normal_value`, `candidate.casefold`, `field.casefold`, `ipaddress.ip_address`, `ipaddress.ip_address(token).compressed.casefold`, `len`, `re.escape`, `re.findall`, `re.sub`, `re.sub('\\s+', '', token).casefold`, `sum`, `token.strip`

</details>

<a id="fn-ccs-evaluation-ledger-_scalars"></a>
### `_scalars`

**함수** · [정의 위치 L142](../../src/ccs/evaluation/ledger.py#L142)

```python
_scalars(value: Any, path: str='$') -> Iterator[tuple[str, str]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_scalars`, `enumerate`, `isinstance`, `sorted`, `str`

</details>

<a id="fn-ccs-evaluation-ledger-build_ledger"></a>
### `build_ledger`

**함수** · [정의 위치 L157](../../src/ccs/evaluation/ledger.py#L157)

```python
build_ledger(run_dir: Path, registry: list[dict[str, Any]]) -> dict[str, Any]
```

> Build a restricted provenance ledger without returning raw values.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / event.payload_ref).read_text`, `Counter`, `DisclosureEvent.model_validate_json`, `Path`, `TypeError`, `_deduplicate_registry`, `_match_count`, `_normal_value`, `_scalars`, `bool`, `cross_episode_bindings.add`, `defaultdict`, `dict`, `hashlib.sha256`, `hashlib.sha256(normalized_value.encode('utf-8')).hexdigest`, `isinstance`, `json.dumps`, `json.dumps(fingerprint_material, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode`, `json.loads`, `ledger_items.append`, `len`, `line.strip`, `list`, `matching_paths.append`, `merged_path.read_text`, `merged_path.read_text(encoding='utf-8').splitlines`, `normalized_value.encode`, `occurrence_totals.values`, `set`, `sorted`, `stage_counts.items`, `sum`, `traces[binding_id].append`, `unique_crossings.add`, `validate_and_merge`

</details>

<a id="module-ccs-evaluation-oracle"></a>
## `ccs.evaluation.oracle`

[소스 파일](../../src/ccs/evaluation/oracle.py) · [이 폴더 설명](../../src/ccs/evaluation/README.md)

> 소스의 모듈 설명: Final-state oracle independent of agent reports and claimed outcomes.

<a id="fn-ccs-evaluation-oracle-_configuration"></a>
### `_configuration`

**함수** · [정의 위치 L11](../../src/ccs/evaluation/oracle.py#L11)

```python
_configuration(snapshot: dict[str, Any]) -> dict[tuple[str, str], Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-evaluation-oracle-evaluate"></a>
### `evaluate`

**함수** · [정의 위치 L15](../../src/ccs/evaluation/oracle.py#L15)

```python
evaluate(db_path: Path, scenario: dict[str, Any]) -> dict[str, Any]
```

> Judge utility from live DB state, deterministic verify, and preserved state.  The LLM report is deliberately not an input.  Scenario ground truth remains evaluator-side and is used only after the episode reaches a terminal state.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `SQLiteBackend`, `ValueError`, `_configuration`, `actual_changes.append`, `backend.call`, `backend.snapshot`, `bool`, `final_config.get`, `forbidden_changes.append`, `ground_truth.get`, `initial_config.get`, `isinstance`, `scenario.keys`, `set`, `sorted`

</details>

<a id="module-ccs-event_communication"></a>
## `ccs.event_communication`

[소스 파일](../../src/ccs/event_communication.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Display actual message direction and admitted payloads for activity records.  Callers pass already-scrubbed event details. No provider transcript is read here.

<a id="fn-ccs-event_communication-_dict"></a>
### `_dict`

**함수** · [정의 위치 L10](../../src/ccs/event_communication.py#L10)

```python
_dict(value: Any) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="fn-ccs-event_communication-communication_for_event"></a>
### `communication_for_event`

**함수** · [정의 위치 L14](../../src/ccs/event_communication.py#L14)

```python
communication_for_event(event: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_dict`, `context.get`, `context.items`, `details.get`, `details.items`, `event.get`, `request.get`, `request.items`, `section`, `str`

</details>

<a id="fn-ccs-event_communication-communication_for_event-section"></a>
### `communication_for_event.section`

**함수 (중첩 handler)** · [정의 위치 L26](../../src/ccs/event_communication.py#L26)

```python
communication_for_event.section(key: str, ko: str, en: str, value: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`sections.append`

</details>

<a id="module-ccs-event_presentation"></a>
## `ccs.event_presentation`

[소스 파일](../../src/ccs/event_presentation.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Stable, display-only routing for curated activity events.  This module never changes the recorded activity JSONL.  It derives a small presentation envelope from fields already admitted by the monitor so the UI can connect a timeline row to the corresponding topology route and node stage.

<a id="fn-ccs-event_presentation-_mapping"></a>
### `_mapping`

**함수** · [정의 위치 L54](../../src/ccs/event_presentation.py#L54)

```python
_mapping(value: Any) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="fn-ccs-event_presentation-_string"></a>
### `_string`

**함수** · [정의 위치 L58](../../src/ccs/event_presentation.py#L58)

```python
_string(value: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="fn-ccs-event_presentation-_first_string"></a>
### `_first_string`

**함수** · [정의 위치 L62](../../src/ccs/event_presentation.py#L62)

```python
_first_string(*values: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `value.strip`

</details>

<a id="fn-ccs-event_presentation-_target"></a>
### `_target`

**함수** · [정의 위치 L69](../../src/ccs/event_presentation.py#L69)

```python
_target(details: dict[str, Any]) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_first_string`, `_mapping`, `arguments.get`, `change.get`, `details.get`, `diagnosis.get`, `incident.get`, `proposed.get`, `request.get`, `result.get`

</details>

<a id="fn-ccs-event_presentation-_result_count"></a>
### `_result_count`

**함수** · [정의 위치 L88](../../src/ccs/event_presentation.py#L88)

```python
_result_count(details: dict[str, Any]) -> int | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`details.get`, `isinstance`, `len`, `result.get`

</details>

<a id="fn-ccs-event_presentation-_tool_stage"></a>
### `_tool_stage`

**함수** · [정의 위치 L102](../../src/ccs/event_presentation.py#L102)

```python
_tool_stage(tool: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-event_presentation-_payload"></a>
### `_payload`

**함수** · [정의 위치 L114](../../src/ccs/event_presentation.py#L114)

```python
_payload(*, route: str, node: str, submodule: str, actor: str, headline_ko: str, headline_en: str, detail_ko: str, detail_en: str, tool: str='', target: str='', result_count: int | None=None, generic: bool=False, track_active: bool=True) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`

</details>

<a id="fn-ccs-event_presentation-_presentation_for_event"></a>
### `_presentation_for_event`

**함수** · [정의 위치 L149](../../src/ccs/event_presentation.py#L149)

```python
_presentation_for_event(event: dict[str, Any]) -> dict[str, Any]
```

> Return bilingual topology and timeline metadata for one safe event.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_STATUS_EN.get`, `_STATUS_KO.get`, `_first_string`, `_mapping`, `_mapping(details.get('report')).get`, `_mapping(details.get('summary')).get`, `_payload`, `_result_count`, `_string`, `_string(event.get('action')).casefold`, `_string(event.get('component')).casefold`, `_string(event.get('status')).casefold`, `_string(event.get('writer_id')).casefold`, `_target`, `_tool_stage`, `details.get`, `event.get`, `noun_en.lower`, `role.title`

</details>

<a id="fn-ccs-event_presentation-presentation_for_event"></a>
### `presentation_for_event`

**함수** · [정의 위치 L351](../../src/ccs/event_presentation.py#L351)

```python
presentation_for_event(event: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`' / '.join`, `_mapping`, `_mapping(request.get('constraints')).get`, `_presentation_for_event`, `communication_for_event`, `context.get`, `counts.append`, `details.get`, `event.get`, `isinstance`, `len`, `request.get`

</details>

<a id="module-ccs-knowledge-__init__"></a>
## `ccs.knowledge.__init__`

[소스 파일](../../src/ccs/knowledge/__init__.py) · [이 폴더 설명](../../src/ccs/knowledge/README.md)

> 소스의 모듈 설명: Local BM25 runbook retrieval and approved incident memory.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-knowledge-stores"></a>
## `ccs.knowledge.stores`

[소스 파일](../../src/ccs/knowledge/stores.py) · [이 폴더 설명](../../src/ccs/knowledge/README.md)

> 소스의 모듈 설명: SQLite FTS5 stores used by the Operation Agent.

<a id="fn-ccs-knowledge-stores-runbook_files"></a>
### `runbook_files`

**함수** · [정의 위치 L18](../../src/ccs/knowledge/stores.py#L18)

```python
runbook_files(directory: Path) -> list[Path]
```

> List Markdown runbooks, excluding folder README documentation.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`directory.rglob`, `path.name.casefold`, `sorted`

</details>

<a id="fn-ccs-knowledge-stores-_fts_query"></a>
### `_fts_query`

**함수** · [정의 위치 L23](../../src/ccs/knowledge/stores.py#L23)

```python
_fts_query(query: str) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`' OR '.join`, `TypeError`, `_QUERY_TOKEN.findall`, `isinstance`, `query.casefold`

</details>

<a id="fn-ccs-knowledge-stores-_validate_k"></a>
### `_validate_k`

**함수** · [정의 위치 L32](../../src/ccs/knowledge/stores.py#L32)

```python
_validate_k(k: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `type`

</details>

<a id="fn-ccs-knowledge-stores-_connect"></a>
### `_connect`

**함수** · [정의 위치 L37](../../src/ccs/knowledge/stores.py#L37)

```python
_connect(path: Path) -> sqlite3.Connection
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `connection.execute`, `isinstance`, `path.parent.mkdir`, `sqlite3.connect`

</details>

<a id="fn-ccs-knowledge-stores-_parse_runbook"></a>
### `_parse_runbook`

**함수** · [정의 위치 L48](../../src/ccs/knowledge/stores.py#L48)

```python
_parse_runbook(path: Path) -> tuple[dict[str, str], str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'\n'.join`, `'\n'.join(lines[closing + 1:]).strip`, `ValueError`, `enumerate`, `key.strip`, `line.lstrip`, `line.lstrip().startswith`, `line.partition`, `line.strip`, `lines[0].strip`, `metadata.keys`, `next`, `path.read_text`, `sorted`, `text.splitlines`, `value.strip`, `value.strip().strip`

</details>

<a id="fn-ccs-knowledge-stores-_chunks"></a>
### `_chunks`

**함수** · [정의 위치 L77](../../src/ccs/knowledge/stores.py#L77)

```python
_chunks(doc_id: str, body: str) -> list[tuple[str, str]]
```

> Split at level-two headings while retaining the document title.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'\n'.join`, `'\n'.join(lines).strip`, `body.splitlines`, `chunks.append`, `current.append`, `enumerate`, `line.startswith`, `title_lines.append`, `title_lines.copy`

</details>

<a id="class-ccs-knowledge-stores-RunbookStore"></a>
### `RunbookStore`

**클래스** · [정의 위치 L105](../../src/ccs/knowledge/stores.py#L105)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Deterministic local BM25 index over the checked-in English runbooks.

<a id="fn-ccs-knowledge-stores-RunbookStore-__init__"></a>
### `RunbookStore.__init__`

**메서드** · [정의 위치 L108](../../src/ccs/knowledge/stores.py#L108)

```python
RunbookStore.__init__(self, db_path: Path, documents_dir: Path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FileNotFoundError`, `RuntimeError`, `TypeError`, `_connect`, `documents_dir.is_dir`, `isinstance`, `self._rebuild`, `self.connection.close`, `self.connection.execute`

</details>

<a id="fn-ccs-knowledge-stores-RunbookStore-_rebuild"></a>
### `RunbookStore._rebuild`

**메서드** · [정의 위치 L133](../../src/ccs/knowledge/stores.py#L133)

```python
RunbookStore._rebuild(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_chunks`, `_parse_runbook`, `doc_ids.add`, `json.dumps`, `rows.append`, `runbook_files`, `self.connection.execute`, `self.connection.executemany`, `set`

</details>

<a id="fn-ccs-knowledge-stores-RunbookStore-search"></a>
### `RunbookStore.search`

**메서드** · [정의 위치 L158](../../src/ccs/knowledge/stores.py#L158)

```python
RunbookStore.search(self, query: str, k: int=3) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_fts_query`, `_validate_k`, `float`, `json.loads`, `self.connection.execute`

</details>

<a id="fn-ccs-knowledge-stores-RunbookStore-close"></a>
### `RunbookStore.close`

**메서드** · [정의 위치 L184](../../src/ccs/knowledge/stores.py#L184)

```python
RunbookStore.close(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.connection.close`

</details>

<a id="fn-ccs-knowledge-stores-RunbookStore-__enter__"></a>
### `RunbookStore.__enter__`

**메서드** · [정의 위치 L187](../../src/ccs/knowledge/stores.py#L187)

```python
RunbookStore.__enter__(self) -> 'RunbookStore'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-knowledge-stores-RunbookStore-__exit__"></a>
### `RunbookStore.__exit__`

**메서드** · [정의 위치 L190](../../src/ccs/knowledge/stores.py#L190)

```python
RunbookStore.__exit__(self, *_: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.close`

</details>

<a id="class-ccs-knowledge-stores-MemoryStore"></a>
### `MemoryStore`

**클래스** · [정의 위치 L194](../../src/ccs/knowledge/stores.py#L194)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Run-local incident memory shared by sequential episodes.  D0 deliberately applies no tenant, scope, or expiry filtering at read time. That unprotected behavior is measurable, while write eligibility remains a baseline safety condition controlled by the runner/operator simulator.

<a id="fn-ccs-knowledge-stores-MemoryStore-__init__"></a>
### `MemoryStore.__init__`

**메서드** · [정의 위치 L202](../../src/ccs/knowledge/stores.py#L202)

```python
MemoryStore.__init__(self, db_path: Path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `_connect`, `self.connection.close`, `self.connection.commit`, `self.connection.execute`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-write"></a>
### `MemoryStore.write`

**메서드** · [정의 위치 L237](../../src/ccs/knowledge/stores.py#L237)

```python
MemoryStore.write(self, record: dict[str, Any] | MemoryRecord, *, verified: bool, approved: bool) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MemoryRecord.model_validate`, `PermissionError`, `ValueError`, `isinstance`, `self._insert`, `validated.verified_outcome.strip`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-import_reference"></a>
### `MemoryStore.import_reference`

**메서드** · [정의 위치 L253](../../src/ccs/knowledge/stores.py#L253)

```python
MemoryStore.import_reference(self, reference: dict[str, Any], *, operator_seeded_experimental_context: bool) -> str
```

> Import an unverified operator reference without weakening normal writes.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MemoryRecord`, `PermissionError`, `TypeError`, `ValueError`, `isinstance`, `normalized.get`, `self._insert`, `set`, `value.strip`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-_insert"></a>
### `MemoryStore._insert`

**메서드** · [정의 위치 L299](../../src/ccs/knowledge/stores.py#L299)

```python
MemoryStore._insert(self, validated: MemoryRecord) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`' '.join`, `ValueError`, `json.dumps`, `self.connection.execute`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-search"></a>
### `MemoryStore.search`

**메서드** · [정의 위치 L352](../../src/ccs/knowledge/stores.py#L352)

```python
MemoryStore.search(self, query: str, k: int=3) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_fts_query`, `_validate_k`, `float`, `json.loads`, `self.connection.execute`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-close"></a>
### `MemoryStore.close`

**메서드** · [정의 위치 L385](../../src/ccs/knowledge/stores.py#L385)

```python
MemoryStore.close(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.connection.close`

</details>

<a id="fn-ccs-knowledge-stores-MemoryStore-__enter__"></a>
### `MemoryStore.__enter__`

**메서드** · [정의 위치 L388](../../src/ccs/knowledge/stores.py#L388)

```python
MemoryStore.__enter__(self) -> 'MemoryStore'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-knowledge-stores-MemoryStore-__exit__"></a>
### `MemoryStore.__exit__`

**메서드** · [정의 위치 L391](../../src/ccs/knowledge/stores.py#L391)

```python
MemoryStore.__exit__(self, *_: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.close`

</details>

<a id="module-ccs-llm"></a>
## `ccs.llm`

[소스 파일](../../src/ccs/llm.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Native OpenAI Responses and Anthropic Messages tool-use adapters.

<a id="class-ccs-llm-ProviderError"></a>
### `ProviderError`

**클래스** · [정의 위치 L14](../../src/ccs/llm.py#L14)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-llm-ProviderSchemaError"></a>
### `ProviderSchemaError`

**클래스** · [정의 위치 L17](../../src/ccs/llm.py#L17)

상속/계약: `ProviderError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-llm-ToolCall"></a>
### `ToolCall`

**클래스** · [정의 위치 L21](../../src/ccs/llm.py#L21)

상속/계약: 별도 상속 없음

선언된 필드: `id`, `name`, `arguments`

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-llm-_decision_fields"></a>
### `_decision_fields`

**함수** · [정의 위치 L28](../../src/ccs/llm.py#L28)

```python
_decision_fields(value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_decision_fields`, `isinstance`, `value.items`

</details>

<a id="class-ccs-llm-Conversation"></a>
### `Conversation`

**클래스** · [정의 위치 L42](../../src/ccs/llm.py#L42)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-llm-Conversation-__init__"></a>
### `Conversation.__init__`

**메서드** · [정의 위치 L43](../../src/ccs/llm.py#L43)

```python
Conversation.__init__(self, config: AIConfig, role: str, system: str, user: dict | str, log_dir: Path, profile_override: str | None=None, *, activity: ActivityLog | None=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AsyncAnthropic`, `AsyncOpenAI`, `BudgetLedger`, `ConfigurationError`, `Path`, `activity_for_episode`, `config.keys.get`, `config.keys.values`, `config.profile`, `isinstance`, `json.dumps`, `self.log_path.parent.mkdir`

</details>

<a id="fn-ccs-llm-Conversation-close"></a>
### `Conversation.close`

**비동기 메서드** · [정의 위치 L60](../../src/ccs/llm.py#L60)

```python
async Conversation.close(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.client.close`

</details>

<a id="fn-ccs-llm-Conversation-feedback"></a>
### `Conversation.feedback`

**메서드** · [정의 위치 L63](../../src/ccs/llm.py#L63)

```python
Conversation.feedback(self, text: str)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.activity.emit`, `self.history.append`

</details>

<a id="fn-ccs-llm-Conversation-result"></a>
### `Conversation.result`

**메서드** · [정의 위치 L67](../../src/ccs/llm.py#L67)

```python
Conversation.result(self, call: ToolCall, result: dict | list)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `json.dumps`, `self.activity.emit`, `self.history.append`, `self.history[-1].get`, `self.history[-1]['content'].append`

</details>

<a id="fn-ccs-llm-Conversation-_log"></a>
### `Conversation._log`

**메서드** · [정의 위치 L80](../../src/ccs/llm.py#L80)

```python
Conversation._log(self, record)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`f.write`, `json.dumps`, `self.log_path.open`

</details>

<a id="fn-ccs-llm-Conversation-next"></a>
### `Conversation.next`

**비동기 메서드** · [정의 위치 L84](../../src/ccs/llm.py#L84)

```python
async Conversation.next(self, schemas: list[dict], *, attempt: int=1) -> list[ToolCall]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Decimal`, `ProviderError`, `ProviderSchemaError`, `ToolCall`, `_decision_fields`, `all`, `any`, `body.get`, `error.get`, `getattr`, `hashlib.sha256`, `hashlib.sha256(serialized.encode()).hexdigest`, `isinstance`, `item.model_dump`, `json.dumps`, `json.loads`, `len`, `raw.get`, `re.sub`, `response.model_dump`, `safe_details.replace`, `schema.get`, `self._log`, `self.activity.emit`, `self.client.messages.create`, `self.client.responses.create`, `self.config.keys.values`, `self.history.append`, `self.history.extend`, `self.ledger.reserve`, `self.ledger.settle`, `serialized.encode`, `str`, `time.monotonic`, `token_cost`, `type`

</details>

<a id="fn-ccs-llm-object_tool"></a>
### `object_tool`

**함수** · [정의 위치 L174](../../src/ccs/llm.py#L174)

```python
object_tool(name: str, description: str, properties: dict, required: list[str] | None=None) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-llm-model_tool"></a>
### `model_tool`

**함수** · [정의 위치 L177](../../src/ccs/llm.py#L177)

```python
model_tool(name: str, description: str, model) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`model.model_json_schema`

</details>

<a id="module-ccs-monitor"></a>
## `ccs.monitor`

[소스 파일](../../src/ccs/monitor.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Safe, local-only live monitor for curated CCS activity events.  The monitor deliberately reads only ``activity/*.jsonl`` plus an allow-list of fields from ``manifest.json`` and ``summary.json``.  Restricted event blobs, model transcripts, configuration files, and episode payloads are outside its read boundary.

<a id="fn-ccs-monitor-_json_safe"></a>
### `_json_safe`

**함수** · [정의 위치 L47](../../src/ccs/monitor.py#L47)

```python
_json_safe(value: Any, *, depth: int=0) -> Any
```

> Copy JSON-like detail data while suppressing credential/reasoning fields.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_json_safe`, `any`, `isinstance`, `lowered.endswith`, `str`, `text_key.casefold`, `value.items`

</details>

<a id="fn-ccs-monitor-_text"></a>
### `_text`

**함수** · [정의 위치 L80](../../src/ccs/monitor.py#L80)

```python
_text(value: Any, default: str='') -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="fn-ccs-monitor-_integer"></a>
### `_integer`

**함수** · [정의 위치 L84](../../src/ccs/monitor.py#L84)

```python
_integer(value: Any, default: int=0) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="fn-ccs-monitor-_normalize_event"></a>
### `_normalize_event`

**함수** · [정의 위치 L88](../../src/ccs/monitor.py#L88)

```python
_normalize_event(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_integer`, `_json_safe`, `_text`, `_text(value.get('component')).casefold`, `_text(value.get('status')).casefold`, `isinstance`, `presentation_for_event`, `value.get`

</details>

<a id="fn-ccs-monitor-_timestamp_key"></a>
### `_timestamp_key`

**함수** · [정의 위치 L115](../../src/ccs/monitor.py#L115)

```python
_timestamp_key(value: str) -> tuple[int, str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`datetime.fromisoformat`, `int`, `parsed.replace`, `parsed.timestamp`, `value.replace`

</details>

<a id="fn-ccs-monitor-_event_sort_key"></a>
### `_event_sort_key`

**함수** · [정의 위치 L125](../../src/ccs/monitor.py#L125)

```python
_event_sort_key(event: dict[str, Any]) -> tuple[Any, ...]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_timestamp_key`

</details>

<a id="fn-ccs-monitor-_activity_files"></a>
### `_activity_files`

**함수** · [정의 위치 L130](../../src/ccs/monitor.py#L130)

```python
_activity_files(run_dir: Path) -> list[Path]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`activity_dir.is_dir`, `activity_dir.iterdir`, `activity_dir.resolve`, `files.append`, `path.is_file`, `path.resolve`, `path.resolve().is_relative_to`, `path.suffix.casefold`, `sorted`

</details>

<a id="fn-ccs-monitor-_read_incremental"></a>
### `_read_incremental`

**함수** · [정의 위치 L145](../../src/ccs/monitor.py#L145)

```python
_read_incremental(run_dir: Path, offsets: dict[str, int] | None=None) -> tuple[list[dict[str, Any]], dict[str, int]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_activity_files`, `_normalize_event`, `chunk.rfind`, `complete.splitlines`, `events.append`, `events.sort`, `isinstance`, `json.loads`, `offsets.get`, `path.open`, `path.stat`, `raw_line.decode`, `raw_line.strip`, `stream.read`, `stream.seek`

</details>

<a id="fn-ccs-monitor-read_activity"></a>
### `read_activity`

**함수** · [정의 위치 L179](../../src/ccs/monitor.py#L179)

```python
read_activity(run_dir: str | Path) -> list[dict[str, Any]]
```

> Return a normalized display-order snapshot of all complete activity lines.  A trailing line without a newline is treated as an in-progress append.  Wall clock order is useful for display but does not prove total causality.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(run_dir).resolve`, `_read_incremental`

</details>

<a id="fn-ccs-monitor-_safe_json_object"></a>
### `_safe_json_object`

**함수** · [정의 위치 L190](../../src/ccs/monitor.py#L190)

```python
_safe_json_object(run_dir: Path, name: str) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `json.loads`, `path.is_file`, `path.read_text`, `path.resolve`, `path.resolve().is_relative_to`, `run_dir.resolve`

</details>

<a id="fn-ccs-monitor-_metadata"></a>
### `_metadata`

**함수** · [정의 위치 L201](../../src/ccs/monitor.py#L201)

```python
_metadata(run_dir: Path) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_activity_files`, `_json_safe`, `_safe_json_object`, `bool`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `episode.get`, `episodes.append`, `isinstance`, `manifest.get`, `manifest_public.get`, `str`, `str(manifest_public.get('status', summary_public.get('status', 'UNKNOWN'))).upper`, `summary.get`, `summary_public.get`

</details>

<a id="fn-ccs-monitor-_encode_cursor"></a>
### `_encode_cursor`

**함수** · [정의 위치 L276](../../src/ccs/monitor.py#L276)

```python
_encode_cursor(offsets: dict[str, int]) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`base64.urlsafe_b64encode`, `base64.urlsafe_b64encode(payload).decode`, `base64.urlsafe_b64encode(payload).decode('ascii').rstrip`, `json.dumps`, `json.dumps(offsets, separators=(',', ':'), sort_keys=True).encode`

</details>

<a id="fn-ccs-monitor-_decode_cursor"></a>
### `_decode_cursor`

**함수** · [정의 위치 L281](../../src/ccs/monitor.py#L281)

```python
_decode_cursor(value: str) -> dict[str, int]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`base64.urlsafe_b64decode`, `decoded.items`, `isinstance`, `json.loads`, `len`, `raw.decode`, `str`

</details>

<a id="fn-ccs-monitor-_legacy_document"></a>
### `_legacy_document`

**함수** · [정의 위치 L332](../../src/ccs/monitor.py#L332)

```python
_legacy_document(snapshot_payload: dict[str, Any] | None=None) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`''.join`, `embedded.replace`, `embedded.replace('&', '\\u0026').replace`, `embedded.replace('&', '\\u0026').replace('&lt;', '\\u003c').replace`, `embedded.replace('\u2028', '\\u2028').replace`, `json.dumps`

</details>

<a id="fn-ccs-monitor-_document"></a>
### `_document`

**함수** · [정의 위치 L662](../../src/ccs/monitor.py#L662)

```python
_document(snapshot_payload: dict[str, Any] | None=None) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`''.join`, `embedded.replace`, `embedded.replace('&', '\\u0026').replace`, `embedded.replace('&', '\\u0026').replace('&lt;', '\\u003c').replace`, `embedded.replace('\u2028', '\\u2028').replace`, `json.dumps`

</details>

<a id="fn-ccs-monitor-write_snapshot"></a>
### `write_snapshot`

**함수** · [정의 위치 L697](../../src/ccs/monitor.py#L697)

```python
write_snapshot(run_dir: str | Path) -> Path
```

> Write a standalone, offline ``monitor.html`` beside the run artifacts.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FileNotFoundError`, `Path`, `Path(run_dir).resolve`, `_document`, `_metadata`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `read_activity`, `root.is_dir`, `writing.replace`, `writing.write_text`

</details>

<a id="class-ccs-monitor-_MonitorHTTPServer"></a>
### `_MonitorHTTPServer`

**클래스** · [정의 위치 L710](../../src/ccs/monitor.py#L710)

상속/계약: `ThreadingHTTPServer`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-monitor-DashboardServer"></a>
### `DashboardServer`

**클래스** · [정의 위치 L715](../../src/ccs/monitor.py#L715)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Serve the activity monitor on loopback with an unguessable URL token.

<a id="fn-ccs-monitor-DashboardServer-__init__"></a>
### `DashboardServer.__init__`

**메서드** · [정의 위치 L718](../../src/ccs/monitor.py#L718)

```python
DashboardServer.__init__(self, run_dir: str | Path, port: int=0)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FileNotFoundError`, `Path`, `Path(run_dir).resolve`, `ValueError`, `isinstance`, `secrets.token_urlsafe`, `self.run_dir.is_dir`

</details>

<a id="fn-ccs-monitor-DashboardServer-start"></a>
### `DashboardServer.start`

**메서드** · [정의 위치 L730](../../src/ccs/monitor.py#L730)

```python
DashboardServer.start(self) -> 'DashboardServer'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_MonitorHTTPServer`, `int`, `partial`, `quote`, `self._thread.start`, `threading.Thread`

</details>

<a id="fn-ccs-monitor-DashboardServer-stop"></a>
### `DashboardServer.stop`

**메서드** · [정의 위치 L742](../../src/ccs/monitor.py#L742)

```python
DashboardServer.stop(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`server.server_close`, `server.shutdown`, `thread.join`, `threading.current_thread`

</details>

<a id="fn-ccs-monitor-DashboardServer-__enter__"></a>
### `DashboardServer.__enter__`

**메서드** · [정의 위치 L752](../../src/ccs/monitor.py#L752)

```python
DashboardServer.__enter__(self) -> 'DashboardServer'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.start`

</details>

<a id="fn-ccs-monitor-DashboardServer-__exit__"></a>
### `DashboardServer.__exit__`

**메서드** · [정의 위치 L755](../../src/ccs/monitor.py#L755)

```python
DashboardServer.__exit__(self, *_: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.stop`

</details>

<a id="class-ccs-monitor-_DashboardHandler"></a>
### `_DashboardHandler`

**클래스** · [정의 위치 L759](../../src/ccs/monitor.py#L759)

상속/계약: `BaseHTTPRequestHandler`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-monitor-_DashboardHandler-__init__"></a>
### `_DashboardHandler.__init__`

**메서드** · [정의 위치 L762](../../src/ccs/monitor.py#L762)

```python
_DashboardHandler.__init__(self, *args: Any, dashboard: DashboardServer, **kwargs: Any)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`super`, `super().__init__`

</details>

<a id="fn-ccs-monitor-_DashboardHandler-log_message"></a>
### `_DashboardHandler.log_message`

**메서드** · [정의 위치 L766](../../src/ccs/monitor.py#L766)

```python
_DashboardHandler.log_message(self, _format: str, *args: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-monitor-_DashboardHandler-_headers"></a>
### `_DashboardHandler._headers`

**메서드** · [정의 위치 L769](../../src/ccs/monitor.py#L769)

```python
_DashboardHandler._headers(self, content_type: str, length: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.send_header`, `str`

</details>

<a id="fn-ccs-monitor-_DashboardHandler-_send"></a>
### `_DashboardHandler._send`

**메서드** · [정의 위치 L782](../../src/ccs/monitor.py#L782)

```python
_DashboardHandler._send(self, status: HTTPStatus, body: bytes, content_type: str='text/plain; charset=utf-8') -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`len`, `self._headers`, `self.end_headers`, `self.send_response`, `self.wfile.write`

</details>

<a id="fn-ccs-monitor-_DashboardHandler-do_HEAD"></a>
### `_DashboardHandler.do_HEAD`

**메서드** · [정의 위치 L789](../../src/ccs/monitor.py#L789)

```python
_DashboardHandler.do_HEAD(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.do_GET`

</details>

<a id="fn-ccs-monitor-_DashboardHandler-do_GET"></a>
### `_DashboardHandler.do_GET`

**메서드** · [정의 위치 L792](../../src/ccs/monitor.py#L792)

```python
_DashboardHandler.do_GET(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_decode_cursor`, `_document`, `_document().encode`, `_encode_cursor`, `_metadata`, `_read_incremental`, `hmac.compare_digest`, `json.dumps`, `json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode`, `parse_qs`, `query.get`, `self._send`, `urlsplit`

</details>

<a id="module-ccs-monitor_i18n"></a>
## `ccs.monitor_i18n`

[소스 파일](../../src/ccs/monitor_i18n.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Bilingual strings for the standalone activity monitor.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-netops-__init__"></a>
## `ccs.netops.__init__`

[소스 파일](../../src/ccs/netops/__init__.py) · [이 폴더 설명](../../src/ccs/netops/README.md)

> 소스의 모듈 설명: Stable network-tool contract and deterministic SQLite implementation.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-netops-backend"></a>
## `ccs.netops.backend`

[소스 파일](../../src/ccs/netops/backend.py) · [이 폴더 설명](../../src/ccs/netops/README.md)

> 소스의 모듈 설명: Backend-neutral interface used by Network Tools handlers.

<a id="class-ccs-netops-backend-NetworkBackend"></a>
### `NetworkBackend`

**클래스** · [정의 위치 L7](../../src/ccs/netops/backend.py#L7)

상속/계약: `Protocol`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Stateful backend contract; concrete storage is deliberately hidden.

<a id="fn-ccs-netops-backend-NetworkBackend-call"></a>
### `NetworkBackend.call`

**메서드** · [정의 위치 L10](../../src/ccs/netops/backend.py#L10)

```python
NetworkBackend.call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-backend-NetworkBackend-snapshot"></a>
### `NetworkBackend.snapshot`

**메서드** · [정의 위치 L12](../../src/ccs/netops/backend.py#L12)

```python
NetworkBackend.snapshot(self) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-backend-NetworkBackend-close"></a>
### `NetworkBackend.close`

**메서드** · [정의 위치 L14](../../src/ccs/netops/backend.py#L14)

```python
NetworkBackend.close(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-ccs-netops-errors"></a>
## `ccs.netops.errors`

[소스 파일](../../src/ccs/netops/errors.py) · [이 폴더 설명](../../src/ccs/netops/README.md)

> 소스의 모듈 설명: Explicit contract failures raised by NetworkBackend implementations.

<a id="class-ccs-netops-errors-BackendError"></a>
### `BackendError`

**클래스** · [정의 위치 L4](../../src/ccs/netops/errors.py#L4)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Base class for backend failures.

<a id="class-ccs-netops-errors-ContractError"></a>
### `ContractError`

**클래스** · [정의 위치 L8](../../src/ccs/netops/errors.py#L8)

상속/계약: `BackendError`, `ValueError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A tool call did not satisfy its declared schema.

<a id="class-ccs-netops-errors-UnknownToolError"></a>
### `UnknownToolError`

**클래스** · [정의 위치 L12](../../src/ccs/netops/errors.py#L12)

상속/계약: `ContractError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> The requested tool is outside the stable tool contract.

<a id="class-ccs-netops-errors-NotFoundError"></a>
### `NotFoundError`

**클래스** · [정의 위치 L16](../../src/ccs/netops/errors.py#L16)

상속/계약: `BackendError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A requested network entity, preview, change, or ticket does not exist.

<a id="class-ccs-netops-errors-VersionConflictError"></a>
### `VersionConflictError`

**클래스** · [정의 위치 L20](../../src/ccs/netops/errors.py#L20)

상속/계약: `BackendError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A preview or rollback was based on stale network state.

<a id="class-ccs-netops-errors-IdempotencyConflictError"></a>
### `IdempotencyConflictError`

**클래스** · [정의 위치 L24](../../src/ccs/netops/errors.py#L24)

상속/계약: `BackendError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> An idempotency key was reused for a different request.

<a id="class-ccs-netops-errors-ChangeConflictError"></a>
### `ChangeConflictError`

**클래스** · [정의 위치 L28](../../src/ccs/netops/errors.py#L28)

상속/계약: `BackendError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A valid object cannot be changed in its current lifecycle state.

<a id="module-ccs-netops-sqlite_backend"></a>
## `ccs.netops.sqlite_backend`

[소스 파일](../../src/ccs/netops/sqlite_backend.py) · [이 폴더 설명](../../src/ccs/netops/README.md)

> 소스의 모듈 설명: Deterministic, stateful wired network backed by SQLite.

<a id="fn-ccs-netops-sqlite_backend-_json"></a>
### `_json`

**함수** · [정의 위치 L17](../../src/ccs/netops/sqlite_backend.py#L17)

```python
_json(value: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`

</details>

<a id="fn-ccs-netops-sqlite_backend-_decode"></a>
### `_decode`

**함수** · [정의 위치 L20](../../src/ccs/netops/sqlite_backend.py#L20)

```python
_decode(value: str) -> Any
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.loads`

</details>

<a id="fn-ccs-netops-sqlite_backend-_hash"></a>
### `_hash`

**함수** · [정의 위치 L23](../../src/ccs/netops/sqlite_backend.py#L23)

```python
_hash(value: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_json`, `_json(value).encode`, `hashlib.sha256`, `hashlib.sha256(_json(value).encode('utf-8')).hexdigest`

</details>

<a id="class-ccs-netops-sqlite_backend-SQLiteBackend"></a>
### `SQLiteBackend`

**클래스** · [정의 위치 L26](../../src/ccs/netops/sqlite_backend.py#L26)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Implement the stable NetworkBackend contract over a wired world DB.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-__init__"></a>
### `SQLiteBackend.__init__`

**메서드** · [정의 위치 L30](../../src/ccs/netops/sqlite_backend.py#L30)

```python
SQLiteBackend.__init__(self, path: Path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `FileNotFoundError`, `Path`, `dict`, `metadata.get`, `self._connection.execute`, `self.close`, `self.path.is_file`, `sqlite3.connect`, `threading.RLock`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-__enter__"></a>
### `SQLiteBackend.__enter__`

**메서드** · [정의 위치 L45](../../src/ccs/netops/sqlite_backend.py#L45)

```python
SQLiteBackend.__enter__(self) -> 'SQLiteBackend'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-__exit__"></a>
### `SQLiteBackend.__exit__`

**메서드** · [정의 위치 L46](../../src/ccs/netops/sqlite_backend.py#L46)

```python
SQLiteBackend.__exit__(self, *_: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.close`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-close"></a>
### `SQLiteBackend.close`

**메서드** · [정의 위치 L47](../../src/ccs/netops/sqlite_backend.py#L47)

```python
SQLiteBackend.close(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`connection.close`, `getattr`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_db"></a>
### `SQLiteBackend._db`

**메서드** · [정의 위치 L52](../../src/ccs/netops/sqlite_backend.py#L52)

```python
SQLiteBackend._db(self) -> sqlite3.Connection
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_meta_int"></a>
### `SQLiteBackend._meta_int`

**메서드** · [정의 위치 L56](../../src/ccs/netops/sqlite_backend.py#L56)

```python
SQLiteBackend._meta_int(self, key: str) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `int`, `self._db.execute`, `self._db.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_set_meta_int"></a>
### `SQLiteBackend._set_meta_int`

**메서드** · [정의 위치 L61](../../src/ccs/netops/sqlite_backend.py#L61)

```python
SQLiteBackend._set_meta_int(self, key: str, value: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._db.execute`, `str`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_state_version"></a>
### `SQLiteBackend._state_version`

**메서드** · [정의 위치 L64](../../src/ccs/netops/sqlite_backend.py#L64)

```python
SQLiteBackend._state_version(self) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._meta_int`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_arguments"></a>
### `SQLiteBackend._arguments`

**메서드** · [정의 위치 L67](../../src/ccs/netops/sqlite_backend.py#L67)

```python
SQLiteBackend._arguments(arguments: dict[str, Any], *, required: set[str], allowed: set[str]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `arguments.keys`, `isinstance`, `sorted`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_text"></a>
### `SQLiteBackend._text`

**메서드** · [정의 위치 L74](../../src/ccs/netops/sqlite_backend.py#L74)

```python
SQLiteBackend._text(value: Any, name: str, *, maximum: int=256) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `isinstance`, `len`, `value.strip`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_limit"></a>
### `SQLiteBackend._limit`

**메서드** · [정의 위치 L81](../../src/ccs/netops/sqlite_backend.py#L81)

```python
SQLiteBackend._limit(value: Any, default: int, maximum: int) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `isinstance`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-call"></a>
### `SQLiteBackend.call`

**메서드** · [정의 위치 L86](../../src/ccs/netops/sqlite_backend.py#L86)

```python
SQLiteBackend.call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`UnknownToolError`, `handler`, `isinstance`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_list_alarms"></a>
### `SQLiteBackend._list_alarms`

**메서드** · [정의 위치 L98](../../src/ccs/netops/sqlite_backend.py#L98)

```python
SQLiteBackend._list_alarms(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`arguments.get`, `dict`, `len`, `params.append`, `self._arguments`, `self._db.execute`, `self._limit`, `self._meta_int`, `self._state_version`, `self._text`, `self._text(arguments['scope'], 'scope').upper`, `set`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_get_logs"></a>
### `SQLiteBackend._get_logs`

**메서드** · [정의 위치 L108](../../src/ccs/netops/sqlite_backend.py#L108)

```python
SQLiteBackend._get_logs(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `arguments.get`, `dict`, `len`, `params.append`, `self._arguments`, `self._db.execute`, `self._limit`, `self._meta_int`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`, `self._text(severity, 'severity').upper`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_get_config"></a>
### `SQLiteBackend._get_config`

**메서드** · [정의 위치 L121](../../src/ccs/netops/sqlite_backend.py#L121)

```python
SQLiteBackend._get_config(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `NotFoundError`, `_decode`, `all`, `arguments.get`, `isinstance`, `items.append`, `len`, `self._arguments`, `self._db.execute`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`, `set`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_node"></a>
### `SQLiteBackend._node`

**메서드** · [정의 위치 L135](../../src/ccs/netops/sqlite_backend.py#L135)

```python
SQLiteBackend._node(row: sqlite3.Row) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_interface"></a>
### `SQLiteBackend._interface`

**메서드** · [정의 위치 L139](../../src/ccs/netops/sqlite_backend.py#L139)

```python
SQLiteBackend._interface(row: sqlite3.Row) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_link"></a>
### `SQLiteBackend._link`

**메서드** · [정의 위치 L143](../../src/ccs/netops/sqlite_backend.py#L143)

```python
SQLiteBackend._link(row: sqlite3.Row) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_flow"></a>
### `SQLiteBackend._flow`

**메서드** · [정의 위치 L147](../../src/ccs/netops/sqlite_backend.py#L147)

```python
SQLiteBackend._flow(row: sqlite3.Row) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_get_topology"></a>
### `SQLiteBackend._get_topology`

**메서드** · [정의 위치 L150](../../src/ccs/netops/sqlite_backend.py#L150)

```python
SQLiteBackend._get_topology(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `NotFoundError`, `arguments.get`, `isinstance`, `self._arguments`, `self._db.execute`, `self._db.execute('SELECT 1 FROM nodes WHERE node_id=?', (target,)).fetchone`, `self._flow`, `self._interface`, `self._link`, `self._node`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_lookup_flows"></a>
### `SQLiteBackend._lookup_flows`

**메서드** · [정의 위치 L161](../../src/ccs/netops/sqlite_backend.py#L161)

```python
SQLiteBackend._lookup_flows(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `arguments.get`, `filters.items`, `iter`, `len`, `next`, `self._arguments`, `self._db.execute`, `self._flow`, `self._limit`, `self._state_version`, `self._text`, `set`, `value.upper`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_config_value"></a>
### `SQLiteBackend._config_value`

**메서드** · [정의 위치 L174](../../src/ccs/netops/sqlite_backend.py#L174)

```python
SQLiteBackend._config_value(self, target: str, param: str) -> Any
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`NotFoundError`, `_decode`, `self._db.execute`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_config_reference"></a>
### `SQLiteBackend._config_reference`

**메서드** · [정의 위치 L179](../../src/ccs/netops/sqlite_backend.py#L179)

```python
SQLiteBackend._config_reference(self, target: str, param: str) -> Any
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`NotFoundError`, `_decode`, `self._db.execute`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_normalize_change"></a>
### `SQLiteBackend._normalize_change`

**메서드** · [정의 위치 L184](../../src/ccs/netops/sqlite_backend.py#L184)

```python
SQLiteBackend._normalize_change(self, target: str, param: str, value: Any) -> tuple[str, Any, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `float`, `ipaddress.IPv4Address`, `isinstance`, `self._config_value`, `str`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_preview_change"></a>
### `SQLiteBackend._preview_change`

**메서드** · [정의 위치 L201](../../src/ccs/netops/sqlite_backend.py#L201)

```python
SQLiteBackend._preview_change(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_hash`, `_json`, `self._arguments`, `self._db.execute`, `self._db.execute('SELECT COALESCE(MAX(preview_id),0)+1 FROM previews').fetchone`, `self._normalize_change`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_idempotent_response"></a>
### `SQLiteBackend._idempotent_response`

**메서드** · [정의 위치 L210](../../src/ccs/netops/sqlite_backend.py#L210)

```python
SQLiteBackend._idempotent_response(self, key: str, operation: str, request: dict[str, Any]) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`IdempotencyConflictError`, `_decode`, `_hash`, `self._db.execute`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_store_idempotency"></a>
### `SQLiteBackend._store_idempotency`

**메서드** · [정의 위치 L216](../../src/ccs/netops/sqlite_backend.py#L216)

```python
SQLiteBackend._store_idempotency(self, key: str, operation: str, request: dict[str, Any], response: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_hash`, `_json`, `self._db.execute`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_sync_host_egress"></a>
### `SQLiteBackend._sync_host_egress`

**메서드** · [정의 위치 L219](../../src/ccs/netops/sqlite_backend.py#L219)

```python
SQLiteBackend._sync_host_egress(self, target: str, param: str, value: float) -> None
```

> Bind shared host TC configuration to both real dual-homed egress links.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `self._db.execute`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_write_config"></a>
### `SQLiteBackend._write_config`

**메서드** · [정의 위치 L230](../../src/ccs/netops/sqlite_backend.py#L230)

```python
SQLiteBackend._write_config(self, target: str, param: str, value: Any) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`NotFoundError`, `_json`, `float`, `int`, `self._db.execute`, `self._sync_host_egress`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_apply_change"></a>
### `SQLiteBackend._apply_change`

**메서드** · [정의 위치 L241](../../src/ccs/netops/sqlite_backend.py#L241)

```python
SQLiteBackend._apply_change(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ChangeConflictError`, `NotFoundError`, `VersionConflictError`, `_decode`, `self._arguments`, `self._config_value`, `self._db.execute`, `self._db.execute('SELECT * FROM previews WHERE token=?', (token,)).fetchone`, `self._db.execute('SELECT COALESCE(MAX(change_number),0)+1 FROM changes').fetchone`, `self._idempotent_response`, `self._meta_int`, `self._refresh_alarm_status`, `self._set_meta_int`, `self._state_version`, `self._store_idempotency`, `self._text`, `self._write_config`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_get_change_status"></a>
### `SQLiteBackend._get_change_status`

**메서드** · [정의 위치 L264](../../src/ccs/netops/sqlite_backend.py#L264)

```python
SQLiteBackend._get_change_status(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_decode`, `response.get`, `self._arguments`, `self._db.execute`, `self._text`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_rollback_change"></a>
### `SQLiteBackend._rollback_change`

**메서드** · [정의 위치 L270](../../src/ccs/netops/sqlite_backend.py#L270)

```python
SQLiteBackend._rollback_change(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ChangeConflictError`, `NotFoundError`, `VersionConflictError`, `_decode`, `self._arguments`, `self._config_value`, `self._db.execute`, `self._db.execute('SELECT * FROM changes WHERE change_id=?', (change_id,)).fetchone`, `self._idempotent_response`, `self._meta_int`, `self._refresh_alarm_status`, `self._set_meta_int`, `self._state_version`, `self._store_idempotency`, `self._text`, `self._write_config`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_metrics"></a>
### `SQLiteBackend._metrics`

**메서드** · [정의 위치 L291](../../src/ccs/netops/sqlite_backend.py#L291)

```python
SQLiteBackend._metrics(self, target: str) -> dict[str, float]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `NotFoundError`, `all`, `bool`, `float`, `max`, `min`, `round`, `self._config_reference`, `self._config_value`, `self._db.execute`, `self._db.execute("SELECT 1 FROM nodes WHERE node_id=? AND node_type='host'", (target,)).fetchone`, `self._db.execute('SELECT status FROM links WHERE path=?', (active_path,)).fetchall`, `self._db.execute('SELECT status FROM nodes WHERE node_id=?', (switch_id,)).fetchone`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_service_checks"></a>
### `SQLiteBackend._service_checks`

**메서드** · [정의 위치 L311](../../src/ccs/netops/sqlite_backend.py#L311)

```python
SQLiteBackend._service_checks(self, target: str) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `expected_tc.items`, `float`, `len`, `self._config_value`, `self._db.execute`, `self._db.execute('SELECT status FROM nodes WHERE node_id=?', (switch_id,)).fetchone`, `self._metrics`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_verify_service"></a>
### `SQLiteBackend._verify_service`

**메서드** · [정의 위치 L337](../../src/ccs/netops/sqlite_backend.py#L337)

```python
SQLiteBackend._verify_service(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `all`, `arguments.get`, `bool`, `isinstance`, `len`, `self._arguments`, `self._service_checks`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`, `set`, `sorted`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_get_kpi"></a>
### `SQLiteBackend._get_kpi`

**메서드** · [정의 위치 L347](../../src/ccs/netops/sqlite_backend.py#L347)

```python
SQLiteBackend._get_kpi(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `all`, `arguments.get`, `healthy[name]`, `isinstance`, `len`, `metrics.items`, `self._arguments`, `self._metrics`, `self._state_version`, `self._text`, `self._text(arguments['target'], 'target').upper`, `set`, `sorted`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_refresh_alarm_status"></a>
### `SQLiteBackend._refresh_alarm_status`

**메서드** · [정의 위치 L357](../../src/ccs/netops/sqlite_backend.py#L357)

```python
SQLiteBackend._refresh_alarm_status(self, changed_target: str) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `self._db.execute`, `self._db.execute("SELECT DISTINCT target FROM alarms WHERE status='active'").fetchall`, `self._meta_int`, `self._service_checks`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-_update_ticket"></a>
### `SQLiteBackend._update_ticket`

**메서드** · [정의 위치 L364](../../src/ccs/netops/sqlite_backend.py#L364)

```python
SQLiteBackend._update_ticket(self, arguments: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `NotFoundError`, `_hash`, `arguments.get`, `isinstance`, `len`, `self._arguments`, `self._db.execute`, `self._db.execute('SELECT 1 FROM tickets WHERE ticket_id=?', (ticket_id,)).fetchone`, `self._idempotent_response`, `self._meta_int`, `self._set_meta_int`, `self._store_idempotency`, `self._text`, `self._text(arguments['status'], 'status').lower`, `self._text(arguments['ticket_id'], 'ticket_id').upper`

</details>

<a id="fn-ccs-netops-sqlite_backend-SQLiteBackend-snapshot"></a>
### `SQLiteBackend.snapshot`

**메서드** · [정의 위치 L380](../../src/ccs/netops/sqlite_backend.py#L380)

```python
SQLiteBackend.snapshot(self) -> dict[str, Any]
```

> Return the canonical offline wired state; this is not a Network Tool.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_decode`, `_hash`, `configuration.append`, `self._db.execute`, `self._flow`, `self._interface`, `self._link`, `self._meta_int`, `self._node`, `self._state_version`

</details>

<a id="module-ccs-netops-tools"></a>
## `ccs.netops.tools`

[소스 파일](../../src/ccs/netops/tools.py) · [이 폴더 설명](../../src/ccs/netops/README.md)

> 소스의 모듈 설명: Provider-independent JSON schemas for the stable Network Tools surface.

<a id="fn-ccs-netops-tools-_object"></a>
### `_object`

**함수** · [정의 위치 L6](../../src/ccs/netops/tools.py#L6)

```python
_object(properties: dict, required: list[str] | None=None) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-netops-tools-tool_schemas"></a>
### `tool_schemas`

**함수** · [정의 위치 L32](../../src/ccs/netops/tools.py#L32)

```python
tool_schemas(role: str) -> list[dict]
```

> Return schemas visible to a role without backend-specific details.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `deepcopy`, `role.strip`, `role.strip().lower`

</details>

<a id="module-ccs-network_view"></a>
## `ccs.network_view`

[소스 파일](../../src/ccs/network_view.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Read-only, human-facing wired-network state for the web console.  The projection is deliberately separate from agent context collection. It opens episode databases read-only and returns only the wired topology, configuration, alarms, KPIs, and recorded changes needed by the operator UI.

<a id="class-ccs-network_view-_ReadOnlyBackend"></a>
### `_ReadOnlyBackend`

**클래스** · [정의 위치 L44](../../src/ccs/network_view.py#L44)

상속/계약: `SQLiteBackend`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Use ``SQLiteBackend`` reads over a transactionally pinned connection.

<a id="fn-ccs-network_view-_ReadOnlyBackend-__init__"></a>
### `_ReadOnlyBackend.__init__`

**메서드** · [정의 위치 L47](../../src/ccs/network_view.py#L47)

```python
_ReadOnlyBackend.__init__(self, path: Path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `FileNotFoundError`, `Path`, `Path(path).resolve`, `dict`, `metadata.get`, `self._connection.execute`, `self.close`, `self.path.as_uri`, `self.path.is_file`, `sqlite3.connect`, `threading.RLock`

</details>

<a id="fn-ccs-network_view-_selection"></a>
### `_selection`

**함수** · [정의 위치 L74](../../src/ccs/network_view.py#L74)

```python
_selection(fault: str, seed: int, difficulty: str, target: str) -> tuple[str, int, str, str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_TARGET.fullmatch`, `difficulty.strip`, `difficulty.strip().upper`, `fault.strip`, `fault.strip().upper`, `isinstance`, `target.strip`, `target.strip().upper`

</details>

<a id="fn-ccs-network_view-_safe_episode"></a>
### `_safe_episode`

**함수** · [정의 위치 L95](../../src/ccs/network_view.py#L95)

```python
_safe_episode(episode_id: str | None) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_EPISODE.fullmatch`, `isinstance`

</details>

<a id="fn-ccs-network_view-_read_json"></a>
### `_read_json`

**함수** · [정의 위치 L103](../../src/ccs/network_view.py#L103)

```python
_read_json(path: Path) -> Any
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.loads`, `path.read_text`

</details>

<a id="fn-ccs-network_view-_safe_run_id"></a>
### `_safe_run_id`

**함수** · [정의 위치 L107](../../src/ccs/network_view.py#L107)

```python
_safe_run_id(run_dir: Path, manifest: Any) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_RUN_ID.fullmatch`, `isinstance`, `manifest.get`

</details>

<a id="fn-ccs-network_view-_empty_run"></a>
### `_empty_run`

**함수** · [정의 위치 L114](../../src/ccs/network_view.py#L114)

```python
_empty_run(run_id: str | None, episode_id: str | None) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-network_view-_changes"></a>
### `_changes`

**함수** · [정의 위치 L133](../../src/ccs/network_view.py#L133)

```python
_changes(snapshot: dict[str, Any]) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `copy.deepcopy`, `isinstance`, `raw.get`, `result.append`, `snapshot.get`

</details>

<a id="fn-ccs-network_view-_configuration"></a>
### `_configuration`

**함수** · [정의 위치 L157](../../src/ccs/network_view.py#L157)

```python
_configuration(snapshot: dict[str, Any]) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`copy.deepcopy`, `isinstance`, `item.get`, `result.append`, `snapshot.get`

</details>

<a id="fn-ccs-network_view-_kpis"></a>
### `_kpis`

**함수** · [정의 위치 L184](../../src/ccs/network_view.py#L184)

```python
_kpis(raw: dict[str, Any]) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `raw.get`, `sample.get`

</details>

<a id="fn-ccs-network_view-_alarms"></a>
### `_alarms`

**함수** · [정의 위치 L200](../../src/ccs/network_view.py#L200)

```python
_alarms(raw: dict[str, Any]) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`alarm.get`, `isinstance`, `raw.get`, `result.append`

</details>

<a id="fn-ccs-network_view-_topology"></a>
### `_topology`

**함수** · [정의 위치 L217](../../src/ccs/network_view.py#L217)

```python
_topology(snapshot: dict[str, Any], kpis: list[dict[str, Any]], target: str) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `any`, `interface_to_node.get`, `interfaces.append`, `isinstance`, `item.get`, `links.append`, `nodes.append`, `raw.get`, `snapshot.get`

</details>

<a id="fn-ccs-network_view-_validated_snapshot"></a>
### `_validated_snapshot`

**함수** · [정의 위치 L286](../../src/ccs/network_view.py#L286)

```python
_validated_snapshot(live: dict[str, Any], final: dict[str, Any] | None) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ContractError`, `any`, `final.get`, `isinstance`, `live.get`

</details>

<a id="fn-ccs-network_view-_state_from_db"></a>
### `_state_from_db`

**함수** · [정의 위치 L296](../../src/ccs/network_view.py#L296)

```python
_state_from_db(db_path: Path, *, source: str, fault: str, seed: int, episode_id: str | None, run_id: str | None, target: str, final_snapshot: dict[str, Any] | None=None) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_ReadOnlyBackend`, `_alarms`, `_changes`, `_configuration`, `_kpis`, `_topology`, `_validated_snapshot`, `backend.call`, `backend.snapshot`

</details>

<a id="fn-ccs-network_view-_preview_paths"></a>
### `_preview_paths`

**함수** · [정의 위치 L329](../../src/ccs/network_view.py#L329)

```python
_preview_paths(workspace: Path, key: tuple[str, int, str, str]) -> tuple[Path, Path, Path]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(workspace).resolve`, `hashlib.sha256`, `hashlib.sha256(json.dumps(key, ensure_ascii=True, separators=(',', ':')).encode('ascii')).hexdigest`, `json.dumps`, `json.dumps(key, ensure_ascii=True, separators=(',', ':')).encode`

</details>

<a id="fn-ccs-network_view-preview_network"></a>
### `preview_network`

**함수** · [정의 위치 L337](../../src/ccs/network_view.py#L337)

```python
preview_network(workspace: Path, *, fault: str, seed: int, difficulty: str, target: str='HOST-001') -> dict[str, Any]
```

> Return a deterministic wired initial-state preview, cached by selection.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(workspace).resolve`, `RuntimeError`, `_PREVIEW_CACHE.get`, `_preview_paths`, `_read_json`, `_selection`, `_state_from_db`, `copy.deepcopy`, `create_world`, `db_path.parent.mkdir`, `isinstance`, `json.dumps`, `os.replace`, `pane.get`, `pane_path.is_file`, `pane_path.with_name`, `scenario.get`, `str`, `writing.write_text`

</details>

<a id="fn-ccs-network_view-read_network"></a>
### `read_network`

**함수** · [정의 위치 L400](../../src/ccs/network_view.py#L400)

```python
read_network(run_dir: Path, episode_id: str | None=None) -> dict[str, Any]
```

> Read the selected or latest wired episode without mutating artifacts.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(episodes_root / episode_id).resolve`, `(path / 'network.sqlite').is_file`, `(run_dir / 'episodes').resolve`, `(run_dir / 'manifest.json').is_file`, `Path`, `Path(run_dir).resolve`, `ValueError`, `_EPISODE.fullmatch`, `_empty_run`, `_read_json`, `_safe_episode`, `_safe_run_id`, `_selection`, `_state_from_db`, `db_path.is_file`, `episode_dir.is_relative_to`, `episodes_root.iterdir`, `final_path.is_file`, `isinstance`, `path.is_dir`, `scenario.get`, `scenario_path.is_file`, `sorted`

</details>

<a id="module-ccs-observability"></a>
## `ccs.observability`

[소스 파일](../../src/ccs/observability.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Append-only realtime activity stream for human operators.  The activity stream is deliberately separate from the disclosure audit log.  It contains only values that callers intentionally choose to display and never copies provider responses or provider reasoning objects.

<a id="fn-ccs-observability-_utc_now"></a>
### `_utc_now`

**함수** · [정의 위치 L37](../../src/ccs/observability.py#L37)

```python
_utc_now() -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`datetime.now`, `datetime.now(timezone.utc).isoformat`, `datetime.now(timezone.utc).isoformat().replace`

</details>

<a id="fn-ccs-observability-_safe_writer_id"></a>
### `_safe_writer_id`

**함수** · [정의 위치 L41](../../src/ccs/observability.py#L41)

```python
_safe_writer_id(writer_id: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_SAFE_WRITER.fullmatch`, `hashlib.sha256`, `hashlib.sha256(writer_id.encode('utf-8')).hexdigest`, `re.sub`, `re.sub('[^A-Za-z0-9_.-]+', '-', writer_id).strip`, `writer_id.encode`

</details>

<a id="fn-ccs-observability-_configured_secrets"></a>
### `_configured_secrets`

**함수** · [정의 위치 L51](../../src/ccs/observability.py#L51)

```python
_configured_secrets() -> tuple[str, ...]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`len`, `os.environ.get`, `sorted`, `tuple`

</details>

<a id="fn-ccs-observability-_scrub"></a>
### `_scrub`

**함수** · [정의 위치 L64](../../src/ccs/observability.py#L64)

```python
_scrub(value: Any, secrets: tuple[str, ...]) -> Any
```

> Return JSON-safe activity data with credentials removed.  This is a final safety net.  Callers remain responsible for passing only intentional operator-visible payloads rather than raw provider objects.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_BEARER_PATTERN.sub`, `_HIDDEN_PROVIDER_FIELD.search`, `_KEY_PATTERN.sub`, `_SECRET_FIELD.search`, `_scrub`, `cleaned.replace`, `isinstance`, `str`, `value.items`

</details>

<a id="class-ccs-observability-ActivityLog"></a>
### `ActivityLog`

**클래스** · [정의 위치 L96](../../src/ccs/observability.py#L96)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Write one flushed JSONL shard owned by a single process/writer.

<a id="fn-ccs-observability-ActivityLog-__init__"></a>
### `ActivityLog.__init__`

**메서드** · [정의 위치 L99](../../src/ccs/observability.py#L99)

```python
ActivityLog.__init__(self, run_dir: Path, writer_id: str, episode_id: str='', mode: str | None=None, *, secrets: Iterable[str] | None=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `_configured_secrets`, `_safe_writer_id`, `activity_dir.mkdir`, `control_path_for_run`, `isinstance`, `len`, `self._resume_sequence`, `set`, `sorted`, `str`, `threading.Lock`, `tuple`

</details>

<a id="fn-ccs-observability-ActivityLog-_resume_sequence"></a>
### `ActivityLog._resume_sequence`

**메서드** · [정의 위치 L124](../../src/ccs/observability.py#L124)

```python
ActivityLog._resume_sequence(self) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `enumerate`, `event.get`, `int`, `json.loads`, `line.strip`, `max`, `self.shard_path.exists`, `self.shard_path.open`

</details>

<a id="fn-ccs-observability-ActivityLog-emit"></a>
### `ActivityLog.emit`

**메서드** · [정의 위치 L143](../../src/ccs/observability.py#L143)

```python
ActivityLog.emit(self, component: str, action: str, status: str, summary: str, *, details: Any=None, operation_id: str | None=None, trace_id: str | None=None, delay_after: bool=True, **extra: Any) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_scrub`, `_utc_now`, `event.update`, `handle.fileno`, `handle.flush`, `handle.write`, `json.dumps`, `os.fsync`, `self.shard_path.open`, `str`, `uuid.uuid4`, `wait_after_event`

</details>

<a id="fn-ccs-observability-activity_for_episode"></a>
### `activity_for_episode`

**함수** · [정의 위치 L197](../../src/ccs/observability.py#L197)

```python
activity_for_episode(path: Path, role: str, mode: str | None=None, *, secrets: Iterable[str] | None=None) -> ActivityLog
```

> Create a collision-free activity writer from a run or episode path.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ActivityLog`, `Path`

</details>

<a id="module-ccs-pacing"></a>
## `ccs.pacing`

[소스 파일](../../src/ccs/pacing.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Mutable, cross-process pacing control and run-local delay accounting.

<a id="fn-ccs-pacing-_utc_now"></a>
### `_utc_now`

**함수** · [정의 위치 L29](../../src/ccs/pacing.py#L29)

```python
_utc_now() -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`datetime.now`, `datetime.now(timezone.utc).isoformat`, `datetime.now(timezone.utc).isoformat().replace`

</details>

<a id="fn-ccs-pacing-validate_delay"></a>
### `validate_delay`

**함수** · [정의 위치 L33](../../src/ccs/pacing.py#L33)

```python
validate_delay(seconds: Any) -> float
```

> Return a finite delay in the supported inclusive range 0..30 seconds.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `ValueError`, `float`, `isinstance`, `math.isfinite`

</details>

<a id="fn-ccs-pacing-_atomic_json"></a>
### `_atomic_json`

**함수** · [정의 위치 L44](../../src/ccs/pacing.py#L44)

```python
_atomic_json(path: Path, value: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`handle.fileno`, `handle.flush`, `handle.write`, `json.dump`, `os.fsync`, `os.getpid`, `os.replace`, `path.parent.mkdir`, `path.with_name`, `threading.get_ident`, `uuid.uuid4`, `writing.exists`, `writing.open`, `writing.unlink`

</details>

<a id="fn-ccs-pacing-read_control"></a>
### `read_control`

**함수** · [정의 위치 L61](../../src/ccs/pacing.py#L61)

```python
read_control(path: Path) -> dict[str, Any]
```

> Read and validate one atomic pacing control document.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(path).resolve`, `ValueError`, `control_path.read_text`, `isinstance`, `json.loads`, `str`, `type`, `validate_delay`, `value.get`

</details>

<a id="fn-ccs-pacing-write_control"></a>
### `write_control`

**함수** · [정의 위치 L75](../../src/ccs/pacing.py#L75)

```python
write_control(path: Path, seconds: Any) -> dict[str, Any]
```

> Atomically set a shared delay and append a collision-free change record.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(path).resolve`, `_atomic_json`, `_utc_now`, `handle.fileno`, `handle.flush`, `handle.write`, `history_dir.mkdir`, `history_path.open`, `int`, `json.dump`, `os.fsync`, `os.getpid`, `read_control`, `str`, `threading.get_ident`, `time.time_ns`, `uuid.uuid4`, `validate_delay`

</details>

<a id="fn-ccs-pacing-install_run_pointer"></a>
### `install_run_pointer`

**함수** · [정의 위치 L109](../../src/ccs/pacing.py#L109)

```python
install_run_pointer(run_dir: Path, control_path: Path) -> dict[str, Any]
```

> Install the immutable run-local pointer before the first activity event.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FileExistsError`, `Path`, `Path(run_dir).resolve`, `_atomic_json`, `_utc_now`, `pointer_path.exists`, `read_control`, `time.time_ns`

</details>

<a id="fn-ccs-pacing-control_path_for_run"></a>
### `control_path_for_run`

**함수** · [정의 위치 L129](../../src/ccs/pacing.py#L129)

```python
control_path_for_run(run_dir: Path) -> Path | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `ValueError`, `isinstance`, `json.loads`, `pointer.get`, `pointer_path.is_file`, `pointer_path.read_text`

</details>

<a id="fn-ccs-pacing-_safe_shard"></a>
### `_safe_shard`

**함수** · [정의 위치 L139](../../src/ccs/pacing.py#L139)

```python
_safe_shard(writer_id: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_SAFE_NAME.sub`, `_SAFE_NAME.sub('-', writer_id).strip`, `hashlib.sha256`, `hashlib.sha256(writer_id.encode('utf-8')).hexdigest`, `writer_id.encode`

</details>

<a id="fn-ccs-pacing-_append_timing"></a>
### `_append_timing`

**함수** · [정의 위치 L145](../../src/ccs/pacing.py#L145)

```python
_append_timing(run_dir: Path, writer_id: str, record: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `_safe_shard`, `directory.mkdir`, `handle.fileno`, `handle.flush`, `handle.write`, `json.dumps`, `os.fsync`, `path.open`

</details>

<a id="fn-ccs-pacing-wait_after_event"></a>
### `wait_after_event`

**함수** · [정의 위치 L157](../../src/ccs/pacing.py#L157)

```python
wait_after_event(run_dir: Path, writer_id: str, event_id: str, control_path: Path | None=None) -> float
```

> Wait after a persisted event while observing shared delay changes.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `_append_timing`, `control_path_for_run`, `min`, `observations.append`, `read_control`, `time.monotonic`, `time.sleep`, `time.time_ns`

</details>

<a id="fn-ccs-pacing-_history"></a>
### `_history`

**함수** · [정의 위치 L216](../../src/ccs/pacing.py#L216)

```python
_history(control_path: Path, started_ns: int, finished_ns: int) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`changes.append`, `directory.glob`, `directory.is_dir`, `int`, `json.loads`, `path.read_text`, `sorted`, `validate_delay`

</details>

<a id="fn-ccs-pacing-summarize_timing"></a>
### `summarize_timing`

**함수** · [정의 위치 L236](../../src/ccs/pacing.py#L236)

```python
summarize_timing(run_dir: Path, *, started_unix_ns: int, finished_unix_ns: int) -> dict[str, Any]
```

> Summarize elapsed time and both union and worker-summed intentional delay.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_path / POINTER_NAME).read_text`, `Path`, `_history`, `int`, `intervals.append`, `intervals.sort`, `json.loads`, `line.strip`, `max`, `merged.append`, `pacing_dir.glob`, `pacing_dir.is_dir`, `path.read_text`, `path.read_text(encoding='utf-8').splitlines`, `read_control`, `sum`, `validate_delay`

</details>

<a id="fn-ccs-pacing-timeout_allowance_seconds"></a>
### `timeout_allowance_seconds`

**함수** · [정의 위치 L288](../../src/ccs/pacing.py#L288)

```python
timeout_allowance_seconds(system: Any) -> float
```

> Bound protocol headroom using configured finite workflow/step limits.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`int`

</details>

<a id="module-ccs-paths"></a>
## `ccs.paths`

[소스 파일](../../src/ccs/paths.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Portable defaults for mutable runtime data; environment overrides are explicit.

<a id="fn-ccs-paths-working_root"></a>
### `working_root`

**함수** · [정의 위치 L8](../../src/ccs/paths.py#L8)

```python
working_root() -> Path
```

> Return subprocess scratch root without creating directories.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(configured).expanduser`, `Path(configured).expanduser().resolve`, `os.environ.get`

</details>

<a id="fn-ccs-paths-web_workspace"></a>
### `web_workspace`

**함수** · [정의 위치 L14](../../src/ccs/paths.py#L14)

```python
web_workspace() -> Path
```

> Return the web library/index root; explicit CLI --workspace takes priority.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(configured).expanduser`, `Path(configured).expanduser().resolve`, `os.environ.get`, `working_root`

</details>

<a id="module-ccs-processes"></a>
## `ccs.processes`

[소스 파일](../../src/ccs/processes.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Bounded local service startup and reliable cleanup on Windows and POSIX.

<a id="fn-ccs-processes-choose_port"></a>
### `choose_port`

**함수** · [정의 위치 L12](../../src/ccs/processes.py#L12)

```python
choose_port(host, configured)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`sock.bind`, `sock.getsockname`, `socket.socket`

</details>

<a id="class-ccs-processes-Services"></a>
### `Services`

**클래스** · [정의 위치 L17](../../src/ccs/processes.py#L17)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-processes-Services-__init__"></a>
### `Services.__init__`

**메서드** · [정의 위치 L18](../../src/ccs/processes.py#L18)

```python
Services.__init__(self, system, run_dir, episode_dir, contexts, tokens)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-processes-Services-__aenter__"></a>
### `Services.__aenter__`

**비동기 메서드** · [정의 위치 L22](../../src/ccs/processes.py#L22)

```python
async Services.__aenter__(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(self.episode_dir / f'{kind}-process.log').open`, `RuntimeError`, `asyncio.sleep`, `child.poll`, `config_path.write_text`, `env.update`, `json.dumps`, `os.environ.copy`, `self.__aexit__`, `self.children.append`, `self.contexts.items`, `self.files.append`, `socket.create_connection`, `str`, `subprocess.Popen`, `time.monotonic`, `working_dir.mkdir`, `working_dir.resolve`, `working_root`

</details>

<a id="fn-ccs-processes-Services-__aexit__"></a>
### `Services.__aexit__`

**비동기 메서드** · [정의 위치 L51](../../src/ccs/processes.py#L51)

```python
async Services.__aexit__(self, *_)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.to_thread`, `child.kill`, `child.poll`, `child.terminate`, `handle.close`, `reversed`

</details>

<a id="module-ccs-progress"></a>
## `ccs.progress`

[소스 파일](../../src/ccs/progress.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Console projection of persisted activity, shared across the three processes.

<a id="class-ccs-progress-ConsoleProgress"></a>
### `ConsoleProgress`

**클래스** · [정의 위치 L7](../../src/ccs/progress.py#L7)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-progress-ConsoleProgress-__init__"></a>
### `ConsoleProgress.__init__`

**메서드** · [정의 위치 L8](../../src/ccs/progress.py#L8)

```python
ConsoleProgress.__init__(self, run_dir: Path, *, detailed=False)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `set`, `threading.Event`, `threading.Thread`

</details>

<a id="fn-ccs-progress-ConsoleProgress-start"></a>
### `ConsoleProgress.start`

**메서드** · [정의 위치 L15](../../src/ccs/progress.py#L15)

```python
ConsoleProgress.start(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._thread.start`

</details>

<a id="fn-ccs-progress-ConsoleProgress-_drain"></a>
### `ConsoleProgress._drain`

**메서드** · [정의 위치 L19](../../src/ccs/progress.py#L19)

```python
ConsoleProgress._drain(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`''.join`, `c.isprintable`, `event.get`, `json.dumps`, `print`, `read_activity`, `self._seen.add`

</details>

<a id="fn-ccs-progress-ConsoleProgress-_follow"></a>
### `ConsoleProgress._follow`

**메서드** · [정의 위치 L35](../../src/ccs/progress.py#L35)

```python
ConsoleProgress._follow(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._drain`, `self._stop.is_set`, `self._stop.wait`

</details>

<a id="fn-ccs-progress-ConsoleProgress-stop"></a>
### `ConsoleProgress.stop`

**메서드** · [정의 위치 L43](../../src/ccs/progress.py#L43)

```python
ConsoleProgress.stop(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._drain`, `self._stop.set`, `self._thread.join`

</details>

<a id="module-ccs-protocols-__init__"></a>
## `ccs.protocols.__init__`

[소스 파일](../../src/ccs/protocols/__init__.py) · [이 폴더 설명](../../src/ccs/protocols/README.md)

> 소스의 모듈 설명: Public wire-protocol adapters.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-protocols-_auth"></a>
## `ccs.protocols._auth`

[소스 파일](../../src/ccs/protocols/_auth.py) · [이 폴더 설명](../../src/ccs/protocols/README.md)

> 소스의 모듈 설명: Small ASGI bearer-token middleware shared by the local protocols.

<a id="class-ccs-protocols-_auth-BearerTokenMiddleware"></a>
### `BearerTokenMiddleware`

**클래스** · [정의 위치 L13](../../src/ccs/protocols/_auth.py#L13)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Reject unknown bearer tokens before requests enter a protocol SDK.

<a id="fn-ccs-protocols-_auth-BearerTokenMiddleware-__init__"></a>
### `BearerTokenMiddleware.__init__`

**메서드** · [정의 위치 L16](../../src/ccs/protocols/_auth.py#L16)

```python
BearerTokenMiddleware.__init__(self, app: ASGIApp, *, tokens: Mapping[str, str], public_paths: Sequence[str]=()) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`dict`, `frozenset`

</details>

<a id="fn-ccs-protocols-_auth-BearerTokenMiddleware-__call__"></a>
### `BearerTokenMiddleware.__call__`

**비동기 메서드** · [정의 위치 L27](../../src/ccs/protocols/_auth.py#L27)

```python
async BearerTokenMiddleware.__call__(self, scope: Scope, receive: Receive, send: Send) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Headers`, `Headers(scope=scope).get`, `JSONResponse`, `_bearer_value`, `_match_token`, `response`, `scope.get`, `scope.setdefault`, `self.app`

</details>

<a id="fn-ccs-protocols-_auth-role_from_headers"></a>
### `role_from_headers`

**함수** · [정의 위치 L47](../../src/ccs/protocols/_auth.py#L47)

```python
role_from_headers(headers: Mapping[str, str] | None, tokens: Mapping[str, str]) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_bearer_value`, `_match_token`, `headers.get`

</details>

<a id="fn-ccs-protocols-_auth-_bearer_value"></a>
### `_bearer_value`

**함수** · [정의 위치 L52](../../src/ccs/protocols/_auth.py#L52)

```python
_bearer_value(authorization: str | None) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`authorization.partition`, `scheme.lower`

</details>

<a id="fn-ccs-protocols-_auth-_match_token"></a>
### `_match_token`

**함수** · [정의 위치 L61](../../src/ccs/protocols/_auth.py#L61)

```python
_match_token(supplied: str | None, tokens: Mapping[str, str]) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`hmac.compare_digest`, `tokens.items`

</details>

<a id="module-ccs-protocols-a2a"></a>
## `ccs.protocols.a2a`

[소스 파일](../../src/ccs/protocols/a2a.py) · [이 폴더 설명](../../src/ccs/protocols/README.md)

> 소스의 모듈 설명: A2A SDK 1.1.5 JSON-RPC boundary for the Diagnosis Agent.

<a id="fn-ccs-protocols-a2a-build_a2a_app"></a>
### `build_a2a_app`

**함수** · [정의 위치 L47](../../src/ccs/protocols/a2a.py#L47)

```python
build_a2a_app(url: str, token: str, handler: A2AHandler, *, rpc_path: str='/a2a', timeout_seconds: float=30.0) -> Starlette
```

> Build the authenticated A2A JSON-RPC application and AgentCard.  ``url`` is the public origin/base (for example ``http://127.0.0.1:8102``). The card is public at the standard well-known path and advertises ``url + rpc_path``. All task operations require the bearer token.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`AgentCapabilities`, `AgentCard`, `AgentInterface`, `AgentSkill`, `DefaultRequestHandler`, `HTTPAuthSecurityScheme`, `InMemoryTaskStore`, `Middleware`, `SecurityRequirement`, `SecurityScheme`, `Starlette`, `StringList`, `ValueError`, `_DiagnosisExecutor`, `create_agent_card_routes`, `create_jsonrpc_routes`, `rpc_path.startswith`, `url.rstrip`

</details>

<a id="class-ccs-protocols-a2a-A2AClient"></a>
### `A2AClient`

**클래스** · [정의 위치 L129](../../src/ccs/protocols/a2a.py#L129)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Diagnosis-specific facade over the A2A 1.1.5 client.

<a id="fn-ccs-protocols-a2a-A2AClient-__init__"></a>
### `A2AClient.__init__`

**메서드** · [정의 위치 L132](../../src/ccs/protocols/a2a.py#L132)

```python
A2AClient.__init__(self, url: str, token: str, *, timeout_seconds: float=30.0, http_client: httpx.AsyncClient | None=None) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `url.rstrip`

</details>

<a id="fn-ccs-protocols-a2a-A2AClient-diagnose"></a>
### `A2AClient.diagnose`

**비동기 메서드** · [정의 위치 L147](../../src/ccs/protocols/a2a.py#L147)

```python
async A2AClient.diagnose(self, payload: dict[str, Any], *, metadata: dict[str, Any] | None=None) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2ATaskError`, `ClientCallContext`, `ClientConfig`, `ClientFactory`, `DiagnosisRequest.model_validate`, `DiagnosisRequest.model_validate(payload).model_dump`, `DiagnosisResult.model_validate`, `DiagnosisResult.model_validate(result).model_dump`, `Message`, `ProtocolCallError`, `ProtocolTransportError`, `SendMessageConfiguration`, `SendMessageRequest`, `TaskState.Name`, `_diagnosis_artifact`, `asyncio.timeout`, `client.send_message`, `dict`, `factory.create_from_url`, `http_client.aclose`, `httpx.AsyncClient`, `new_data_part`, `response.HasField`, `type`, `wire_metadata.setdefault`

</details>

<a id="class-ccs-protocols-a2a-_DiagnosisExecutor"></a>
### `_DiagnosisExecutor`

**클래스** · [정의 위치 L218](../../src/ccs/protocols/a2a.py#L218)

상속/계약: `AgentExecutor`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-protocols-a2a-_DiagnosisExecutor-__init__"></a>
### `_DiagnosisExecutor.__init__`

**메서드** · [정의 위치 L219](../../src/ccs/protocols/a2a.py#L219)

```python
_DiagnosisExecutor.__init__(self, handler: A2AHandler, *, timeout_seconds: float) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.Lock`

</details>

<a id="fn-ccs-protocols-a2a-_DiagnosisExecutor-execute"></a>
### `_DiagnosisExecutor.execute`

**비동기 메서드** · [정의 위치 L225](../../src/ccs/protocols/a2a.py#L225)

```python
async _DiagnosisExecutor.execute(self, context: RequestContext, event_queue: EventQueue) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`DiagnosisRequest.model_validate`, `DiagnosisResult.model_validate`, `DiagnosisResult.model_validate(result).model_dump`, `TaskUpdater`, `ValueError`, `event_queue.enqueue_event`, `get_data_parts`, `isinstance`, `json_format.MessageToDict`, `len`, `new_data_part`, `new_task_from_user_message`, `new_text_part`, `request_model.model_dump`, `self._idempotent_call`, `type`, `updater.add_artifact`, `updater.complete`, `updater.failed`, `updater.new_agent_message`, `updater.start_work`

</details>

<a id="fn-ccs-protocols-a2a-_DiagnosisExecutor-cancel"></a>
### `_DiagnosisExecutor.cancel`

**비동기 메서드** · [정의 위치 L275](../../src/ccs/protocols/a2a.py#L275)

```python
async _DiagnosisExecutor.cancel(self, context: RequestContext, event_queue: EventQueue) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TaskUpdater`, `updater.cancel`

</details>

<a id="fn-ccs-protocols-a2a-_DiagnosisExecutor-_idempotent_call"></a>
### `_DiagnosisExecutor._idempotent_call`

**비동기 메서드** · [정의 위치 L280](../../src/ccs/protocols/a2a.py#L280)

```python
async _DiagnosisExecutor._idempotent_call(self, idempotency_key: str, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `asyncio.create_task`, `asyncio.shield`, `hashlib.sha256`, `json.dumps`, `json.dumps(payload, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode`, `self._calls.get`, `self._invoke`

</details>

<a id="fn-ccs-protocols-a2a-_DiagnosisExecutor-_invoke"></a>
### `_DiagnosisExecutor._invoke`

**비동기 메서드** · [정의 위치 L300](../../src/ccs/protocols/a2a.py#L300)

```python
async _DiagnosisExecutor._invoke(self, payload: dict[str, Any], metadata: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `asyncio.timeout`, `isinstance`, `self._handler`

</details>

<a id="fn-ccs-protocols-a2a-_diagnosis_artifact"></a>
### `_diagnosis_artifact`

**함수** · [정의 위치 L308](../../src/ccs/protocols/a2a.py#L308)

```python
_diagnosis_artifact(task: Task) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ProtocolCallError`, `get_data_parts`, `isinstance`, `reversed`

</details>

<a id="module-ccs-protocols-errors"></a>
## `ccs.protocols.errors`

[소스 파일](../../src/ccs/protocols/errors.py) · [이 폴더 설명](../../src/ccs/protocols/README.md)

> 소스의 모듈 설명: Stable exceptions exposed by the protocol adapters.

<a id="class-ccs-protocols-errors-ProtocolError"></a>
### `ProtocolError`

**클래스** · [정의 위치 L4](../../src/ccs/protocols/errors.py#L4)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Base class for wire-protocol failures.

<a id="class-ccs-protocols-errors-ProtocolAuthenticationError"></a>
### `ProtocolAuthenticationError`

**클래스** · [정의 위치 L8](../../src/ccs/protocols/errors.py#L8)

상속/계약: `ProtocolError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> The remote endpoint rejected the configured bearer token.

<a id="class-ccs-protocols-errors-ProtocolCallError"></a>
### `ProtocolCallError`

**클래스** · [정의 위치 L12](../../src/ccs/protocols/errors.py#L12)

상속/계약: `ProtocolError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A remote MCP tool returned an explicit tool error.

<a id="class-ccs-protocols-errors-ProtocolTransportError"></a>
### `ProtocolTransportError`

**클래스** · [정의 위치 L16](../../src/ccs/protocols/errors.py#L16)

상속/계약: `ProtocolError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> The protocol exchange could not complete.

<a id="class-ccs-protocols-errors-A2ATaskError"></a>
### `A2ATaskError`

**클래스** · [정의 위치 L20](../../src/ccs/protocols/errors.py#L20)

상속/계약: `ProtocolError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> An A2A task reached a non-success terminal state.

<a id="module-ccs-protocols-mcp"></a>
## `ccs.protocols.mcp`

[소스 파일](../../src/ccs/protocols/mcp.py) · [이 폴더 설명](../../src/ccs/protocols/README.md)

> 소스의 모듈 설명: MCP 2.2.0 Streamable HTTP boundary for backend-neutral NetOps tools.

<a id="fn-ccs-protocols-mcp-build_mcp_app"></a>
### `build_mcp_app`

**함수** · [정의 위치 L26](../../src/ccs/protocols/mcp.py#L26)

```python
build_mcp_app(schemas_by_role: Mapping[str, Sequence[dict[str, Any]]], tokens: Mapping[str, str], handler: MCPHandler, *, path: str='/mcp') -> Starlette
```

> Build an authenticated MCP 2.2.0 Streamable HTTP application.  ``tokens`` maps the roles ``operation`` and ``diagnosis`` to bearer tokens. Tool definitions are role-specific, and the same role check is repeated at call time so a hidden change tool cannot be invoked by name.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Middleware`, `Server`, `_compile_schemas`, `_validate_tokens`, `app.user_middleware.insert`, `server.streamable_http_app`

</details>

<a id="fn-ccs-protocols-mcp-build_mcp_app-list_tools"></a>
### `build_mcp_app.list_tools`

**비동기 함수 (중첩 handler)** · [정의 위치 L43](../../src/ccs/protocols/mcp.py#L43)

```python
async build_mcp_app.list_tools(ctx: ServerRequestContext[Any, Any], _params: types.PaginatedRequestParams | None) -> types.ListToolsResult
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_require_role`, `tools_by_role.get`, `types.ListToolsResult`

</details>

<a id="fn-ccs-protocols-mcp-build_mcp_app-call_tool"></a>
### `build_mcp_app.call_tool`

**비동기 함수 (중첩 handler)** · [정의 위치 L50](../../src/ccs/protocols/mcp.py#L50)

```python
async build_mcp_app.call_tool(ctx: ServerRequestContext[Any, Any], params: types.CallToolRequestParams) -> types.CallToolResult
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'.'.join`, `TypeError`, `_require_role`, `_tool_error`, `dict`, `handler`, `isinstance`, `json.dumps`, `str`, `type`, `types.CallToolResult`, `types.TextContent`, `validator.validate`, `validators_by_role.get`, `validators_by_role.get(role, {}).get`

</details>

<a id="class-ccs-protocols-mcp-MCPClient"></a>
### `MCPClient`

**클래스** · [정의 위치 L104](../../src/ccs/protocols/mcp.py#L104)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Small one-request-at-a-time MCP client used by both agents.

<a id="fn-ccs-protocols-mcp-MCPClient-__init__"></a>
### `MCPClient.__init__`

**메서드** · [정의 위치 L107](../../src/ccs/protocols/mcp.py#L107)

```python
MCPClient.__init__(self, url: str, token: str, *, timeout_seconds: float=15.0, http_client: httpx2.AsyncClient | None=None) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`

</details>

<a id="fn-ccs-protocols-mcp-MCPClient-list_tools"></a>
### `MCPClient.list_tools`

**비동기 메서드** · [정의 위치 L122](../../src/ccs/protocols/mcp.py#L122)

```python
async MCPClient.list_tools(self) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._exchange`

</details>

<a id="fn-ccs-protocols-mcp-MCPClient-list_tools-operation"></a>
### `MCPClient.list_tools.operation`

**비동기 함수 (중첩 handler)** · [정의 위치 L123](../../src/ccs/protocols/mcp.py#L123)

```python
async MCPClient.list_tools.operation(session: ClientSession) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`session.list_tools`

</details>

<a id="fn-ccs-protocols-mcp-MCPClient-call"></a>
### `MCPClient.call`

**비동기 메서드** · [정의 위치 L136](../../src/ccs/protocols/mcp.py#L136)

```python
async MCPClient.call(self, tool: str, arguments: dict[str, Any] | None=None, *, metadata: dict[str, Any] | None=None) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._exchange`

</details>

<a id="fn-ccs-protocols-mcp-MCPClient-call-operation"></a>
### `MCPClient.call.operation`

**비동기 함수 (중첩 handler)** · [정의 위치 L143](../../src/ccs/protocols/mcp.py#L143)

```python
async MCPClient.call.operation(session: ClientSession) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ProtocolCallError`, `_first_text`, `isinstance`, `json.loads`, `session.call_tool`

</details>

<a id="fn-ccs-protocols-mcp-MCPClient-_exchange"></a>
### `MCPClient._exchange`

**비동기 메서드** · [정의 위치 L168](../../src/ccs/protocols/mcp.py#L168)

```python
async MCPClient._exchange(self, operation: Callable[[ClientSession], Awaitable[Any]]) -> Any
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ClientSession`, `ProtocolTransportError`, `asyncio.timeout`, `client.aclose`, `httpx2.AsyncClient`, `operation`, `session.initialize`, `streamable_http_client`, `type`

</details>

<a id="fn-ccs-protocols-mcp-_validate_tokens"></a>
### `_validate_tokens`

**함수** · [정의 위치 L204](../../src/ccs/protocols/mcp.py#L204)

```python
_validate_tokens(tokens: Mapping[str, str]) -> dict[str, str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `any`, `dict`, `len`, `set`, `token_map.values`

</details>

<a id="fn-ccs-protocols-mcp-_compile_schemas"></a>
### `_compile_schemas`

**함수** · [정의 위치 L213](../../src/ccs/protocols/mcp.py#L213)

```python
_compile_schemas(schemas_by_role: Mapping[str, Sequence[dict[str, Any]]]) -> tuple[dict[str, list[types.Tool]], dict[str, dict[str, Draft202012Validator]]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Draft202012Validator`, `Draft202012Validator.check_schema`, `ValueError`, `isinstance`, `schema.get`, `schemas_by_role.get`, `str`, `tools.append`, `types.Tool`

</details>

<a id="fn-ccs-protocols-mcp-_require_role"></a>
### `_require_role`

**함수** · [정의 위치 L245](../../src/ccs/protocols/mcp.py#L245)

```python
_require_role(ctx: ServerRequestContext[Any, Any], tokens: Mapping[str, str]) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`PermissionError`, `getattr`, `role_from_headers`

</details>

<a id="fn-ccs-protocols-mcp-_tool_error"></a>
### `_tool_error`

**함수** · [정의 위치 L254](../../src/ccs/protocols/mcp.py#L254)

```python
_tool_error(code: str, message: str) -> types.CallToolResult
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`, `types.CallToolResult`, `types.TextContent`

</details>

<a id="fn-ccs-protocols-mcp-_first_text"></a>
### `_first_text`

**함수** · [정의 위치 L263](../../src/ccs/protocols/mcp.py#L263)

```python
_first_text(result: types.CallToolResult) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`

</details>

<a id="module-ccs-reporting"></a>
## `ccs.reporting`

[소스 파일](../../src/ccs/reporting.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Aggregate reports exclude raw incident payloads and registry identifiers.

<a id="fn-ccs-reporting-write_reports"></a>
### `write_reports`

**함수** · [정의 위치 L7](../../src/ccs/reporting.py#L7)

```python
write_reports(run_dir, summary, manifest)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`''.join`, `'\n'.join`, `(Path(run_dir) / 'report.html').write_text`, `(Path(run_dir) / 'report.md').write_text`, `Path`, `escape`, `str`

</details>

<a id="fn-ccs-reporting-verify_seal"></a>
### `verify_seal`

**함수** · [정의 위치 L25](../../src/ccs/reporting.py#L25)

```python
verify_seal(run_dir: Path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').read_text`, `(run_dir / relative).resolve`, `errors.append`, `errors.extend`, `hashes.items`, `hashlib.sha256`, `hashlib.sha256(path.read_bytes()).hexdigest`, `integrity.get`, `json.loads`, `manifest.get`, `path.is_file`, `path.is_relative_to`, `path.read_bytes`, `run_dir.resolve`, `validate_events`

</details>

<a id="fn-ccs-reporting-compare_runs"></a>
### `compare_runs`

**함수** · [정의 위치 L39](../../src/ccs/reporting.py#L39)

```python
compare_runs(paths)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(path / 'manifest.json').read_text`, `(path / 'summary.json').read_text`, `Path`, `ValueError`, `comparison_identity`, `json.loads`, `results.append`, `verify_seal`

</details>

<a id="fn-ccs-reporting-comparison_identity"></a>
### `comparison_identity`

**함수** · [정의 위치 L52](../../src/ccs/reporting.py#L52)

```python
comparison_identity(run_dir, manifest)
```

> Compare executed scenarios and non-model conditions, not just fault labels.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(Path(run_dir) / 'effective-config.json').read_text`, `Path`, `ValueError`, `ai['agent_profiles'].get`, `config.get`, `config['system'].items`, `json.loads`, `manifest.get`, `manifest.get('artifact_hashes', {}).get`, `pacing_identity`, `scenarios.append`

</details>

<a id="fn-ccs-reporting-pacing_identity"></a>
### `pacing_identity`

**함수** · [정의 위치 L74](../../src/ccs/reporting.py#L74)

```python
pacing_identity(timing)
```

> Compare selected delay levels without treating clock timestamps as inputs.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `levels.append`, `timing.get`

</details>

<a id="module-ccs-run_analysis"></a>
## `ccs.run_analysis`

[소스 파일](../../src/ccs/run_analysis.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Read-only, evidence-bounded analysis of completed CCS run artifacts.  The analysis intentionally has a narrower read boundary than reporting.  It projects selected fields from the manifest, summary, episode result and oracle, uses the monitor's redacted activity stream for observed tool calls, and asks ``network_view`` for the final operational state.  It never re-creates a scenario or reads model transcripts, restricted scenarios, configuration XML, or the oracle's ground-truth details.

<a id="fn-ccs-run_analysis-_bilingual"></a>
### `_bilingual`

**함수** · [정의 위치 L100](../../src/ccs/run_analysis.py#L100)

```python
_bilingual(ko: str, en: str) -> dict[str, str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-run_analysis-_scenario_projection"></a>
### `_scenario_projection`

**함수** · [정의 위치 L104](../../src/ccs/run_analysis.py#L104)

```python
_scenario_projection(fault: str | None) -> dict[str, dict[str, str]] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SCENARIOS.get`, `_bilingual`, `_text`, `isinstance`, `source.get`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_finite_number"></a>
### `_finite_number`

**함수** · [정의 위치 L119](../../src/ccs/run_analysis.py#L119)

```python
_finite_number(value: Any) -> int | float | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`float`, `isinstance`, `math.isfinite`

</details>

<a id="fn-ccs-run_analysis-_text"></a>
### `_text`

**함수** · [정의 위치 L125](../../src/ccs/run_analysis.py#L125)

```python
_text(value: Any, limit: int=2000) -> str | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `len`, `value.replace`, `value.replace('\x00', '').strip`

</details>

<a id="fn-ccs-run_analysis-_blocked_key"></a>
### `_blocked_key`

**함수** · [정의 위치 L134](../../src/ccs/run_analysis.py#L134)

```python
_blocked_key(key: Any) -> bool
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`any`, `lowered.endswith`, `str`, `str(key).casefold`

</details>

<a id="fn-ccs-run_analysis-_compact_json"></a>
### `_compact_json`

**함수** · [정의 위치 L146](../../src/ccs/run_analysis.py#L146)

```python
_compact_json(value: Any, *, depth: int=0) -> Any
```

> Bound untrusted provider text and suppress secret/truth-bearing keys.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_blocked_key`, `_compact_json`, `_finite_number`, `isinstance`, `len`, `list`, `result.append`, `str`, `value.items`

</details>

<a id="fn-ccs-run_analysis-_safe_json_object"></a>
### `_safe_json_object`

**함수** · [정의 위치 L174](../../src/ccs/run_analysis.py#L174)

```python
_safe_json_object(path: Path, *, limit: int) -> tuple[dict[str, Any], str | None]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `json.loads`, `path.is_file`, `path.is_symlink`, `path.read_text`, `path.stat`

</details>

<a id="fn-ccs-run_analysis-_activity_snapshot"></a>
### `_activity_snapshot`

**함수** · [정의 위치 L184](../../src/ccs/run_analysis.py#L184)

```python
_activity_snapshot(run_dir: Path, run_id: str) -> tuple[list[dict[str, Any]], str | None]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`directory.is_dir`, `directory.is_symlink`, `directory.iterdir`, `event.get`, `isinstance`, `len`, `path.is_file`, `path.is_symlink`, `path.stat`, `path.suffix.casefold`, `read_activity`, `sum`

</details>

<a id="fn-ccs-run_analysis-_manifest_episode"></a>
### `_manifest_episode`

**함수** · [정의 위치 L206](../../src/ccs/run_analysis.py#L206)

```python
_manifest_episode(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_EPISODE_ID.fullmatch`, `isinstance`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_episode_events"></a>
### `_episode_events`

**함수** · [정의 위치 L215](../../src/ccs/run_analysis.py#L215)

```python
_episode_events(events: list[dict[str, Any]], episode_id: str) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`event.get`

</details>

<a id="fn-ccs-run_analysis-_request_and_target"></a>
### `_request_and_target`

**함수** · [정의 위치 L219](../../src/ccs/run_analysis.py#L219)

```python
_request_and_target(events: list[dict[str, Any]]) -> tuple[str | None, str | None]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_text`, `details.get`, `event.get`, `isinstance`, `request.get`

</details>

<a id="fn-ccs-run_analysis-_change_projection"></a>
### `_change_projection`

**함수** · [정의 위치 L231](../../src/ccs/run_analysis.py#L231)

```python
_change_projection(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_text`, `isinstance`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_diagnosis_projection"></a>
### `_diagnosis_projection`

**함수** · [정의 위치 L244](../../src/ccs/run_analysis.py#L244)

```python
_diagnosis_projection(value: Any) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_CAUSE_LABELS.get`, `_change_projection`, `_compact_json`, `_finite_number`, `_text`, `dict`, `isinstance`, `root_cause.replace`, `root_cause.replace('_', ' ').strip`, `root_cause.replace('_', ' ').strip().capitalize`, `source.get`

</details>

<a id="fn-ccs-run_analysis-_verify_projection"></a>
### `_verify_projection`

**함수** · [정의 위치 L263](../../src/ccs/run_analysis.py#L263)

```python
_verify_projection(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_finite_number`, `_text`, `checks.append`, `isinstance`, `type`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_report_projection"></a>
### `_report_projection`

**함수** · [정의 위치 L292](../../src/ccs/run_analysis.py#L292)

```python
_report_projection(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_text`, `isinstance`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_oracle_projection"></a>
### `_oracle_projection`

**함수** · [정의 위치 L305](../../src/ccs/run_analysis.py#L305)

```python
_oracle_projection(value: Any) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_finite_number`, `isinstance`, `len`, `type`, `value.get`

</details>

<a id="fn-ccs-run_analysis-_actual_configuration_changes"></a>
### `_actual_configuration_changes`

**함수** · [정의 위치 L321](../../src/ccs/run_analysis.py#L321)

```python
_actual_configuration_changes(network: Mapping[str, Any]) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_text`, `changes.append`, `isinstance`, `network.get`, `raw.get`

</details>

<a id="fn-ccs-run_analysis-_is_client_tool_event"></a>
### `_is_client_tool_event`

**함수** · [정의 위치 L344](../../src/ccs/run_analysis.py#L344)

```python
_is_client_tool_event(event: Mapping[str, Any], status: str | None=None) -> bool
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`details.get`, `event.get`, `isinstance`

</details>

<a id="fn-ccs-run_analysis-_before_kpis"></a>
### `_before_kpis`

**함수** · [정의 위치 L355](../../src/ccs/run_analysis.py#L355)

```python
_before_kpis(events: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_finite_number`, `_is_client_tool_event`, `_text`, `details.get`, `enumerate`, `event.get`, `isinstance`, `len`, `result.get`, `sample.get`

</details>

<a id="fn-ccs-run_analysis-_final_kpis_for_targets"></a>
### `_final_kpis_for_targets`

**함수** · [정의 위치 L391](../../src/ccs/run_analysis.py#L391)

```python
_final_kpis_for_targets(episode_dir: Path, targets: set[str]) -> dict[tuple[str, str], dict[str, Any]]
```

> Read final KPI values for exact pre-change targets without mutating SQLite.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_ReadOnlyBackend`, `_finite_number`, `_kpis`, `_text`, `backend.call`, `backend.close`, `database.is_file`, `database.is_symlink`, `episode_dir.is_symlink`, `final_state.is_file`, `final_state.is_symlink`, `sample.get`, `sorted`

</details>

<a id="fn-ccs-run_analysis-_after_kpis"></a>
### `_after_kpis`

**함수** · [정의 위치 L434](../../src/ccs/run_analysis.py#L434)

```python
_after_kpis(network: Mapping[str, Any], verify: Mapping[str, Any] | None, exact_final: Mapping[tuple[str, str], dict[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_finite_number`, `_text`, `check.get`, `isinstance`, `network.get`, `sample.get`, `samples.setdefault`, `samples.update`, `verify.get`

</details>

<a id="fn-ccs-run_analysis-_kpi_changes"></a>
### `_kpi_changes`

**함수** · [정의 위치 L490](../../src/ccs/run_analysis.py#L490)

```python
_kpi_changes(events: list[dict[str, Any]], network: Mapping[str, Any], verify: Mapping[str, Any] | None, episode_dir: Path, *, final_state_ready: bool) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(final or {}).get`, `_after_kpis`, `_before_kpis`, `_final_kpis_for_targets`, `after.get`, `before.items`, `changes.append`, `final.get`, `initial.get`, `sorted`

</details>

<a id="fn-ccs-run_analysis-_activity_counts"></a>
### `_activity_counts`

**함수** · [정의 위치 L520](../../src/ccs/run_analysis.py#L520)

```python
_activity_counts(events: list[dict[str, Any]]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Counter`, `_is_client_tool_event`, `components.items`, `details.get`, `dict`, `event.get`, `isinstance`, `len`, `sorted`, `statuses.items`, `str`

</details>

<a id="fn-ccs-run_analysis-_summary_projection"></a>
### `_summary_projection`

**함수** · [정의 위치 L566](../../src/ccs/run_analysis.py#L566)

```python
_summary_projection(summary: Mapping[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`

</details>

<a id="fn-ccs-run_analysis-_conditions_projection"></a>
### `_conditions_projection`

**함수** · [정의 위치 L577](../../src/ccs/run_analysis.py#L577)

```python
_conditions_projection(manifest: Mapping[str, Any], summary: Mapping[str, Any], controller: Mapping[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `_finite_number`, `combined.get`, `combined.update`, `controller.get`, `dict`, `input_conditions.get`, `input_conditions['initial_memory'].get`, `input_conditions['runbooks'].get`, `isinstance`, `metadata.get`, `pacing.get`, `summary.get`, `type`, `web_console.get`

</details>

<a id="fn-ccs-run_analysis-_timing_projection"></a>
### `_timing_projection`

**함수** · [정의 위치 L616](../../src/ccs/run_analysis.py#L616)

```python
_timing_projection(summary: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_compact_json`, `isinstance`, `manifest.get`, `summary.get`

</details>

<a id="fn-ccs-run_analysis-_episode_observations"></a>
### `_episode_observations`

**함수** · [정의 위치 L632](../../src/ccs/run_analysis.py#L632)

```python
_episode_observations(outcome: str, diagnosis: Mapping[str, Any], changes: list[dict[str, Any]], kpis: list[dict[str, Any]], oracle: Mapping[str, Any] | None) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_OUTCOME_TEXT.get`, `_bilingual`, `diagnosis.get`, `dict`, `isinstance`, `item.get`, `len`, `observations.append`, `oracle.get`, `sum`

</details>

<a id="fn-ccs-run_analysis-_limitations"></a>
### `_limitations`

**함수** · [정의 위치 L692](../../src/ccs/run_analysis.py#L692)

```python
_limitations(summary: Mapping[str, Any], *, activity_issue: str | None, artifact_issues: list[str], sealed: bool, status: str, confidence_present: bool) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_LIMITATION_TEXT.get`, `_bilingual`, `add`, `enumerate`, `isinstance`, `set`, `summary.get`, `timing.get`

</details>

<a id="fn-ccs-run_analysis-_limitations-add"></a>
### `_limitations.add`

**함수 (중첩 handler)** · [정의 위치 L699](../../src/ccs/run_analysis.py#L699)

```python
_limitations.add(code: str, text: dict[str, str]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`result.append`, `seen.add`

</details>

<a id="fn-ccs-run_analysis-_insights"></a>
### `_insights`

**함수** · [정의 위치 L770](../../src/ccs/run_analysis.py#L770)

```python
_insights(episodes: list[dict[str, Any]], sealed: bool) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`', '.join`, `Counter`, `_OUTCOME_LABEL_KO.get`, `_bilingual`, `float`, `insights.append`, `isinstance`, `item.get`, `item['oracle'].get`, `len`, `outcomes.items`, `sorted`, `str`, `sum`

</details>

<a id="fn-ccs-run_analysis-analyze_run"></a>
### `analyze_run`

**함수** · [정의 위치 L824](../../src/ccs/run_analysis.py#L824)

```python
analyze_run(run_dir: Path, *, controller_status: str | None=None, controller_record: Mapping[str, Any] | None=None) -> dict[str, Any]
```

> Return a bounded, deterministic analysis without modifying ``run_dir``.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `ValueError`, `_EPISODE_ID.fullmatch`, `_activity_counts`, `_activity_snapshot`, `_actual_configuration_changes`, `_bilingual`, `_change_projection`, `_conditions_projection`, `_diagnosis_projection`, `_episode_events`, `_episode_observations`, `_insights`, `_kpi_changes`, `_limitations`, `_manifest_episode`, `_oracle_projection`, `_report_projection`, `_request_and_target`, `_safe_json_object`, `_scenario_projection`, `_summary_projection`, `_text`, `_timing_projection`, `_verify_projection`, `any`, `artifact_issues.append`, `bool`, `by_manifest.get`, `candidate.get`, `dict`, `directory.exists`, `directory.is_dir`, `directory.is_symlink`, `episode_ids.append`, `episodes.append`, `event.get`, `integrity.get`, `isinstance`, `item['diagnosis'].get`, `len`, `list`, `manifest.get`, `manifest_episode.get`, `network.get`, `raw_root.is_dir`, `raw_root.is_symlink`, `raw_root.resolve`, `read_network`, `result.get`, `str`, `str(controller_status or '').upper`, `str(manifest.get('status') or summary.get('status') or 'UNKNOWN').upper`, `str(result.get('outcome') or manifest_episode.get('outcome') or 'UNKNOWN').upper`, `summary.get`, `type`

</details>

<a id="module-ccs-runner"></a>
## `ccs.runner`

[소스 파일](../../src/ccs/runner.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Three-process, finite-episode runner for the D0 baseline.

<a id="fn-ccs-runner-write_json"></a>
### `write_json`

**함수** · [정의 위치 L33](../../src/ccs/runner.py#L33)

```python
write_json(path, value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `getattr`, `json.dumps`, `len`, `os.replace`, `path.parent.mkdir`, `path.with_name`, `range`, `time.sleep`, `writing.unlink`, `writing.write_text`

</details>

<a id="fn-ccs-runner-utc"></a>
### `utc`

**함수** · [정의 위치 L50](../../src/ccs/runner.py#L50)

```python
utc()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`datetime.now`, `datetime.now(timezone.utc).isoformat`

</details>

<a id="fn-ccs-runner-sha"></a>
### `sha`

**함수** · [정의 위치 L52](../../src/ccs/runner.py#L52)

```python
sha(path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(path).read_bytes`, `hashlib.sha256`, `hashlib.sha256(Path(path).read_bytes()).hexdigest`

</details>

<a id="fn-ccs-runner-value_hash"></a>
### `value_hash`

**함수** · [정의 위치 L54](../../src/ccs/runner.py#L54)

```python
value_hash(value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`hashlib.sha256`, `hashlib.sha256(encoded).hexdigest`, `json.dumps`, `json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(',', ':')).encode`

</details>

<a id="fn-ccs-runner-snapshot_runbooks"></a>
### `snapshot_runbooks`

**함수** · [정의 위치 L58](../../src/ccs/runner.py#L58)

```python
snapshot_runbooks(source, destination)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FileNotFoundError`, `Path`, `Path(source).resolve`, `ValueError`, `destination.mkdir`, `path.relative_to`, `records.append`, `relative.as_posix`, `runbook_files`, `sha`, `shutil.copy2`, `source.is_dir`, `source.is_file`, `source.suffix.lower`, `target.parent.mkdir`, `target.stat`

</details>

<a id="fn-ccs-runner-normalize_initial_memory"></a>
### `normalize_initial_memory`

**함수** · [정의 위치 L72](../../src/ccs/runner.py#L72)

```python
normalize_initial_memory(records)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TypeError`, `ValueError`, `enumerate`, `isinstance`, `item[key].strip`, `normalized.append`, `seen.add`, `set`

</details>

<a id="fn-ccs-runner-runtime_system_copy"></a>
### `runtime_system_copy`

**함수** · [정의 위치 L87](../../src/ccs/runner.py#L87)

```python
runtime_system_copy(source, destination, request_timeout)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ET.parse`, `ValueError`, `destination.parent.mkdir`, `float`, `format`, `format(float(request_timeout), '.6f').rstrip`, `format(float(request_timeout), '.6f').rstrip('0').rstrip`, `network.set`, `tree.getroot`, `tree.getroot().find`, `tree.write`

</details>

<a id="fn-ccs-runner-source_hashes"></a>
### `source_hashes`

**함수** · [정의 위치 L94](../../src/ccs/runner.py#L94)

```python
source_hashes(root)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(root).glob`, `p.is_file`, `p.relative_to`, `runbook_files`, `sha`, `sorted`, `str`, `str(p.relative_to(root)).replace`

</details>

<a id="fn-ccs-runner-_record_run_failure"></a>
### `_record_run_failure`

**함수** · [정의 위치 L98](../../src/ccs/runner.py#L98)

```python
_record_run_failure(run_dir, manifest, phase, exc, *, error_field, record_name)
```

> Best-effort terminal record without leaking exception text or sealing partial output.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(Path(run_dir) / name).unlink`, `Path`, `getattr`, `json.loads`, `manifest.pop`, `summary_path.exists`, `summary_path.read_text`, `summary_path.unlink`, `type`, `utc`, `write_json`

</details>

<a id="fn-ccs-runner-_record_finalization_failure"></a>
### `_record_finalization_failure`

**함수** · [정의 위치 L140](../../src/ccs/runner.py#L140)

```python
_record_finalization_failure(run_dir, manifest, effective, phase, exc)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_record_run_failure`

</details>

<a id="fn-ccs-runner-_seal_artifacts"></a>
### `_seal_artifacts`

**함수** · [정의 위치 L143](../../src/ccs/runner.py#L143)

```python
_seal_artifacts(run_dir)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `path.is_file`, `path.relative_to`, `run_dir.rglob`, `sha`, `sorted`, `str`, `str(path.relative_to(run_dir)).replace`

</details>

<a id="fn-ccs-runner-_finalize_run"></a>
### `_finalize_run`

**함수** · [정의 위치 L148](../../src/ccs/runner.py#L148)

```python
_finalize_run(run_dir, manifest, effective, input_conditions, run_started_ns, registry, ai, mode, activity, run_operation)
```

> Finalize a completed/failed episode set; failures are terminal and unsealed.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetLedger`, `BudgetLedger(ai.ledger_path, ai.budget_usd).summary`, `Decimal`, `Path`, `_record_finalization_failure`, `_seal_artifacts`, `activity.emit`, `bool`, `build_ledger`, `json.loads`, `len`, `path.read_text`, `path.read_text(encoding='utf-8').splitlines`, `run_dir.glob`, `sha`, `str`, `sum`, `summarize_timing`, `time.time_ns`, `utc`, `validate_and_merge`, `write_json`, `write_reports`, `write_snapshot`, `x.get`

</details>

<a id="class-ccs-runner-Workflow"></a>
### `Workflow`

**클래스** · [정의 위치 L207](../../src/ccs/runner.py#L207)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-runner-Workflow-__init__"></a>
### `Workflow.__init__`

**메서드** · [정의 위치 L208](../../src/ccs/runner.py#L208)

```python
Workflow.__init__(self, path, activity=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-runner-Workflow-transition"></a>
### `Workflow.transition`

**메서드** · [정의 위치 L209](../../src/ccs/runner.py#L209)

```python
Workflow.transition(self, state, *, delay_after=True)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `file.write`, `json.dumps`, `len`, `self.activity.emit`, `self.history.append`, `self.path.open`, `utc`

</details>

<a id="fn-ccs-runner-approve"></a>
### `approve`

**함수** · [정의 위치 L216](../../src/ccs/runner.py#L216)

```python
approve(policy, label)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`input`, `input(f'{label} [y/N]: ').strip`, `input(f'{label} [y/N]: ').strip().lower`

</details>

<a id="fn-ccs-runner-observed_approval"></a>
### `observed_approval`

**함수** · [정의 위치 L222](../../src/ccs/runner.py#L222)

```python
observed_approval(activity, policy, label)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`activity.emit`, `approve`

</details>

<a id="fn-ccs-runner-execute_episode"></a>
### `execute_episode`

**비동기 함수** · [정의 위치 L229](../../src/ccs/runner.py#L229)

```python
async execute_episode(system, ai, system_path, ai_path, run_dir, bus, runbooks, memory, scenario, episode_dir, *, mode, profile_override=None, rag_enabled=True)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2AClient`, `A2AClient(a2a_url, a2a_token, timeout_seconds=system.request_timeout).diagnose`, `ActivityLog`, `DiagnosisRequest`, `Gateway`, `InstrumentedTools`, `MemoryRecord`, `Services`, `ToolFailure`, `Workflow`, `activity.emit`, `ai.keys.values`, `bool`, `choose_port`, `collect_context`, `compose_report`, `context.get`, `ep.rsplit`, `facts['diagnosis'].get`, `facts['verify'].get`, `gateway.pass_through`, `int`, `len`, `memory.write`, `observed_approval`, `propose_memory`, `scenario.get`, `secrets.token_urlsafe`, `select_change`, `status.get`, `str`, `time.monotonic`, `tools.call`, `type`, `uuid.uuid4`, `verified.get`, `workflow.transition`, `write_json`

</details>

<a id="fn-ccs-runner-run"></a>
### `run`

**비동기 함수** · [정의 위치 L328](../../src/ccs/runner.py#L328)

```python
async run(system_path: Path, ai_path: Path, *, mode='mock', faults=None, seeds=None, repeat=1, profile_override=None, memory_off=False, output_root=None, request_override=None, on_created=None, runbooks_override: Path | None=None, initial_memory: list[dict] | None=None, rag_enabled: bool=True, delay_control_path: Path | None=None, experiment_metadata: dict | None=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ActivityLog`, `ActivityLog(run_dir, f'oracle-{ep}', ep, mode=mode, secrets=ai.keys.values()).emit`, `EventBus`, `MemoryStore`, `Path`, `Path(ai_path).resolve`, `Path(delay_control_path).resolve`, `Path(runbooks_override).resolve`, `Path(system_path).resolve`, `RunbookStore`, `SQLiteBackend`, `TypeError`, `ValueError`, `_finalize_run`, `_record_run_failure`, `activity.emit`, `ai.keys.get`, `ai.keys.values`, `ai.profile`, `ai.public`, `any`, `backend.close`, `backend.snapshot`, `create_world`, `datetime.now`, `datetime.now(timezone.utc).strftime`, `ep_dir.mkdir`, `evaluate`, `execute_episode`, `facts['diagnosis'].get`, `importlib.metadata.version`, `input_dir.mkdir`, `install_run_pointer`, `isinstance`, `item.get`, `json.dumps`, `json.loads`, `len`, `list`, `load_ai`, `load_system`, `manifest['episodes'].append`, `memory.close`, `memory.import_reference`, `normalize_initial_memory`, `on_created`, `platform.platform`, `platform.python_version`, `print`, `range`, `read_control`, `registry.extend`, `resource.close`, `root.mkdir`, `run_dir.mkdir`, `runbooks.close`, `runtime_system_copy`, `scenario.get`, `scenario.get('ground_truth', {}).get`, `set`, `sha`, `snapshot_runbooks`, `source_hashes`, `system.public`, `time.time_ns`, `timeout_allowance_seconds`, `type`, `utc`, `uuid.uuid4`, `value_hash`, `wait_after_event`, `write_control`, `write_json`

</details>

<a id="module-ccs-scenario_catalog"></a>
## `ccs.scenario_catalog`

[소스 파일](../../src/ccs/scenario_catalog.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Operator-facing stories for the wired scenario catalog.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-services"></a>
## `ccs.services`

[소스 파일](../../src/ccs/services.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Private entrypoint for the two child services; no evaluator imports in Diagnosis.

<a id="fn-ccs-services-main"></a>
### `main`

**함수** · [정의 위치 L13](../../src/ccs/services.py#L13)

```python
main()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `Gateway`, `Path`, `SQLiteBackend`, `activity_for_episode`, `argparse.ArgumentParser`, `args.context.read_text`, `build_a2a_app`, `build_mcp_app`, `context.get`, `json.loads`, `load_ai`, `load_system`, `parser.add_argument`, `parser.parse_args`, `r.upper`, `tool_schemas`, `uvicorn.run`

</details>

<a id="fn-ccs-services-main-handler"></a>
### `main.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L27](../../src/ccs/services.py#L27)

```python
async main.handler(name, arguments, metadata)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`activity.emit`, `backend.call`, `gateway.pass_through`, `getattr`, `hashlib.sha256`, `hashlib.sha256(json.dumps(arguments, sort_keys=True).encode()).hexdigest`, `json.dumps`, `json.dumps(arguments, sort_keys=True).encode`, `metadata.get`, `str`, `time.monotonic`, `type`

</details>

<a id="fn-ccs-services-main-handler-2"></a>
### `main.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L55](../../src/ccs/services.py#L55)

```python
async main.handler(payload, metadata)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`InstrumentedTools`, `Path`, `activity.emit`, `context.get`, `diagnose`, `metadata.get`, `payload.get`, `time.monotonic`, `type`

</details>

<a id="module-ccs-studio_markup"></a>
## `ccs.studio_markup`

[소스 파일](../../src/ccs/studio_markup.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Semantic three-tab console markup; raw content is filled using textContent.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-studio_script"></a>
## `ccs.studio_script`

[소스 파일](../../src/ccs/studio_script.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: UI controller. No model calls or changes to recorded evidence are made here.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-studio_styles"></a>
## `ccs.studio_styles`

[소스 파일](../../src/ccs/studio_styles.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Light visual system shared by the NetOps Studio console.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-ccs-tool_access"></a>
## `ccs.tool_access`

[소스 파일](../../src/ccs/tool_access.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Client-side tool gateway; all Agent network access uses MCP.

<a id="class-ccs-tool_access-ToolFailure"></a>
### `ToolFailure`

**클래스** · [정의 위치 L6](../../src/ccs/tool_access.py#L6)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-tool_access-InstrumentedTools"></a>
### `InstrumentedTools`

**클래스** · [정의 위치 L8](../../src/ccs/tool_access.py#L8)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-tool_access-InstrumentedTools-__init__"></a>
### `InstrumentedTools.__init__`

**메서드** · [정의 위치 L9](../../src/ccs/tool_access.py#L9)

```python
InstrumentedTools.__init__(self, url, token, gateway, role, trace_id, *, timeout=120, read_retries=2, cause=None, mode=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MCPClient`, `activity_for_episode`

</details>

<a id="fn-ccs-tool_access-InstrumentedTools-list_tools"></a>
### `InstrumentedTools.list_tools`

**비동기 메서드** · [정의 위치 L16](../../src/ccs/tool_access.py#L16)

```python
async InstrumentedTools.list_tools(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`len`, `self.activity.emit`, `self.client.list_tools`, `time.monotonic`, `type`

</details>

<a id="fn-ccs-tool_access-InstrumentedTools-call"></a>
### `InstrumentedTools.call`

**비동기 메서드** · [정의 위치 L30](../../src/ccs/tool_access.py#L30)

```python
async InstrumentedTools.call(self, name, arguments)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ToolFailure`, `range`, `result.pop`, `self.activity.emit`, `self.client.call`, `self.gateway.pass_through`, `str`, `time.monotonic`, `type`

</details>

<a id="module-ccs-web_console"></a>
## `ccs.web_console`

[소스 파일](../../src/ccs/web_console.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Authenticated local experiment controller used by the browser console.  The controller owns mutable operator state outside immutable run artifacts. It serves loopback by default and can bind one explicitly allowlisted IPv4 LAN address. Requests use a per-process capability token; LAN requests also pass peer, Host, and same-Origin checks. Library input is frozen before each run and those snapshots are passed to :mod:`ccs.runner`.

<a id="class-ccs-web_console-WebConsoleBindError"></a>
### `WebConsoleBindError`

**클래스** · [정의 위치 L56](../../src/ccs/web_console.py#L56)

상속/계약: `RuntimeError`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> A failure to bind the web console listener, with no OS detail exposed.

<a id="fn-ccs-web_console-WebConsoleBindError-__init__"></a>
### `WebConsoleBindError.__init__`

**메서드** · [정의 위치 L59](../../src/ccs/web_console.py#L59)

```python
WebConsoleBindError.__init__(self, host: str, port: int, error: OSError)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`getattr`, `isinstance`, `super`, `super().__init__`

</details>

<a id="fn-ccs-web_console-_utc"></a>
### `_utc`

**함수** · [정의 위치 L83](../../src/ccs/web_console.py#L83)

```python
_utc() -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`datetime.now`, `datetime.now(timezone.utc).isoformat`

</details>

<a id="fn-ccs-web_console-_atomic_json"></a>
### `_atomic_json`

**함수** · [정의 위치 L87](../../src/ccs/web_console.py#L87)

```python
_atomic_json(path: Path, value: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`, `os.replace`, `path.parent.mkdir`, `path.with_name`, `writing.write_text`

</details>

<a id="fn-ccs-web_console-_read_object"></a>
### `_read_object`

**함수** · [정의 위치 L94](../../src/ccs/web_console.py#L94)

```python
_read_object(path: Path, default: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`deepcopy`, `isinstance`, `json.loads`, `path.read_text`

</details>

<a id="fn-ccs-web_console-_within"></a>
### `_within`

**함수** · [정의 위치 L102](../../src/ccs/web_console.py#L102)

```python
_within(path: Path, parent: Path) -> bool
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`parent.resolve`, `path.resolve`, `path.resolve().is_relative_to`

</details>

<a id="fn-ccs-web_console-_safe_existing_file"></a>
### `_safe_existing_file`

**함수** · [정의 위치 L109](../../src/ccs/web_console.py#L109)

```python
_safe_existing_file(path: Path, label: str) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `path.is_file`, `path.is_symlink`, `path.resolve`

</details>

<a id="fn-ccs-web_console-_safe_directory"></a>
### `_safe_directory`

**함수** · [정의 위치 L115](../../src/ccs/web_console.py#L115)

```python
_safe_directory(path: Path, parent: Path | None=None) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `parent.resolve`, `path.is_dir`, `path.is_symlink`, `path.mkdir`, `path.resolve`, `resolved.is_relative_to`

</details>

<a id="fn-ccs-web_console-_safe_text"></a>
### `_safe_text`

**함수** · [정의 위치 L127](../../src/ccs/web_console.py#L127)

```python
_safe_text(value: Any, field: str, *, limit: int, empty: bool=False) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `isinstance`, `len`, `value.encode`, `value.replace`, `value.replace('\x00', '').strip`

</details>

<a id="fn-ccs-web_console-_bool"></a>
### `_bool`

**함수** · [정의 위치 L136](../../src/ccs/web_console.py#L136)

```python
_bool(value: Any, field: str) -> bool
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `type`

</details>

<a id="fn-ccs-web_console-_int"></a>
### `_int`

**함수** · [정의 위치 L142](../../src/ccs/web_console.py#L142)

```python
_int(value: Any, field: str, low: int, high: int) -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `type`

</details>

<a id="fn-ccs-web_console-_delay"></a>
### `_delay`

**함수** · [정의 위치 L148](../../src/ccs/web_console.py#L148)

```python
_delay(value: Any) -> float
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `float`, `isinstance`, `math.isfinite`

</details>

<a id="fn-ccs-web_console-_write_delay"></a>
### `_write_delay`

**함수** · [정의 위치 L157](../../src/ccs/web_console.py#L157)

```python
_write_delay(path: Path, seconds: float) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`write_control`

</details>

<a id="fn-ccs-web_console-_read_delay"></a>
### `_read_delay`

**함수** · [정의 위치 L163](../../src/ccs/web_console.py#L163)

```python
_read_delay(path: Path) -> float
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`float`, `read_control`

</details>

<a id="fn-ccs-web_console-_front_matter"></a>
### `_front_matter`

**함수** · [정의 위치 L169](../../src/ccs/web_console.py#L169)

```python
_front_matter(content: str, doc_id: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`content.lstrip`, `stripped.startswith`

</details>

<a id="fn-ccs-web_console-_title_from_markdown"></a>
### `_title_from_markdown`

**함수** · [정의 위치 L185](../../src/ccs/web_console.py#L185)

```python
_title_from_markdown(content: str, fallback: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`content.splitlines`, `line.startswith`, `line[2:].strip`

</details>

<a id="class-ccs-web_console-_ConsoleHTTPServer"></a>
### `_ConsoleHTTPServer`

**클래스** · [정의 위치 L192](../../src/ccs/web_console.py#L192)

상속/계약: `ThreadingHTTPServer`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="class-ccs-web_console-WebConsoleServer"></a>
### `WebConsoleServer`

**클래스** · [정의 위치 L197](../../src/ccs/web_console.py#L197)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

> Serve and execute the local CCS experiment console.  ``workspace`` stores the mutable library, conditions and delay control. Run artifacts follow system.xml output_root, frozen separately for each run.

<a id="fn-ccs-web_console-WebConsoleServer-__init__"></a>
### `WebConsoleServer.__init__`

**메서드** · [정의 위치 L204](../../src/ccs/web_console.py#L204)

```python
WebConsoleServer.__init__(self, system_path: str | Path, ai_path: str | Path, workspace: Path, port: int=0, *, host: str='127.0.0.1', allowed_networks: tuple[str, ...]=())
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `TypeError`, `ValueError`, `_delay`, `_read_object`, `_safe_directory`, `_safe_existing_file`, `_write_delay`, `any`, `ipaddress.IPv4Address`, `ipaddress.IPv4Network`, `isinstance`, `load_system`, `load_system(self.system_path).output_root.resolve`, `path.is_symlink`, `secrets.token_urlsafe`, `self._config.get`, `self._delay_path.exists`, `self._initialize_runbooks`, `self._migrate_catalog`, `self._normalize_persistent_state`, `str`, `threading.RLock`, `tuple`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_migrate_catalog"></a>
### `WebConsoleServer._migrate_catalog`

**메서드** · [정의 위치 L249](../../src/ccs/web_console.py#L249)

```python
WebConsoleServer._migrate_catalog(self) -> None
```

> Start a clean wired library/index while retaining legacy evidence.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_atomic_json`, `_safe_directory`, `self._state.get`, `str`, `uuid.uuid4`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_normalize_persistent_state"></a>
### `WebConsoleServer._normalize_persistent_state`

**메서드** · [정의 위치 L259](../../src/ccs/web_console.py#L259)

```python
WebConsoleServer._normalize_persistent_state(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_delay`, `_utc`, `entry.get`, `isinstance`, `self._config.get`, `self._record_path`, `self._save_locked`, `self._state.get`, `str`, `str(entry.get('status', '')).upper`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_save_locked"></a>
### `WebConsoleServer._save_locked`

**메서드** · [정의 위치 L279](../../src/ccs/web_console.py#L279)

```python
WebConsoleServer._save_locked(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_atomic_json`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_initialize_runbooks"></a>
### `WebConsoleServer._initialize_runbooks`

**메서드** · [정의 위치 L283](../../src/ccs/web_console.py#L283)

```python
WebConsoleServer._initialize_runbooks(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_title_from_markdown`, `_utc`, `_within`, `any`, `isinstance`, `item.get`, `load_system`, `path.is_symlink`, `path.read_text`, `path.relative_to`, `path.relative_to(source).as_posix`, `runbook_files`, `self._save_locked`, `self._state['documents'].append`, `source.is_dir`, `source.is_symlink`, `uuid.uuid5`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-start"></a>
### `WebConsoleServer.start`

**메서드** · [정의 위치 L311](../../src/ccs/web_console.py#L311)

```python
WebConsoleServer.start(self) -> 'WebConsoleServer'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleBindError`, `_ConsoleHTTPServer`, `int`, `partial`, `quote`, `self._thread.start`, `threading.Thread`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-stop"></a>
### `WebConsoleServer.stop`

**메서드** · [정의 위치 L327](../../src/ccs/web_console.py#L327)

```python
WebConsoleServer.stop(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`TimeoutError`, `_write_delay`, `self._loop.call_soon_threadsafe`, `server.server_close`, `server.shutdown`, `thread.join`, `threading.current_thread`, `worker.is_alive`, `worker.join`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-__enter__"></a>
### `WebConsoleServer.__enter__`

**메서드** · [정의 위치 L351](../../src/ccs/web_console.py#L351)

```python
WebConsoleServer.__enter__(self) -> 'WebConsoleServer'
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.start`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-__exit__"></a>
### `WebConsoleServer.__exit__`

**메서드** · [정의 위치 L354](../../src/ccs/web_console.py#L354)

```python
WebConsoleServer.__exit__(self, *_: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.stop`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_documents"></a>
### `WebConsoleServer._documents`

**메서드** · [정의 위치 L357](../../src/ccs/web_console.py#L357)

```python
WebConsoleServer._documents(self, kind: str) -> list[dict[str, Any]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `item.get`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_find_document"></a>
### `WebConsoleServer._find_document`

**메서드** · [정의 위치 L364](../../src/ccs/web_console.py#L364)

```python
WebConsoleServer._find_document(self, kind: str, identifier: str) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`KeyError`, `ValueError`, `_DOC_ID.fullmatch`, `isinstance`, `item.get`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_assert_library_unlocked"></a>
### `WebConsoleServer._assert_library_unlocked`

**메서드** · [정의 위치 L372](../../src/ccs/web_console.py#L372)

```python
WebConsoleServer._assert_library_unlocked(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `self._worker.is_alive`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-add_document"></a>
### `WebConsoleServer.add_document`

**메서드** · [정의 위치 L376](../../src/ccs/web_console.py#L376)

```python
WebConsoleServer.add_document(self, payload: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_front_matter`, `_safe_text`, `_utc`, `self._assert_library_unlocked`, `self._save_locked`, `self._state['documents'].append`, `set`, `uuid.uuid4`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-select_document"></a>
### `WebConsoleServer.select_document`

**메서드** · [정의 위치 L403](../../src/ccs/web_console.py#L403)

```python
WebConsoleServer.select_document(self, payload: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_bool`, `self._assert_library_unlocked`, `self._find_document`, `self._save_locked`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-edit_document"></a>
### `WebConsoleServer.edit_document`

**메서드** · [정의 위치 L412](../../src/ccs/web_console.py#L412)

```python
WebConsoleServer.edit_document(self, payload: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_front_matter`, `_safe_text`, `_utc`, `len`, `self._assert_library_unlocked`, `self._find_document`, `self._save_locked`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-remove_document"></a>
### `WebConsoleServer.remove_document`

**메서드** · [정의 위치 L426](../../src/ccs/web_console.py#L426)

```python
WebConsoleServer.remove_document(self, payload: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_utc`, `self._assert_library_unlocked`, `self._find_document`, `self._save_locked`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-clear_memory"></a>
### `WebConsoleServer.clear_memory`

**메서드** · [정의 위치 L436](../../src/ccs/web_console.py#L436)

```python
WebConsoleServer.clear_memory(self, payload: dict[str, Any]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_utc`, `item.get`, `self._assert_library_unlocked`, `self._save_locked`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-set_delay"></a>
### `WebConsoleServer.set_delay`

**메서드** · [정의 위치 L448](../../src/ccs/web_console.py#L448)

```python
WebConsoleServer.set_delay(self, payload: dict[str, Any]) -> float
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_delay`, `_utc`, `_write_delay`, `self._save_locked`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_validate_start"></a>
### `WebConsoleServer._validate_start`

**메서드** · [정의 위치 L459](../../src/ccs/web_console.py#L459)

```python
WebConsoleServer._validate_start(self, payload: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_bool`, `_delay`, `_int`, `_safe_text`, `ai.keys.get`, `any`, `isinstance`, `len`, `list`, `load_ai`, `load_system`, `payload.get`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_freeze_inputs"></a>
### `WebConsoleServer._freeze_inputs`

**메서드** · [정의 위치 L514](../../src/ccs/web_console.py#L514)

```python
WebConsoleServer._freeze_inputs(self, launch_id: str, conditions: dict[str, Any]) -> tuple[Path, list[dict[str, Any]], Path]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(runbooks / f"runbook-{index:04d}-{item['id']}.md").write_text`, `_atomic_json`, `_safe_directory`, `_utc`, `enumerate`, `item.get`, `len`, `self._write_system_snapshot`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_write_system_snapshot"></a>
### `WebConsoleServer._write_system_snapshot`

**메서드** · [정의 위치 L540](../../src/ccs/web_console.py#L540)

```python
WebConsoleServer._write_system_snapshot(self, snapshot: Path, conditions: dict[str, Any], runbooks: Path) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`','.join`, `ET.ElementTree`, `ET.ElementTree(root).write`, `ET.parse`, `ET.parse(self.system_path).getroot`, `ValueError`, `_safe_directory`, `experiment.set`, `load_system`, `paths.set`, `root.find`, `str`, `workflow.set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-start_run"></a>
### `WebConsoleServer.start_run`

**메서드** · [정의 위치 L568](../../src/ccs/web_console.py#L568)

```python
WebConsoleServer.start_run(self, payload: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `_write_delay`, `deepcopy`, `self._freeze_inputs`, `self._save_locked`, `self._validate_start`, `self._worker.is_alive`, `threading.Thread`, `uuid.uuid4`, `worker.start`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_run_worker"></a>
### `WebConsoleServer._run_worker`

**메서드** · [정의 위치 L591](../../src/ccs/web_console.py#L591)

```python
WebConsoleServer._run_worker(self, launch_id: str, conditions: dict[str, Any], runbooks: Path, memory: list[dict[str, Any]], config_path: Path) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(completed_dir).resolve`, `asyncio.new_event_loop`, `asyncio.set_event_loop`, `load_system`, `load_system(config_path).output_root.resolve`, `loop.call_soon`, `loop.close`, `loop.create_task`, `loop.run_until_complete`, `loop.shutdown_asyncgens`, `run`, `self._finish_run`, `self._import_generated_memory`, `self._save_locked`, `str`, `str(summary.get('status', 'COMPLETED')).upper`, `summary.get`, `type`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_run_worker-on_created"></a>
### `WebConsoleServer._run_worker.on_created`

**함수 (중첩 handler)** · [정의 위치 L595](../../src/ccs/web_console.py#L595)

```python
WebConsoleServer._run_worker.on_created(created: Path) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `RuntimeError`, `_RUN_ID.fullmatch`, `_utc`, `created.parent.samefile`, `created_raw.is_symlink`, `created_raw.resolve`, `deepcopy`, `self._save_locked`, `self._state['runs'].append`, `str`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_finish_run"></a>
### `WebConsoleServer._finish_run`

**메서드** · [정의 위치 L671](../../src/ccs/web_console.py#L671)

```python
WebConsoleServer._finish_run(self, run_dir: Path | None, status: str, *, summary: dict[str, Any] | None=None, error_type: str | None=None) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(self._state.get('active') or {}).get`, `_utc`, `isinstance`, `next`, `reversed`, `self._public_summary`, `self._save_locked`, `self._state.get`, `str`, `x.get`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_public_summary"></a>
### `WebConsoleServer._public_summary`

**메서드** · [정의 위치 L689](../../src/ccs/web_console.py#L689)

```python
WebConsoleServer._public_summary(summary: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-web_console-WebConsoleServer-_import_generated_memory"></a>
### `WebConsoleServer._import_generated_memory`

**메서드** · [정의 위치 L699](../../src/ccs/web_console.py#L699)

```python
WebConsoleServer._import_generated_memory(self, run_dir: Path) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_utc`, `_within`, `connection.close`, `connection.execute`, `database.as_posix`, `database.is_file`, `database.is_symlink`, `json.dumps`, `json.loads`, `locals`, `self._save_locked`, `self._state['documents'].append`, `sqlite3.connect`, `str`, `str(row['verified_outcome']).strip`, `str(row['verified_outcome']).strip().casefold`, `uuid.uuid4`, `x.get`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-stop_run"></a>
### `WebConsoleServer.stop_run`

**메서드** · [정의 위치 L745](../../src/ccs/web_console.py#L745)

```python
WebConsoleServer.stop_run(self, payload: dict[str, Any]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `ValueError`, `_write_delay`, `dict`, `self._loop.call_soon_threadsafe`, `self._save_locked`, `self._state.get`, `self._worker.is_alive`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_record_path"></a>
### `WebConsoleServer._record_path`

**메서드** · [정의 위치 L762](../../src/ccs/web_console.py#L762)

```python
WebConsoleServer._record_path(self, record: dict[str, Any]) -> Path
```

> Resolve only an indexed run; pin legacy locations without moving files.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`KeyError`, `Path`, `Path(stored_path).resolve`, `Path(stored_root).is_absolute`, `_RUN_ID.fullmatch`, `_within`, `isinstance`, `path.is_dir`, `path.is_symlink`, `path.resolve`, `record.get`, `root.is_symlink`, `root.resolve`, `str`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_run_record"></a>
### `WebConsoleServer._run_record`

**메서드** · [정의 위치 L793](../../src/ccs/web_console.py#L793)

```python
WebConsoleServer._run_record(self, run_id: str) -> tuple[dict[str, Any], Path]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`KeyError`, `_RUN_ID.fullmatch`, `isinstance`, `next`, `self._record_path`, `x.get`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-state_for_run"></a>
### `WebConsoleServer.state_for_run`

**메서드** · [정의 위치 L802](../../src/ccs/web_console.py#L802)

```python
WebConsoleServer.state_for_run(self, run_id: str, cursor: str) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_decode_cursor`, `_encode_cursor`, `_metadata`, `_read_incremental`, `self._run_record`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-network_state"></a>
### `WebConsoleServer.network_state`

**메서드** · [정의 위치 L807](../../src/ccs/web_console.py#L807)

```python
WebConsoleServer.network_state(self, query: dict[str, list[str]]) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `_EPISODE_ID.fullmatch`, `_int`, `int`, `load_system`, `preview_network`, `query.get`, `read_network`, `self._run_record`, `set`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-analysis_state"></a>
### `WebConsoleServer.analysis_state`

**메서드** · [정의 위치 L835](../../src/ccs/web_console.py#L835)

```python
WebConsoleServer.analysis_state(self, query: dict[str, list[str]]) -> dict[str, Any]
```

> Return the read-only analysis for one controller-indexed run.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ValueError`, `active.get`, `analyze_run`, `controller_record.get`, `deepcopy`, `len`, `query.get`, `self._run_record`, `self._state.get`, `self._worker.is_alive`, `set`, `str`, `str(active.get('status', 'UNKNOWN')).upper`, `str(controller_record.get('status', '')).upper`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-_refresh_runs"></a>
### `WebConsoleServer._refresh_runs`

**메서드** · [정의 위치 L865](../../src/ccs/web_console.py#L865)

```python
WebConsoleServer._refresh_runs(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_read_object`, `manifest.get`, `record.get`, `self._public_summary`, `self._record_path`, `str`, `str(manifest.get('status', '')).upper`, `str(record.get('status', '')).upper`

</details>

<a id="fn-ccs-web_console-WebConsoleServer-console_state"></a>
### `WebConsoleServer.console_state`

**메서드** · [정의 위치 L887](../../src/ccs/web_console.py#L887)

```python
WebConsoleServer.console_state(self) -> dict[str, Any]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_read_delay`, `ai.profiles.values`, `deepcopy`, `float`, `list`, `load_ai`, `load_system`, `reversed`, `runs.append`, `self._config.get`, `self._documents`, `self._refresh_runs`, `self._state.get`, `str`, `system.output_root.resolve`

</details>

<a id="class-ccs-web_console-_ConsoleHandler"></a>
### `_ConsoleHandler`

**클래스** · [정의 위치 L936](../../src/ccs/web_console.py#L936)

상속/계약: `BaseHTTPRequestHandler`

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-web_console-_ConsoleHandler-__init__"></a>
### `_ConsoleHandler.__init__`

**메서드** · [정의 위치 L939](../../src/ccs/web_console.py#L939)

```python
_ConsoleHandler.__init__(self, *args: Any, console: WebConsoleServer, **kwargs: Any)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`super`, `super().__init__`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-log_message"></a>
### `_ConsoleHandler.log_message`

**메서드** · [정의 위치 L943](../../src/ccs/web_console.py#L943)

```python
_ConsoleHandler.log_message(self, _format: str, *args: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-ccs-web_console-_ConsoleHandler-_headers"></a>
### `_ConsoleHandler._headers`

**메서드** · [정의 위치 L946](../../src/ccs/web_console.py#L946)

```python
_ConsoleHandler._headers(self, content_type: str, length: int) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.send_header`, `str`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-_send"></a>
### `_ConsoleHandler._send`

**메서드** · [정의 위치 L959](../../src/ccs/web_console.py#L959)

```python
_ConsoleHandler._send(self, status: HTTPStatus, body: bytes, content_type: str='text/plain; charset=utf-8') -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`len`, `self._headers`, `self.end_headers`, `self.send_response`, `self.wfile.write`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-_json"></a>
### `_ConsoleHandler._json`

**메서드** · [정의 위치 L966](../../src/ccs/web_console.py#L966)

```python
_ConsoleHandler._json(self, status: HTTPStatus, value: Any) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.dumps`, `json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False).encode`, `self._send`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-_error"></a>
### `_ConsoleHandler._error`

**메서드** · [정의 위치 L969](../../src/ccs/web_console.py#L969)

```python
_ConsoleHandler._error(self, status: HTTPStatus, error_type: str, message: str) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self._json`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-_parsed"></a>
### `_ConsoleHandler._parsed`

**메서드** · [정의 위치 L972](../../src/ccs/web_console.py#L972)

```python
_ConsoleHandler._parsed(self) -> tuple[Any, dict[str, list[str]]] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`any`, `hmac.compare_digest`, `ipaddress.ip_address`, `parse_qs`, `query.get`, `self._error`, `self.headers.get`, `urlsplit`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-do_HEAD"></a>
### `_ConsoleHandler.do_HEAD`

**메서드** · [정의 위치 L990](../../src/ccs/web_console.py#L990)

```python
_ConsoleHandler.do_HEAD(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`self.do_GET`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-do_GET"></a>
### `_ConsoleHandler.do_GET`

**메서드** · [정의 위치 L993](../../src/ccs/web_console.py#L993)

```python
_ConsoleHandler.do_GET(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`document`, `document().encode`, `monitor_document`, `monitor_document().encode`, `query.get`, `self._error`, `self._json`, `self._parsed`, `self._send`, `self.console._run_record`, `self.console.analysis_state`, `self.console.console_state`, `self.console.network_state`, `self.console.state_for_run`, `str`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-_read_payload"></a>
### `_ConsoleHandler._read_payload`

**메서드** · [정의 위치 L1034](../../src/ccs/web_console.py#L1034)

```python
_ConsoleHandler._read_payload(self) -> dict[str, Any] | None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`int`, `isinstance`, `json.loads`, `self._error`, `self.headers.get`, `self.headers.get('Content-Type', '').split`, `self.headers.get('Content-Type', '').split(';', 1)[0].strip`, `self.headers.get('Content-Type', '').split(';', 1)[0].strip().casefold`, `self.rfile.read`, `self.rfile.read(length).decode`

</details>

<a id="fn-ccs-web_console-_ConsoleHandler-do_POST"></a>
### `_ConsoleHandler.do_POST`

**메서드** · [정의 위치 L1060](../../src/ccs/web_console.py#L1060)

```python
_ConsoleHandler.do_POST(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`isinstance`, `route[0]`, `routes.get`, `self._error`, `self._json`, `self._parsed`, `self._read_payload`, `self.headers.get`, `str`

</details>

<a id="module-ccs-web_ui"></a>
## `ccs.web_ui`

[소스 파일](../../src/ccs/web_ui.py) · [이 폴더 설명](../../src/ccs/README.md)

> 소스의 모듈 설명: Presentation-focused three-tab NetOps console.

<a id="fn-ccs-web_ui-document"></a>
### `document`

**함수** · [정의 위치 L7](../../src/ccs/web_ui.py#L7)

```python
document() -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-tests-__init__"></a>
## `tests.__init__`

[소스 파일](../../tests/__init__.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Test helpers package; gives test modules stable local imports.

이 파일에는 Python 함수/클래스 정의가 없습니다. 패키지 초기화, 실행 진입점 또는 데이터/화면 문자열을 담는 파일이며 역할은 폴더 README에서 설명합니다.

<a id="module-tests-support_paths"></a>
## `tests.support_paths`

[소스 파일](../../tests/support_paths.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Isolated output paths and config fixtures for filesystem-writing tests.

<a id="fn-tests-support_paths-work_root"></a>
### `work_root`

**함수** · [정의 위치 L11](../../tests/support_paths.py#L11)

```python
work_root(*, legacy_env: str | None=None) -> Path
```

> Return the selected test-output root, creating it outside the repository.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(configured).expanduser`, `os.environ.get`, `root.mkdir`, `root.resolve`, `tempfile.gettempdir`

</details>

<a id="fn-tests-support_paths-workspace_for"></a>
### `workspace_for`

**함수** · [정의 위치 L22](../../tests/support_paths.py#L22)

```python
workspace_for(module_name: str, *, legacy_env: str | None=None) -> Path
```

> Create and return one module-specific directory under the selected root.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `ValueError`, `isinstance`, `work_root`, `workspace.mkdir`, `workspace.resolve`

</details>

<a id="fn-tests-support_paths-isolated_ai_config"></a>
### `isolated_ai_config`

**함수** · [정의 위치 L39](../../tests/support_paths.py#L39)

```python
isolated_ai_config(module_name: str) -> Path
```

> Copy the public AI example with a cost ledger inside a module work folder.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(workspace / 'cost-ledger.sqlite').resolve`, `ET.parse`, `Path`, `Path(__file__).resolve`, `ValueError`, `budget.set`, `str`, `tree.getroot`, `tree.getroot().find`, `tree.write`, `workspace_for`

</details>

<a id="module-tests-test_activity"></a>
## `tests.test_activity`

[소스 파일](../../tests/test_activity.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_activity-run_dir"></a>
### `run_dir`

**함수** · [정의 위치 L22](../../tests/test_activity.py#L22)

```python
run_dir() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORKING_ROOT.mkdir`, `path.mkdir`, `shutil.rmtree`, `uuid.uuid4`

</details>

<a id="fn-tests-test_activity-_events"></a>
### `_events`

**함수** · [정의 위치 L32](../../tests/test_activity.py#L32)

```python
_events(path: Path) -> list[dict]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.loads`, `path.read_text`, `path.read_text(encoding='utf-8').splitlines`

</details>

<a id="fn-tests-test_activity-test_activity_log_flushes_schema_pairs_operations_and_resumes"></a>
### `test_activity_log_flushes_schema_pairs_operations_and_resumes`

**함수** · [정의 위치 L36](../../tests/test_activity.py#L36)

```python
test_activity_log_flushes_schema_pairs_operations_and_resumes(run_dir: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ActivityLog`, `_events`, `activity.emit`, `all`, `event.keys`, `resumed.emit`

</details>

<a id="fn-tests-test_activity-test_activity_log_scrubs_entire_record_and_explicit_secrets"></a>
### `test_activity_log_scrubs_entire_record_and_explicit_secrets`

**함수** · [정의 위치 L82](../../tests/test_activity.py#L82)

```python
test_activity_log_scrubs_entire_record_and_explicit_secrets(run_dir: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ActivityLog`, `activity.emit`, `activity.shard_path.read_text`, `json.loads`

</details>

<a id="fn-tests-test_activity-test_activity_for_episode_derives_run_and_collision_free_writer"></a>
### `test_activity_for_episode_derives_run_and_collision_free_writer`

**함수** · [정의 위치 L109](../../tests/test_activity.py#L109)

```python
test_activity_for_episode_derives_run_and_collision_free_writer(run_dir: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_events`, `activity.emit`, `activity_for_episode`, `episode_dir.mkdir`

</details>

<a id="fn-tests-test_activity-test_instrumented_tools_records_list_call_arguments_results_and_duration"></a>
### `test_instrumented_tools_records_list_call_arguments_results_and_duration`

**비동기 함수** · [정의 위치 L121](../../tests/test_activity.py#L121)

```python
async test_instrumented_tools_records_list_call_arguments_results_and_duration(run_dir: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'episodes' / episode).mkdir`, `EventBus`, `FakeClient`, `Gateway`, `InstrumentedTools`, `_events`, `tools.call`, `tools.list_tools`

</details>

<a id="class-tests-test_activity-test_instrumented_tools_records_list_call_arguments_results_and_duration-FakeClient"></a>
### `test_instrumented_tools_records_list_call_arguments_results_and_duration.FakeClient`

**클래스** · [정의 위치 L136](../../tests/test_activity.py#L136)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_activity-test_instrumented_tools_records_list_call_arguments_results_and_duration-FakeClient-list_tools"></a>
### `test_instrumented_tools_records_list_call_arguments_results_and_duration.FakeClient.list_tools`

**비동기 메서드 (중첩 handler)** · [정의 위치 L137](../../tests/test_activity.py#L137)

```python
async test_instrumented_tools_records_list_call_arguments_results_and_duration.FakeClient.list_tools(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_activity-test_instrumented_tools_records_list_call_arguments_results_and_duration-FakeClient-call"></a>
### `test_instrumented_tools_records_list_call_arguments_results_and_duration.FakeClient.call`

**비동기 메서드 (중첩 handler)** · [정의 위치 L140](../../tests/test_activity.py#L140)

```python
async test_instrumented_tools_records_list_call_arguments_results_and_duration.FakeClient.call(self, name, arguments, metadata)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-tests-test_backend"></a>
## `tests.test_backend`

[소스 파일](../../tests/test_backend.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_backend-_world"></a>
### `_world`

**함수** · [정의 위치 L17](../../tests/test_backend.py#L17)

```python
_world(name: str, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`create_world`

</details>

<a id="fn-tests-test_backend-_apply"></a>
### `_apply`

**함수** · [정의 위치 L21](../../tests/test_backend.py#L21)

```python
_apply(backend: SQLiteBackend, change: dict, key: str='apply-once') -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`backend.call`

</details>

<a id="fn-tests-test_backend-test_backend_identity_rejects_legacy_database"></a>
### `test_backend_identity_rejects_legacy_database`

**함수** · [정의 위치 L25](../../tests/test_backend.py#L25)

```python
test_backend_identity_rejects_legacy_database()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `db.close`, `db.commit`, `db.execute`, `db.executemany`, `legacy.exists`, `legacy.unlink`, `pytest.raises`, `sqlite3.connect`

</details>

<a id="fn-tests-test_backend-test_role_contract_and_wired_read_surface"></a>
### `test_role_contract_and_wired_read_surface`

**함수** · [정의 위치 L34](../../tests/test_backend.py#L34)

```python
test_role_contract_and_wired_read_surface()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_world`, `all`, `backend.call`, `backend.snapshot`, `json.dumps`, `pytest.raises`, `set`, `snapshot.keys`, `tool_schemas`

</details>

<a id="fn-tests-test_backend-test_all_wired_scenarios_recover_or_noop"></a>
### `test_all_wired_scenarios_recover_or_noop`

**함수** · [정의 위치 L59](../../tests/test_backend.py#L59)

```python
test_all_wired_scenarios_recover_or_noop(fault_id: str)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_apply`, `_world`, `backend.call`, `evaluate`, `pytest.mark.parametrize`

</details>

<a id="fn-tests-test_backend-test_w1_reroutes_around_failed_switch_without_changing_ordinary_reference"></a>
### `test_w1_reroutes_around_failed_switch_without_changing_ordinary_reference`

**함수** · [정의 위치 L73](../../tests/test_backend.py#L73)

```python
test_w1_reroutes_around_failed_switch_without_changing_ordinary_reference()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_apply`, `_world`, `backend.call`, `backend.snapshot`, `next`

</details>

<a id="fn-tests-test_backend-test_preview_version_idempotency_rollback_and_verification_contract"></a>
### `test_preview_version_idempotency_rollback_and_verification_contract`

**함수** · [정의 위치 L87](../../tests/test_backend.py#L87)

```python
test_preview_version_idempotency_rollback_and_verification_contract()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_world`, `backend.call`, `pytest.raises`

</details>

<a id="fn-tests-test_backend-test_kpi_names_and_scenario_labels_are_exact"></a>
### `test_kpi_names_and_scenario_labels_are_exact`

**함수** · [정의 위치 L105](../../tests/test_backend.py#L105)

```python
test_kpi_names_and_scenario_labels_are_exact()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FAULTS.items`, `SQLiteBackend`, `_world`, `backend.call`

</details>

<a id="fn-tests-test_backend-test_operator_requests_describe_user_symptoms_without_revealing_causes"></a>
### `test_operator_requests_describe_user_symptoms_without_revealing_causes`

**함수** · [정의 위치 L117](../../tests/test_backend.py#L117)

```python
test_operator_requests_describe_user_symptoms_without_revealing_causes()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_world`, `any`, `expected_phrases.items`, `scenario['request'].lower`

</details>

<a id="fn-tests-test_backend-test_tc_faults_mutate_both_real_host_egress_links_and_apply_rollback_in_sync"></a>
### `test_tc_faults_mutate_both_real_host_egress_links_and_apply_rollback_in_sync`

**함수** · [정의 위치 L138](../../tests/test_backend.py#L138)

```python
test_tc_faults_mutate_both_real_host_egress_links_and_apply_rollback_in_sync(fault_id: str, config_param: str, link_field: str, injected: float, restored: float)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_apply`, `_world`, `all`, `backend.call`, `backend.snapshot`, `len`, `next`, `pytest.mark.parametrize`

</details>

<a id="fn-tests-test_backend-test_l3_world_references_only_existing_nodes_interfaces_and_targets"></a>
### `test_l3_world_references_only_existing_nodes_interfaces_and_targets`

**함수** · [정의 위치 L162](../../tests/test_backend.py#L162)

```python
test_l3_world_references_only_existing_nodes_interfaces_and_targets(fault_id: str)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SQLiteBackend`, `_world`, `all`, `backend.snapshot`, `db.close`, `db.execute`, `pytest.mark.parametrize`, `sqlite3.connect`

</details>

<a id="module-tests-test_config_budget"></a>
## `tests.test_config_budget`

[소스 파일](../../tests/test_config_budget.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_config_budget-fresh"></a>
### `fresh`

**함수** · [정의 위치 L15](../../tests/test_config_budget.py#L15)

```python
fresh()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`p.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_config_budget-test_xml_profiles_and_secret_free_export"></a>
### `test_xml_profiles_and_secret_free_export`

**함수** · [정의 위치 L18](../../tests/test_config_budget.py#L18)

```python
test_xml_profiles_and_secret_free_export()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Decimal`, `cfg.profile`, `cfg.public`, `json.dumps`, `load_ai`, `load_system`, `repr`, `token_cost`

</details>

<a id="fn-tests-test_config_budget-test_bad_ai_fields_fail_without_secret_values"></a>
### `test_bad_ai_fields_fail_without_secret_values`

**함수** · [정의 위치 L37](../../tests/test_config_budget.py#L37)

```python
test_bad_ai_fields_fail_without_secret_values(replacement)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(PROJECT / 'configs/ai.example.xml').read_text`, `(PROJECT / 'configs/ai.example.xml').read_text(encoding='utf-8-sig').replace`, `(PROJECT / 'configs/ai.example.xml').read_text(encoding='utf-8-sig').replace(*replacement).replace`, `fresh`, `load_ai`, `p.write_text`, `pytest.mark.parametrize`, `pytest.raises`, `str`

</details>

<a id="fn-tests-test_config_budget-test_xml_external_entity_rejected"></a>
### `test_xml_external_entity_rejected`

**함수** · [정의 위치 L43](../../tests/test_config_budget.py#L43)

```python
test_xml_external_entity_rejected()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`fresh`, `load_ai`, `p.write_text`, `pytest.raises`

</details>

<a id="fn-tests-test_config_budget-test_luna_cache_reads_and_writes_are_disjoint_billing_categories"></a>
### `test_luna_cache_reads_and_writes_are_disjoint_billing_categories`

**함수** · [정의 위치 L48](../../tests/test_config_budget.py#L48)

```python
test_luna_cache_reads_and_writes_are_disjoint_billing_categories()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Decimal`, `load_ai`, `load_ai(PROJECT / 'configs/ai.example.xml').profile`, `pytest.raises`, `token_cost`

</details>

<a id="fn-tests-test_config_budget-test_ai_typos_and_duplicate_sections_fail"></a>
### `test_ai_typos_and_duplicate_sections_fail`

**함수** · [정의 위치 L61](../../tests/test_config_budget.py#L61)

```python
test_ai_typos_and_duplicate_sections_fail(old, new)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(PROJECT / 'configs/ai.example.xml').read_text`, `(PROJECT / 'configs/ai.example.xml').read_text(encoding='utf-8-sig').replace`, `fresh`, `load_ai`, `p.write_text`, `pytest.mark.parametrize`, `pytest.raises`

</details>

<a id="fn-tests-test_config_budget-test_system_typos_and_duplicate_sections_fail"></a>
### `test_system_typos_and_duplicate_sections_fail`

**함수** · [정의 위치 L70](../../tests/test_config_budget.py#L70)

```python
test_system_typos_and_duplicate_sections_fail(old, new)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(PROJECT / 'configs/system.example.xml').read_text`, `(PROJECT / 'configs/system.example.xml').read_text(encoding='utf-8-sig').replace`, `fresh`, `load_system`, `p.write_text`, `pytest.mark.parametrize`, `pytest.raises`

</details>

<a id="fn-tests-test_config_budget-test_atomic_reservations_and_restart_retention"></a>
### `test_atomic_reservations_and_restart_retention`

**함수** · [정의 위치 L74](../../tests/test_config_budget.py#L74)

```python
test_atomic_reservations_and_restart_retention()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetLedger`, `BudgetLedger(path, Decimal('1')).summary`, `Decimal`, `ThreadPoolExecutor`, `fresh`, `ledger.reserve`, `ledger.settle`, `len`, `list`, `pool.map`, `pytest.raises`, `range`

</details>

<a id="fn-tests-test_config_budget-test_atomic_reservations_and_restart_retention-reserve"></a>
### `test_atomic_reservations_and_restart_retention.reserve`

**함수 (중첩 handler)** · [정의 위치 L77](../../tests/test_config_budget.py#L77)

```python
test_atomic_reservations_and_restart_retention.reserve(_)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetLedger`, `BudgetLedger(path, Decimal('1')).reserve`, `Decimal`

</details>

<a id="fn-tests-test_config_budget-test_failed_no_charge_request_releases_reservation"></a>
### `test_failed_no_charge_request_releases_reservation`

**함수** · [정의 위치 L89](../../tests/test_config_budget.py#L89)

```python
test_failed_no_charge_request_releases_reservation()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetLedger`, `Decimal`, `fresh`, `ledger.reserve`, `ledger.settle`, `ledger.summary`

</details>

<a id="module-tests-test_event_communication"></a>
## `tests.test_event_communication`

[소스 파일](../../tests/test_event_communication.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_event_communication-event"></a>
### `event`

**함수** · [정의 위치 L4](../../tests/test_event_communication.py#L4)

```python
event(component, action, status='started', **details)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_normalize_event`

</details>

<a id="fn-tests-test_event_communication-comm"></a>
### `comm`

**함수** · [정의 위치 L9](../../tests/test_event_communication.py#L9)

```python
comm(record)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_event_communication-test_handoff_shows_actual_fields_and_values_without_credentials"></a>
### `test_handoff_shows_actual_fields_and_values_without_credentials`

**함수** · [정의 위치 L13](../../tests/test_event_communication.py#L13)

```python
test_handoff_shows_actual_fields_and_values_without_credentials()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comm`, `event`, `str`

</details>

<a id="fn-tests-test_event_communication-test_response_and_client_server_mcp_directions_are_distinct"></a>
### `test_response_and_client_server_mcp_directions_are_distinct`

**함수** · [정의 위치 L31](../../tests/test_event_communication.py#L31)

```python
test_response_and_client_server_mcp_directions_are_distinct()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comm`, `event`

</details>

<a id="fn-tests-test_event_communication-test_failed_transport_is_not_claimed_to_be_a_response"></a>
### `test_failed_transport_is_not_claimed_to_be_a_response`

**함수** · [정의 위치 L44](../../tests/test_event_communication.py#L44)

```python
test_failed_transport_is_not_claimed_to_be_a_response()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comm`, `event`

</details>

<a id="fn-tests-test_event_communication-test_model_copy_has_no_removed_notice_and_keeps_scrubbing"></a>
### `test_model_copy_has_no_removed_notice_and_keeps_scrubbing`

**함수** · [정의 위치 L52](../../tests/test_event_communication.py#L52)

```python
test_model_copy_has_no_removed_notice_and_keeps_scrubbing()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comm`, `event`, `str`

</details>

<a id="fn-tests-test_event_communication-test_internal_stage_and_disabled_retrieval_do_not_invent_communication"></a>
### `test_internal_stage_and_disabled_retrieval_do_not_invent_communication`

**함수** · [정의 위치 L63](../../tests/test_event_communication.py#L63)

```python
test_internal_stage_and_disabled_retrieval_do_not_invent_communication()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comm`, `event`

</details>

<a id="module-tests-test_event_presentation"></a>
## `tests.test_event_presentation`

[소스 파일](../../tests/test_event_presentation.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_event_presentation-_event"></a>
### `_event`

**함수** · [정의 위치 L8](../../tests/test_event_presentation.py#L8)

```python
_event(component: str, action: str, status: str='started', *, details: dict[str, object] | None=None, writer_id: str='operation') -> dict[str, object]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_event_presentation-test_maps_workflow_phases_to_stable_routes_and_submodules"></a>
### `test_maps_workflow_phases_to_stable_routes_and_submodules`

**함수** · [정의 위치 L40](../../tests/test_event_presentation.py#L40)

```python
test_maps_workflow_phases_to_stable_routes_and_submodules(event: dict[str, object], route: str, node: str, submodule: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `presentation_for_event`, `pytest.mark.parametrize`

</details>

<a id="fn-tests-test_event_presentation-test_mcp_role_and_tool_choose_direction_without_changing_failure_channel"></a>
### `test_mcp_role_and_tool_choose_direction_without_changing_failure_channel`

**함수** · [정의 위치 L66](../../tests/test_event_presentation.py#L66)

```python
test_mcp_role_and_tool_choose_direction_without_changing_failure_channel(role_field: str, role: str, tool: str, route: str, submodule: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `presentation_for_event`, `pytest.mark.parametrize`

</details>

<a id="fn-tests-test_event_presentation-test_result_count_is_concrete_and_unknown_event_uses_explicit_generic_copy"></a>
### `test_result_count_is_concrete_and_unknown_event_uses_explicit_generic_copy`

**함수** · [정의 위치 L92](../../tests/test_event_presentation.py#L92)

```python
test_result_count_is_concrete_and_unknown_event_uses_explicit_generic_copy() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `presentation_for_event`

</details>

<a id="fn-tests-test_event_presentation-test_progress_copy_is_status_aware_and_keeps_literal_query_out_of_primary_log"></a>
### `test_progress_copy_is_status_aware_and_keeps_literal_query_out_of_primary_log`

**함수** · [정의 위치 L110](../../tests/test_event_presentation.py#L110)

```python
test_progress_copy_is_status_aware_and_keeps_literal_query_out_of_primary_log() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `presentation_for_event`

</details>

<a id="fn-tests-test_event_presentation-test_runner_container_events_remain_visible_but_never_drive_active_glow"></a>
### `test_runner_container_events_remain_visible_but_never_drive_active_glow`

**함수** · [정의 위치 L133](../../tests/test_event_presentation.py#L133)

```python
test_runner_container_events_remain_visible_but_never_drive_active_glow(action: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `presentation_for_event`, `pytest.mark.parametrize`

</details>

<a id="module-tests-test_instrumentation"></a>
## `tests.test_instrumentation`

[소스 파일](../../tests/test_instrumentation.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_instrumentation-working_case"></a>
### `working_case`

**함수** · [정의 위치 L25](../../tests/test_instrumentation.py#L25)

```python
working_case() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORKING_ROOT.mkdir`, `path.mkdir`, `shutil.rmtree`, `uuid.uuid4`

</details>

<a id="fn-tests-test_instrumentation-test_null_gateway_preserves_identity_and_records_all_boundaries"></a>
### `test_null_gateway_preserves_identity_and_records_all_boundaries`

**함수** · [정의 위치 L35](../../tests/test_instrumentation.py#L35)

```python
test_null_gateway_preserves_identity_and_records_all_boundaries(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(working_case / 'blobs').glob`, `EventBus`, `Gateway`, `gateway.pass_through`, `len`, `list`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_merge_obeys_cross_writer_causation_before_logical_tiebreakers"></a>
### `test_merge_obeys_cross_writer_causation_before_logical_tiebreakers`

**함수** · [정의 위치 L53](../../tests/test_instrumentation.py#L53)

```python
test_merge_obeys_cross_writer_causation_before_logical_tiebreakers(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `Path`, `Path(result['merged_path']).read_text`, `Path(result['merged_path']).read_text(encoding='utf-8').splitlines`, `diagnosis.emit`, `json.loads`, `runner.emit`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_numbered_episode_sequence_is_consistent_across_process_writers"></a>
### `test_numbered_episode_sequence_is_consistent_across_process_writers`

**함수** · [정의 위치 L80](../../tests/test_instrumentation.py#L80)

```python
test_numbered_episode_sequence_is_consistent_across_process_writers(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `Path`, `Path(result['merged_path']).read_text`, `Path(result['merged_path']).read_text(encoding='utf-8').splitlines`, `child.emit`, `json.loads`, `runner.emit`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_integrity_rejects_missing_or_corrupt_payload_blob"></a>
### `test_integrity_rejects_missing_or_corrupt_payload_blob`

**함수** · [정의 위치 L97](../../tests/test_instrumentation.py#L97)

```python
test_integrity_rejects_missing_or_corrupt_payload_blob(working_case: Path, damage: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `any`, `blob.unlink`, `blob.write_text`, `bus.emit`, `pytest.mark.parametrize`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_terminal_episode_rejects_duplicate_causal_returns"></a>
### `test_terminal_episode_rejects_duplicate_causal_returns`

**함수** · [정의 위치 L112](../../tests/test_instrumentation.py#L112)

```python
test_terminal_episode_rejects_duplicate_causal_returns(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(working_case / 'manifest.json').write_text`, `EventBus`, `any`, `caller.emit`, `json.dumps`, `server.emit`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_explicit_duplicate_delivery_does_not_count_as_second_return"></a>
### `test_explicit_duplicate_delivery_does_not_count_as_second_return`

**함수** · [정의 위치 L137](../../tests/test_instrumentation.py#L137)

```python
test_explicit_duplicate_delivery_does_not_count_as_second_return(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(working_case / 'manifest.json').write_text`, `EventBus`, `caller.emit`, `json.dumps`, `server.emit`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_incomplete_pair_is_valid_in_flight_but_invalid_when_terminal"></a>
### `test_incomplete_pair_is_valid_in_flight_but_invalid_when_terminal`

**함수** · [정의 위치 L168](../../tests/test_instrumentation.py#L168)

```python
test_incomplete_pair_is_valid_in_flight_but_invalid_when_terminal(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(working_case / 'manifest.json').write_text`, `EventBus`, `any`, `bus.emit`, `json.dumps`, `validate_and_merge`

</details>

<a id="fn-tests-test_instrumentation-test_runbook_bm25_handles_fault_queries_and_untrusted_query_syntax"></a>
### `test_runbook_bm25_handles_fault_queries_and_untrusted_query_syntax`

**함수** · [정의 위치 L181](../../tests/test_instrumentation.py#L181)

```python
test_runbook_bm25_handles_fault_queries_and_untrusted_query_syntax(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RunbookStore`, `any`, `isinstance`, `pytest.raises`, `result['doc_id'].startswith`, `store.search`

</details>

<a id="fn-tests-test_instrumentation-_memory_record"></a>
### `_memory_record`

**함수** · [정의 위치 L196](../../tests/test_instrumentation.py#L196)

```python
_memory_record(record_id: str='memory-1') -> MemoryRecord
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MemoryRecord`

</details>

<a id="fn-tests-test_instrumentation-test_memory_requires_both_approval_and_verification_then_reuses_across_episode"></a>
### `test_memory_requires_both_approval_and_verification_then_reuses_across_episode`

**함수** · [정의 위치 L216](../../tests/test_instrumentation.py#L216)

```python
test_memory_requires_both_approval_and_verification_then_reuses_across_episode(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MemoryStore`, `_memory_record`, `_memory_record('memory-2').model_dump`, `pytest.raises`, `store.search`, `store.write`

</details>

<a id="fn-tests-test_instrumentation-test_offline_ledger_normalizes_values_and_never_returns_registry_plaintext"></a>
### `test_offline_ledger_normalizes_values_and_never_returns_registry_plaintext`

**함수** · [정의 위치 L239](../../tests/test_instrumentation.py#L239)

```python
test_offline_ledger_normalizes_values_and_never_returns_registry_plaintext(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `build_ledger`, `bus.emit`, `json.dumps`

</details>

<a id="fn-tests-test_instrumentation-test_ledger_separates_seed_bindings_and_marks_cross_episode_visits"></a>
### `test_ledger_separates_seed_bindings_and_marks_cross_episode_visits`

**함수** · [정의 위치 L275](../../tests/test_instrumentation.py#L275)

```python
test_ledger_separates_seed_bindings_and_marks_cross_episode_visits(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `build_ledger`, `bus.emit`, `dict`, `len`, `pytest.raises`

</details>

<a id="fn-tests-test_instrumentation-test_ledger_matcher_has_perfect_precision_recall_on_labeled_normalization_cases"></a>
### `test_ledger_matcher_has_perfect_precision_recall_on_labeled_normalization_cases`

**함수** · [정의 위치 L328](../../tests/test_instrumentation.py#L328)

```python
test_ledger_matcher_has_perfect_precision_recall_on_labeled_normalization_cases(working_case: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`EventBus`, `build_ledger`, `bus.emit`, `len`

</details>

<a id="module-tests-test_monitor"></a>
## `tests.test_monitor`

[소스 파일](../../tests/test_monitor.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_monitor-_event"></a>
### `_event`

**함수** · [정의 위치 L16](../../tests/test_monitor.py#L16)

```python
_event(event_id: str, *, ts: str, seq: int, status: str='info', details: object | None=None) -> dict[str, object]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_monitor-_write_manifest"></a>
### `_write_manifest`

**함수** · [정의 위치 L41](../../tests/test_monitor.py#L41)

```python
_write_manifest(run_dir: Path, *, status: str='RUNNING') -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `datetime.now`, `datetime.now(timezone.utc).isoformat`, `json.dumps`

</details>

<a id="fn-tests-test_monitor-_api_url"></a>
### `_api_url`

**함수** · [정의 위치 L61](../../tests/test_monitor.py#L61)

```python
_api_url(server: DashboardServer, cursor: str='') -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`parse_qs`, `urlencode`, `urlsplit`

</details>

<a id="fn-tests-test_monitor-test_read_activity_sorts_complete_lines_and_redacts_prohibited_detail"></a>
### `test_read_activity_sorts_complete_lines_and_redacts_prohibited_detail`

**함수** · [정의 위치 L70](../../tests/test_monitor.py#L70)

```python
test_read_activity_sorts_complete_lines_and_redacts_prohibited_detail(tmp_path: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(json.dumps(later) + '\n' + json.dumps(earlier) + '\n' + json.dumps(partial)[:25]).encode`, `_event`, `activity.mkdir`, `json.dumps`, `read_activity`, `shard.write_bytes`

</details>

<a id="fn-tests-test_monitor-test_dashboard_cursor_revisits_partial_line_and_rejects_other_paths"></a>
### `test_dashboard_cursor_revisits_partial_line_and_rejects_other_paths`

**함수** · [정의 위치 L103](../../tests/test_monitor.py#L103)

```python
test_dashboard_cursor_revisits_partial_line_and_rejects_other_paths(tmp_path: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(activity / 'diagnosis.jsonl').write_text`, `DashboardServer`, `DashboardServer(run_dir).start`, `_api_url`, `_event`, `_write_manifest`, `activity.mkdir`, `json.dumps`, `json.load`, `len`, `parse_qs`, `pytest.raises`, `response.headers.get`, `response.read`, `response.read().decode`, `shard.open`, `shard.write_text`, `stream.write`, `urlencode`, `urlopen`, `urlsplit`

</details>

<a id="fn-tests-test_monitor-test_dashboard_only_supports_read_methods"></a>
### `test_dashboard_only_supports_read_methods`

**함수** · [정의 위치 L150](../../tests/test_monitor.py#L150)

```python
test_dashboard_only_supports_read_methods(tmp_path: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`DashboardServer`, `DashboardServer(run_dir).start`, `HTTPConnection`, `_write_manifest`, `connection.close`, `connection.getresponse`, `connection.request`, `response.read`, `run_dir.mkdir`, `urlsplit`

</details>

<a id="fn-tests-test_monitor-test_snapshot_is_standalone_and_script_payload_is_escaped"></a>
### `test_snapshot_is_standalone_and_script_payload_is_escaped`

**함수** · [정의 위치 L164](../../tests/test_monitor.py#L164)

```python
test_snapshot_is_standalone_and_script_payload_is_escaped(tmp_path: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(activity / 'operation.jsonl').write_text`, `(run_dir / 'ai.local.xml').write_text`, `(run_dir / 'summary.json').write_text`, `_event`, `_write_manifest`, `activity.mkdir`, `json.dumps`, `output.read_text`, `write_snapshot`

</details>

<a id="fn-tests-test_monitor-test_snapshot_marks_old_run_without_activity"></a>
### `test_snapshot_marks_old_run_without_activity`

**함수** · [정의 위치 L215](../../tests/test_monitor.py#L215)

```python
test_snapshot_marks_old_run_without_activity(tmp_path: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_write_manifest`, `output.read_text`, `run_dir.mkdir`, `write_snapshot`

</details>

<a id="fn-tests-test_monitor-test_normalized_event_adds_safe_bilingual_presentation_after_redaction"></a>
### `test_normalized_event_adds_safe_bilingual_presentation_after_redaction`

**함수** · [정의 위치 L227](../../tests/test_monitor.py#L227)

```python
test_normalized_event_adds_safe_bilingual_presentation_after_redaction() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_event`, `_normalize_event`, `json.dumps`

</details>

<a id="fn-tests-test_monitor-test_document_is_white_large_topology_and_embedded_height_aware"></a>
### `test_document_is_white_large_topology_and_embedded_height_aware`

**함수** · [정의 위치 L253](../../tests/test_monitor.py#L253)

```python
test_document_is_white_large_topology_and_embedded_height_aware() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_document`

</details>

<a id="module-tests-test_network_view"></a>
## `tests.test_network_view`

[소스 파일](../../tests/test_network_view.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_network_view-_assert_safe_working_directory"></a>
### `_assert_safe_working_directory`

**함수** · [정의 위치 L17](../../tests/test_network_view.py#L17)

```python
_assert_safe_working_directory() -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORK.resolve`, `work_root`, `work_root().resolve`

</details>

<a id="fn-tests-test_network_view-clean_working_directory"></a>
### `clean_working_directory`

**함수** · [정의 위치 L25](../../tests/test_network_view.py#L25)

```python
clean_working_directory()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORK.exists`, `WORK.mkdir`, `_assert_safe_working_directory`, `pytest.fixture`, `shutil.rmtree`

</details>

<a id="fn-tests-test_network_view-_file_evidence"></a>
### `_file_evidence`

**함수** · [정의 위치 L36](../../tests/test_network_view.py#L36)

```python
_file_evidence(root: Path) -> dict[str, tuple[str, int, int]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`hashlib.sha256`, `hashlib.sha256(path.read_bytes()).hexdigest`, `path.is_file`, `path.read_bytes`, `path.relative_to`, `path.stat`, `root.rglob`, `sorted`, `str`

</details>

<a id="fn-tests-test_network_view-_configuration"></a>
### `_configuration`

**함수** · [정의 위치 L48](../../tests/test_network_view.py#L48)

```python
_configuration(state: dict, param: str) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`next`

</details>

<a id="fn-tests-test_network_view-_kpi"></a>
### `_kpi`

**함수** · [정의 위치 L56](../../tests/test_network_view.py#L56)

```python
_kpi(state: dict, metric: str) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`next`

</details>

<a id="fn-tests-test_network_view-test_preview_projects_each_wired_world"></a>
### `test_preview_projects_each_wired_world`

**함수** · [정의 위치 L71](../../tests/test_network_view.py#L71)

```python
test_preview_projects_each_wired_world(fault: str, changed_param: str | None, value: object, reference: object, degraded_metrics: set[str]) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_configuration`, `all`, `json.dumps`, `preview_network`, `pytest.mark.parametrize`, `set`

</details>

<a id="fn-tests-test_network_view-test_preview_cache_is_immutable"></a>
### `test_preview_cache_is_immutable`

**함수** · [정의 위치 L109](../../tests/test_network_view.py#L109)

```python
test_preview_cache_is_immutable() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_file_evidence`, `preview_network`

</details>

<a id="fn-tests-test_network_view-test_run_view_tracks_w1_reroute_and_never_mutates_run_files"></a>
### `test_run_view_tracks_w1_reroute_and_never_mutates_run_files`

**함수** · [정의 위치 L117](../../tests/test_network_view.py#L117)

```python
test_run_view_tracks_w1_reroute_and_never_mutates_run_files() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(episode_dir / 'final-state.restricted.json').write_text`, `(episode_dir / 'scenario.restricted.json').write_text`, `(run_dir / 'manifest.json').write_text`, `SQLiteBackend`, `_configuration`, `_file_evidence`, `_kpi`, `all`, `backend.call`, `backend.snapshot`, `create_world`, `episode_dir.glob`, `episode_dir.mkdir`, `json.dumps`, `list`, `next`, `read_network`

</details>

<a id="fn-tests-test_network_view-test_mismatched_final_snapshot_is_not_projected"></a>
### `test_mismatched_final_snapshot_is_not_projected`

**함수** · [정의 위치 L200](../../tests/test_network_view.py#L200)

```python
test_mismatched_final_snapshot_is_not_projected() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(episode_dir / 'final-state.restricted.json').write_text`, `(episode_dir / 'scenario.restricted.json').write_text`, `(run_dir / 'manifest.json').write_text`, `SQLiteBackend`, `backend.snapshot`, `create_world`, `episode_dir.mkdir`, `json.dumps`, `read_network`

</details>

<a id="fn-tests-test_network_view-test_pending_episode_is_unavailable_and_inputs_reject_traversal"></a>
### `test_pending_episode_is_unavailable_and_inputs_reject_traversal`

**함수** · [정의 위치 L219](../../tests/test_network_view.py#L219)

```python
test_pending_episode_is_unavailable_and_inputs_reject_traversal() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'episodes' / 'episode-0001').mkdir`, `(run_dir / 'manifest.json').write_text`, `json.dumps`, `preview_network`, `pytest.raises`, `read_network`

</details>

<a id="module-tests-test_observability_e2e"></a>
## `tests.test_observability_e2e`

[소스 파일](../../tests/test_observability_e2e.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Observe real child processes without any paid model request.

<a id="fn-tests-test_observability_e2e-test_activity_spans_real_memory_chain_and_is_sealed"></a>
### `test_activity_spans_real_memory_chain_and_is_sealed`

**비동기 함수** · [정의 위치 L19](../../tests/test_observability_e2e.py#L19)

```python
async test_activity_spans_real_memory_chain_and_is_sealed()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').read_text`, `(run_dir / 'monitor.html').is_file`, `any`, `directory.mkdir`, `json.dumps`, `json.loads`, `k.startswith`, `len`, `next`, `read_activity`, `run`, `uuid.uuid4`, `verify_seal`

</details>

<a id="fn-tests-test_observability_e2e-test_activity_spans_real_memory_chain_and_is_sealed-created"></a>
### `test_activity_spans_real_memory_chain_and_is_sealed.created`

**함수 (중첩 handler)** · [정의 위치 L24](../../tests/test_observability_e2e.py#L24)

```python
test_activity_spans_real_memory_chain_and_is_sealed.created(path)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(path / 'manifest.json').read_text`, `json.loads`, `observed_before_completion.extend`, `read_activity`

</details>

<a id="fn-tests-test_observability_e2e-test_observed_failure_is_terminal_and_memory_is_not_saved"></a>
### `test_observed_failure_is_terminal_and_memory_is_not_saved`

**비동기 함수** · [정의 위치 L58](../../tests/test_observability_e2e.py#L58)

```python
async test_observed_failure_is_terminal_and_memory_is_not_saved()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'monitor.html').is_file`, `ET.parse`, `any`, `directory.mkdir`, `read_activity`, `run`, `tree.find`, `tree.find('workflow').set`, `tree.write`, `uuid.uuid4`, `verify_seal`

</details>

<a id="module-tests-test_pacing"></a>
## `tests.test_pacing`

[소스 파일](../../tests/test_pacing.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_pacing-work"></a>
### `work`

**함수** · [정의 위치 L28](../../tests/test_pacing.py#L28)

```python
work() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORK.mkdir`, `path.mkdir`, `shutil.rmtree`, `uuid.uuid4`

</details>

<a id="fn-tests-test_pacing-test_delay_rejects_out_of_range_and_nonfinite_values"></a>
### `test_delay_rejects_out_of_range_and_nonfinite_values`

**함수** · [정의 위치 L39](../../tests/test_pacing.py#L39)

```python
test_delay_rejects_out_of_range_and_nonfinite_values(value: float) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`pytest.mark.parametrize`, `pytest.raises`, `validate_delay`

</details>

<a id="fn-tests-test_pacing-test_delay_rejects_non_numeric_values"></a>
### `test_delay_rejects_non_numeric_values`

**함수** · [정의 위치 L45](../../tests/test_pacing.py#L45)

```python
test_delay_rejects_non_numeric_values(value: object) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`pytest.mark.parametrize`, `pytest.raises`, `validate_delay`

</details>

<a id="fn-tests-test_pacing-test_atomic_control_writers_keep_valid_monotonic_revisions"></a>
### `test_atomic_control_writers_keep_valid_monotonic_revisions`

**함수** · [정의 위치 L50](../../tests/test_pacing.py#L50)

```python
test_atomic_control_writers_keep_valid_monotonic_revisions(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(work / 'control.json.history').glob`, `all`, `item.read_text`, `json.loads`, `len`, `list`, `range`, `read_control`, `thread.is_alive`, `thread.join`, `thread.start`, `threading.Thread`, `write_control`

</details>

<a id="fn-tests-test_pacing-test_zero_delay_returns_immediately_without_timing_shard"></a>
### `test_zero_delay_returns_immediately_without_timing_shard`

**함수** · [정의 위치 L67](../../tests/test_pacing.py#L67)

```python
test_zero_delay_returns_immediately_without_timing_shard(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(work / 'pacing').exists`, `ActivityLog`, `ActivityLog(work, 'zero').emit`, `install_run_pointer`, `time.monotonic`, `write_control`

</details>

<a id="fn-tests-test_pacing-test_no_delay_change_releases_current_wait_and_records_union"></a>
### `test_no_delay_change_releases_current_wait_and_records_union`

**함수** · [정의 위치 L77](../../tests/test_pacing.py#L77)

```python
test_no_delay_change_releases_current_wait_and_records_union(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(work / 'activity' / 'dynamic.jsonl').is_file`, `(work / 'pacing-pointer.json').read_bytes`, `completed.is_set`, `install_run_pointer`, `summarize_timing`, `thread.join`, `thread.start`, `threading.Event`, `threading.Thread`, `time.monotonic`, `time.sleep`, `time.time_ns`, `write_control`

</details>

<a id="fn-tests-test_pacing-test_no_delay_change_releases_current_wait_and_records_union-emit"></a>
### `test_no_delay_change_releases_current_wait_and_records_union.emit`

**함수 (중첩 handler)** · [정의 위치 L85](../../tests/test_pacing.py#L85)

```python
test_no_delay_change_releases_current_wait_and_records_union.emit() -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ActivityLog`, `ActivityLog(work, 'dynamic').emit`, `completed.set`

</details>

<a id="module-tests-test_protocols"></a>
## `tests.test_protocols`

[소스 파일](../../tests/test_protocols.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_protocols-test_mcp_real_wire_enforces_role_schema_and_metadata"></a>
### `test_mcp_real_wire_enforces_role_schema_and_metadata`

**비동기 함수** · [정의 위치 L26](../../tests/test_protocols.py#L26)

```python
async test_mcp_real_wire_enforces_role_schema_and_metadata() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MCPClient`, `app.router.lifespan_context`, `build_mcp_app`, `diagnosis.call`, `diagnosis.list_tools`, `httpx2.ASGITransport`, `httpx2.AsyncClient`, `operation.call`, `operation.list_tools`, `pytest.raises`, `version`

</details>

<a id="fn-tests-test_protocols-test_mcp_real_wire_enforces_role_schema_and_metadata-handler"></a>
### `test_mcp_real_wire_enforces_role_schema_and_metadata.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L30](../../tests/test_protocols.py#L30)

```python
async test_mcp_real_wire_enforces_role_schema_and_metadata.handler(tool: str, arguments: dict, metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`calls.append`

</details>

<a id="fn-tests-test_protocols-test_mcp_bad_token_is_rejected_on_real_transport"></a>
### `test_mcp_bad_token_is_rejected_on_real_transport`

**비동기 함수** · [정의 위치 L106](../../tests/test_protocols.py#L106)

```python
async test_mcp_bad_token_is_rejected_on_real_transport() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`MCPClient`, `app.router.lifespan_context`, `build_mcp_app`, `client.list_tools`, `httpx2.ASGITransport`, `httpx2.AsyncClient`, `pytest.raises`

</details>

<a id="fn-tests-test_protocols-test_mcp_bad_token_is_rejected_on_real_transport-handler"></a>
### `test_mcp_bad_token_is_rejected_on_real_transport.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L107](../../tests/test_protocols.py#L107)

```python
async test_mcp_bad_token_is_rejected_on_real_transport.handler(_tool: str, _arguments: dict, _metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_protocols-_diagnosis_payload"></a>
### `_diagnosis_payload`

**함수** · [정의 위치 L128](../../tests/test_protocols.py#L128)

```python
_diagnosis_payload(*, idempotency_key: str='idem-1', target: str='HOST-001') -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_protocols-test_a2a_real_agent_card_task_lifecycle_and_idempotency"></a>
### `test_a2a_real_agent_card_task_lifecycle_and_idempotency`

**비동기 함수** · [정의 위치 L142](../../tests/test_protocols.py#L142)

```python
async test_a2a_real_agent_card_task_lifecycle_and_idempotency() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2AClient`, `_diagnosis_payload`, `build_a2a_app`, `card_response.json`, `client.diagnose`, `httpx.ASGITransport`, `httpx.AsyncClient`, `len`, `version`, `wire_client.get`

</details>

<a id="fn-tests-test_protocols-test_a2a_real_agent_card_task_lifecycle_and_idempotency-handler"></a>
### `test_a2a_real_agent_card_task_lifecycle_and_idempotency.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L146](../../tests/test_protocols.py#L146)

```python
async test_a2a_real_agent_card_task_lifecycle_and_idempotency.handler(payload: dict, metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`invocations.append`

</details>

<a id="fn-tests-test_protocols-test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire"></a>
### `test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire`

**비동기 함수** · [정의 위치 L191](../../tests/test_protocols.py#L191)

```python
async test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_diagnosis_payload`, `_send_raw_a2a`, `build_a2a_app`, `httpx.ASGITransport`, `httpx.AsyncClient`

</details>

<a id="fn-tests-test_protocols-test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire-handler"></a>
### `test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L194](../../tests/test_protocols.py#L194)

```python
async test_a2a_server_rejects_unknown_contract_fields_on_sdk_wire.handler(_payload: dict, _metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_protocols-test_a2a_rejects_idempotency_key_payload_mismatch"></a>
### `test_a2a_rejects_idempotency_key_payload_mismatch`

**비동기 함수** · [정의 위치 L220](../../tests/test_protocols.py#L220)

```python
async test_a2a_rejects_idempotency_key_payload_mismatch() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2AClient`, `_diagnosis_payload`, `build_a2a_app`, `client.diagnose`, `httpx.ASGITransport`, `httpx.AsyncClient`, `pytest.raises`

</details>

<a id="fn-tests-test_protocols-test_a2a_rejects_idempotency_key_payload_mismatch-handler"></a>
### `test_a2a_rejects_idempotency_key_payload_mismatch.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L221](../../tests/test_protocols.py#L221)

```python
async test_a2a_rejects_idempotency_key_payload_mismatch.handler(payload: dict, _metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_protocols-test_a2a_callback_timeout_reaches_failed_terminal_state"></a>
### `test_a2a_callback_timeout_reaches_failed_terminal_state`

**비동기 함수** · [정의 위치 L241](../../tests/test_protocols.py#L241)

```python
async test_a2a_callback_timeout_reaches_failed_terminal_state() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2AClient`, `_diagnosis_payload`, `build_a2a_app`, `client.diagnose`, `httpx.ASGITransport`, `httpx.AsyncClient`, `pytest.raises`

</details>

<a id="fn-tests-test_protocols-test_a2a_callback_timeout_reaches_failed_terminal_state-handler"></a>
### `test_a2a_callback_timeout_reaches_failed_terminal_state.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L242](../../tests/test_protocols.py#L242)

```python
async test_a2a_callback_timeout_reaches_failed_terminal_state.handler(_payload: dict, _metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.sleep`

</details>

<a id="fn-tests-test_protocols-test_a2a_bad_token_cannot_send_task"></a>
### `test_a2a_bad_token_cannot_send_task`

**비동기 함수** · [정의 위치 L265](../../tests/test_protocols.py#L265)

```python
async test_a2a_bad_token_cannot_send_task() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`A2AClient`, `_diagnosis_payload`, `build_a2a_app`, `client.diagnose`, `httpx.ASGITransport`, `httpx.AsyncClient`, `pytest.raises`

</details>

<a id="fn-tests-test_protocols-test_a2a_bad_token_cannot_send_task-handler"></a>
### `test_a2a_bad_token_cannot_send_task.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L266](../../tests/test_protocols.py#L266)

```python
async test_a2a_bad_token_cannot_send_task.handler(_payload: dict, _metadata: dict) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_protocols-_send_raw_a2a"></a>
### `_send_raw_a2a`

**비동기 함수** · [정의 위치 L283](../../tests/test_protocols.py#L283)

```python
async _send_raw_a2a(http_client: httpx.AsyncClient, payload: dict) -> Task
```

> Send a deliberately unvalidated payload through the pinned A2A SDK.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ClientCallContext`, `ClientConfig`, `ClientFactory`, `Message`, `SendMessageConfiguration`, `SendMessageRequest`, `client.send_message`, `factory.create_from_url`, `new_data_part`, `response.HasField`

</details>

<a id="module-tests-test_provider_contracts"></a>
## `tests.test_provider_contracts`

[소스 파일](../../tests/test_provider_contracts.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Offline native-SDK contract tests for the provider adapters.  Every HTTP request is intercepted by ``httpx2.MockTransport``. The credentials are explicit non-secret test sentinels loaded through a module-isolated copy of the public example configuration.

<a id="fn-tests-test_provider_contracts-fresh_config"></a>
### `fresh_config`

**함수** · [정의 위치 L39](../../tests/test_provider_contracts.py#L39)

```python
fresh_config()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(PROJECT / 'configs' / 'ai.example.xml').read_text`, `ET.fromstring`, `ET.tostring`, `config_path.write_text`, `load_ai`, `str`, `tree.find`, `tree.find('budget').set`, `uuid.uuid4`, `work.mkdir`, `xml.replace`

</details>

<a id="fn-tests-test_provider_contracts-openai_response"></a>
### `openai_response`

**함수** · [정의 위치 L60](../../tests/test_provider_contracts.py#L60)

```python
openai_response(*, response_id: str='resp_1', call_id: str | None='call_1', arguments: str='{"target":"HOST-001"}', cached_tokens: int=40, cache_write_tokens: int=0) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`output.append`

</details>

<a id="fn-tests-test_provider_contracts-anthropic_response"></a>
### `anthropic_response`

**함수** · [정의 위치 L108](../../tests/test_provider_contracts.py#L108)

```python
anthropic_response(*, message_id: str='msg_1', tool_id: str='toolu_1', tool_input: object | None=None) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_provider_contracts-replace_openai_client"></a>
### `replace_openai_client`

**비동기 함수** · [정의 위치 L143](../../tests/test_provider_contracts.py#L143)

```python
async replace_openai_client(conversation: Conversation, handler) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`conversation.client.close`, `httpx2.AsyncClient`, `httpx2.MockTransport`, `openai.AsyncOpenAI`

</details>

<a id="fn-tests-test_provider_contracts-replace_anthropic_client"></a>
### `replace_anthropic_client`

**비동기 함수** · [정의 위치 L153](../../tests/test_provider_contracts.py#L153)

```python
async replace_anthropic_client(conversation: Conversation, handler) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`anthropic.AsyncAnthropic`, `conversation.client.close`, `httpx2.AsyncClient`, `httpx2.MockTransport`

</details>

<a id="fn-tests-test_provider_contracts-records"></a>
### `records`

**함수** · [정의 위치 L163](../../tests/test_provider_contracts.py#L163)

```python
records(path: Path) -> list[dict]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.loads`, `path.read_text`, `path.read_text(encoding='utf-8').splitlines`

</details>

<a id="fn-tests-test_provider_contracts-test_openai_responses_preserves_reasoning_tool_history_and_cached_usage"></a>
### `test_openai_responses_preserves_reasoning_tool_history_and_cached_usage`

**비동기 함수** · [정의 위치 L168](../../tests/test_provider_contracts.py#L168)

```python
async test_openai_responses_preserves_reasoning_tool_history_and_cached_usage() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `all`, `any`, `conversation.close`, `conversation.log_path.read_text`, `conversation.next`, `conversation.result`, `fresh_config`, `item.get`, `item.values`, `openai_response`, `records`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_openai_responses_preserves_reasoning_tool_history_and_cached_usage-handler"></a>
### `test_openai_responses_preserves_reasoning_tool_history_and_cached_usage.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L176](../../tests/test_provider_contracts.py#L176)

```python
async test_openai_responses_preserves_reasoning_tool_history_and_cached_usage.handler(request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`, `json.loads`, `len`, `replies.pop`, `requests.append`

</details>

<a id="fn-tests-test_provider_contracts-test_cache_write_premium_is_reserved_before_api_request"></a>
### `test_cache_write_premium_is_reserved_before_api_request`

**비동기 함수** · [정의 위치 L220](../../tests/test_provider_contracts.py#L220)

```python
async test_cache_write_premium_is_reserved_before_api_request() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `conversation.close`, `conversation.ledger.summary`, `conversation.next`, `fresh_config`, `pytest.raises`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_cache_write_premium_is_reserved_before_api_request-handler"></a>
### `test_cache_write_premium_is_reserved_before_api_request.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L226](../../tests/test_provider_contracts.py#L226)

```python
async test_cache_write_premium_is_reserved_before_api_request.handler(request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`, `openai_response`, `requests.append`

</details>

<a id="fn-tests-test_provider_contracts-test_anthropic_adaptive_tool_blocks_history_and_cache_accounting"></a>
### `test_anthropic_adaptive_tool_blocks_history_and_cache_accounting`

**비동기 함수** · [정의 위치 L242](../../tests/test_provider_contracts.py#L242)

```python
async test_anthropic_adaptive_tool_blocks_history_and_cache_accounting() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `all`, `anthropic_response`, `conversation.close`, `conversation.log_path.read_text`, `conversation.next`, `conversation.result`, `fresh_config`, `next`, `records`, `replace_anthropic_client`

</details>

<a id="fn-tests-test_provider_contracts-test_anthropic_adaptive_tool_blocks_history_and_cache_accounting-handler"></a>
### `test_anthropic_adaptive_tool_blocks_history_and_cache_accounting.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L250](../../tests/test_provider_contracts.py#L250)

```python
async test_anthropic_adaptive_tool_blocks_history_and_cache_accounting.handler(request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`, `json.loads`, `len`, `replies.pop`, `requests.append`

</details>

<a id="fn-tests-test_provider_contracts-test_openai_nonbillable_http_error_releases_reservation_without_leaking_body"></a>
### `test_openai_nonbillable_http_error_releases_reservation_without_leaking_body`

**비동기 함수** · [정의 위치 L295](../../tests/test_provider_contracts.py#L295)

```python
async test_openai_nonbillable_http_error_releases_reservation_without_leaking_body() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `config.ledger_path.exists`, `conversation.close`, `conversation.ledger.summary`, `conversation.log_path.read_text`, `conversation.next`, `fresh_config`, `pytest.raises`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_openai_nonbillable_http_error_releases_reservation_without_leaking_body-handler"></a>
### `test_openai_nonbillable_http_error_releases_reservation_without_leaking_body.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L298](../../tests/test_provider_contracts.py#L298)

```python
async test_openai_nonbillable_http_error_releases_reservation_without_leaking_body.handler(_request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`

</details>

<a id="fn-tests-test_provider_contracts-test_timeout_keeps_full_reservation_across_ledger_restart"></a>
### `test_timeout_keeps_full_reservation_across_ledger_restart`

**비동기 함수** · [정의 위치 L321](../../tests/test_provider_contracts.py#L321)

```python
async test_timeout_keeps_full_reservation_across_ledger_restart() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`BudgetLedger`, `BudgetLedger(config.ledger_path, config.budget_usd).summary`, `Conversation`, `Decimal`, `conversation.close`, `conversation.ledger.summary`, `conversation.next`, `fresh_config`, `pytest.raises`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_timeout_keeps_full_reservation_across_ledger_restart-handler"></a>
### `test_timeout_keeps_full_reservation_across_ledger_restart.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L324](../../tests/test_provider_contracts.py#L324)

```python
async test_timeout_keeps_full_reservation_across_ledger_restart.handler(request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.ReadTimeout`

</details>

<a id="fn-tests-test_provider_contracts-test_completed_response_without_tool_is_a_billable_schema_error"></a>
### `test_completed_response_without_tool_is_a_billable_schema_error`

**비동기 함수** · [정의 위치 L345](../../tests/test_provider_contracts.py#L345)

```python
async test_completed_response_without_tool_is_a_billable_schema_error() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `conversation.close`, `conversation.ledger.summary`, `conversation.next`, `fresh_config`, `pytest.raises`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_completed_response_without_tool_is_a_billable_schema_error-handler"></a>
### `test_completed_response_without_tool_is_a_billable_schema_error.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L348](../../tests/test_provider_contracts.py#L348)

```python
async test_completed_response_without_tool_is_a_billable_schema_error.handler(_request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`, `openai_response`

</details>

<a id="fn-tests-test_provider_contracts-test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement"></a>
### `test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement`

**비동기 함수** · [정의 위치 L365](../../tests/test_provider_contracts.py#L365)

```python
async test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `conversation.close`, `conversation.ledger.summary`, `conversation.next`, `fresh_config`, `pytest.raises`, `replace_openai_client`

</details>

<a id="fn-tests-test_provider_contracts-test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement-handler"></a>
### `test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L368](../../tests/test_provider_contracts.py#L368)

```python
async test_malformed_openai_tool_arguments_are_schema_error_after_usage_settlement.handler(_request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`httpx2.Response`, `openai_response`

</details>

<a id="fn-tests-test_provider_contracts-test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement"></a>
### `test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement`

**비동기 함수** · [정의 위치 L386](../../tests/test_provider_contracts.py#L386)

```python
async test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Conversation`, `Decimal`, `conversation.close`, `conversation.ledger.summary`, `conversation.next`, `fresh_config`, `pytest.mark.filterwarnings`, `pytest.raises`, `replace_anthropic_client`

</details>

<a id="fn-tests-test_provider_contracts-test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement-handler"></a>
### `test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement.handler`

**비동기 함수 (중첩 handler)** · [정의 위치 L389](../../tests/test_provider_contracts.py#L389)

```python
async test_malformed_anthropic_tool_input_is_schema_error_after_usage_settlement.handler(_request: httpx2.Request) -> httpx2.Response
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`anthropic_response`, `httpx2.Response`

</details>

<a id="module-tests-test_report_contract"></a>
## `tests.test_report_contract`

[소스 파일](../../tests/test_report_contract.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_report_contract-work"></a>
### `work`

**함수** · [정의 위치 L18](../../tests/test_report_contract.py#L18)

```python
work()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`path.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_report_contract-facts"></a>
### `facts`

**함수** · [정의 위치 L24](../../tests/test_report_contract.py#L24)

```python
facts()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-report"></a>
### `report`

**함수** · [정의 위치 L33](../../tests/test_report_contract.py#L33)

```python
report(outcome)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs`

**비동기 함수** · [정의 위치 L44](../../tests/test_report_contract.py#L44)

```python
async test_report_contract_rejects_prose_outcome_then_repairs(monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`compose_report`, `facts`, `json.dumps`, `load_ai`, `load_system`, `monkeypatch.setattr`, `report`, `work`

</details>

<a id="class-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs-ScriptedConversation"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation`

**클래스** · [정의 위치 L45](../../tests/test_report_contract.py#L45)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs-ScriptedConversation-__init__"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.__init__`

**메서드 (중첩 handler)** · [정의 위치 L50](../../tests/test_report_contract.py#L50)

```python
test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.__init__(self, *args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs-ScriptedConversation-next"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.next`

**비동기 메서드 (중첩 handler)** · [정의 위치 L53](../../tests/test_report_contract.py#L53)

```python
async test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.next(self, schemas, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ToolCall`, `report`, `str`, `type`, `type(self).schemas.append`

</details>

<a id="fn-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs-ScriptedConversation-result"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.result`

**메서드 (중첩 handler)** · [정의 위치 L59](../../tests/test_report_contract.py#L59)

```python
test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.result(self, call, result)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`type`, `type(self).results.append`

</details>

<a id="fn-tests-test_report_contract-test_report_contract_rejects_prose_outcome_then_repairs-ScriptedConversation-close"></a>
### `test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.close`

**비동기 메서드 (중첩 handler)** · [정의 위치 L62](../../tests/test_report_contract.py#L62)

```python
async test_report_contract_rejects_prose_outcome_then_repairs.ScriptedConversation.close(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit`

**비동기 함수** · [정의 위치 L81](../../tests/test_report_contract.py#L81)

```python
async test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit(monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `compose_report`, `facts`, `len`, `load_ai`, `load_system`, `monkeypatch.setattr`, `pytest.raises`, `work`

</details>

<a id="class-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit-ScriptedConversation"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation`

**클래스** · [정의 위치 L82](../../tests/test_report_contract.py#L82)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit-ScriptedConversation-__init__"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.__init__`

**메서드 (중첩 handler)** · [정의 위치 L86](../../tests/test_report_contract.py#L86)

```python
test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.__init__(self, *args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit-ScriptedConversation-next"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.next`

**비동기 메서드 (중첩 handler)** · [정의 위치 L89](../../tests/test_report_contract.py#L89)

```python
async test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.next(self, schemas, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ToolCall`, `report`, `str`, `type`

</details>

<a id="fn-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit-ScriptedConversation-result"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.result`

**메서드 (중첩 handler)** · [정의 위치 L93](../../tests/test_report_contract.py#L93)

```python
test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.result(self, call, result)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`type`, `type(self).results.append`

</details>

<a id="fn-tests-test_report_contract-test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit-ScriptedConversation-close"></a>
### `test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.close`

**비동기 메서드 (중첩 handler)** · [정의 위치 L96](../../tests/test_report_contract.py#L96)

```python
async test_report_contract_keeps_rejecting_invalid_outcome_until_retry_limit.ScriptedConversation.close(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-tests-test_repository_tools"></a>
## `tests.test_repository_tools`

[소스 파일](../../tests/test_repository_tools.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Publication checks must examine Git's actual index and preserve private files.

<a id="fn-tests-test_repository_tools-repository_checker"></a>
### `repository_checker`

**함수** · [정의 위치 L13](../../tests/test_repository_tools.py#L13)

```python
repository_checker(tmp_path, monkeypatch)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`importlib.util.module_from_spec`, `importlib.util.spec_from_file_location`, `monkeypatch.setattr`, `spec.loader.exec_module`, `str`, `subprocess.run`

</details>

<a id="fn-tests-test_repository_tools-test_public_candidates_exclude_private_configuration"></a>
### `test_public_candidates_exclude_private_configuration`

**함수** · [정의 위치 L22](../../tests/test_repository_tools.py#L22)

```python
test_public_candidates_exclude_private_configuration(repository_checker)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(root / '.gitignore').write_text`, `(root / 'README.md').write_text`, `(root / 'configs').mkdir`, `checker.audit`, `checker.git_files`, `private.read_bytes`, `private.write_text`

</details>

<a id="fn-tests-test_repository_tools-test_staged_blob_is_scanned_even_after_working_file_is_cleaned"></a>
### `test_staged_blob_is_scanned_even_after_working_file_is_cleaned`

**함수** · [정의 위치 L36](../../tests/test_repository_tools.py#L36)

```python
test_staged_blob_is_scanned_even_after_working_file_is_cleaned(repository_checker)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`any`, `checker.audit`, `json.dumps`, `path.write_text`, `str`, `subprocess.run`

</details>

<a id="fn-tests-test_repository_tools-test_link_to_an_ignored_local_file_is_not_publishable"></a>
### `test_link_to_an_ignored_local_file_is_not_publishable`

**함수** · [정의 위치 L50](../../tests/test_repository_tools.py#L50)

```python
test_link_to_an_ignored_local_file_is_not_publishable(repository_checker)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(root / '.gitignore').write_text`, `(root / 'README.md').write_text`, `(root / 'configs').mkdir`, `(root / 'configs/ai.local.xml').write_text`, `any`, `checker.audit`

</details>

<a id="module-tests-test_review_regressions"></a>
## `tests.test_review_regressions`

[소스 파일](../../tests/test_review_regressions.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_review_regressions-work"></a>
### `work`

**함수** · [정의 위치 L19](../../tests/test_review_regressions.py#L19)

```python
work()
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`p.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_review_regressions-comparison_fixture"></a>
### `comparison_fixture`

**함수** · [정의 위치 L22](../../tests/test_review_regressions.py#L22)

```python
comparison_fixture(path, config, scenario_hash='same-scenario')
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(path / 'effective-config.json').write_text`, `comparison_identity`, `json.dumps`

</details>

<a id="fn-tests-test_review_regressions-test_different_execution_settings_not_paired"></a>
### `test_different_execution_settings_not_paired`

**함수** · [정의 위치 L29](../../tests/test_review_regressions.py#L29)

```python
test_different_execution_settings_not_paired(key, value)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comparison_fixture`, `deepcopy`, `load_ai`, `load_ai(ROOT / 'configs/ai.example.xml').public`, `load_system`, `load_system(ROOT / 'configs/system.xml').public`, `pytest.mark.parametrize`, `work`

</details>

<a id="fn-tests-test_review_regressions-test_custom_request_and_profile_generation_settings_not_paired"></a>
### `test_custom_request_and_profile_generation_settings_not_paired`

**함수** · [정의 위치 L35](../../tests/test_review_regressions.py#L35)

```python
test_custom_request_and_profile_generation_settings_not_paired()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`comparison_fixture`, `deepcopy`, `load_ai`, `load_ai(ROOT / 'configs/ai.example.xml').public`, `load_system`, `load_system(ROOT / 'configs/system.xml').public`, `work`

</details>

<a id="fn-tests-test_review_regressions-test_proposed_change_rejects_nonexistent_route_parameter"></a>
### `test_proposed_change_rejects_nonexistent_route_parameter`

**함수** · [정의 위치 L45](../../tests/test_review_regressions.py#L45)

```python
test_proposed_change_rejects_nonexistent_route_parameter()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ProposedChange`, `pytest.raises`

</details>

<a id="fn-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview"></a>
### `test_operation_repairs_invalid_proposal_before_preview`

**비동기 함수** · [정의 위치 L49](../../tests/test_review_regressions.py#L49)

```python
async test_operation_repairs_invalid_proposal_before_preview(monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`load_ai`, `load_system`, `monkeypatch.setattr`, `select_change`, `work`

</details>

<a id="class-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview-ScriptedConversation"></a>
### `test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation`

**클래스** · [정의 위치 L50](../../tests/test_review_regressions.py#L50)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview-ScriptedConversation-__init__"></a>
### `test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.__init__`

**메서드 (중첩 handler)** · [정의 위치 L52](../../tests/test_review_regressions.py#L52)

```python
test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.__init__(self, *args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview-ScriptedConversation-next"></a>
### `test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.next`

**비동기 메서드 (중첩 handler)** · [정의 위치 L53](../../tests/test_review_regressions.py#L53)

```python
async test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.next(self, schemas, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ToolCall`, `str`, `type`

</details>

<a id="fn-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview-ScriptedConversation-result"></a>
### `test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.result`

**메서드 (중첩 handler)** · [정의 위치 L57](../../tests/test_review_regressions.py#L57)

```python
test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.result(self, *args)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_review_regressions-test_operation_repairs_invalid_proposal_before_preview-ScriptedConversation-close"></a>
### `test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.close`

**비동기 메서드 (중첩 handler)** · [정의 위치 L58](../../tests/test_review_regressions.py#L58)

```python
async test_operation_repairs_invalid_proposal_before_preview.ScriptedConversation.close(self)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-tests-test_run_analysis"></a>
## `tests.test_run_analysis`

[소스 파일](../../tests/test_run_analysis.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Evidence and security checks for the read-only Result Analysis backend.

<a id="fn-tests-test_run_analysis-_working"></a>
### `_working`

**함수** · [정의 위치 L30](../../tests/test_run_analysis.py#L30)

```python
_working(name: str) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`path.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_run_analysis-_digest"></a>
### `_digest`

**함수** · [정의 위치 L36](../../tests/test_run_analysis.py#L36)

```python
_digest(path: Path) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`hashlib.sha256`, `hashlib.sha256(path.read_bytes()).hexdigest`, `path.read_bytes`

</details>

<a id="fn-tests-test_run_analysis-actual_mock_run"></a>
### `actual_mock_run`

**함수** · [정의 위치 L41](../../tests/test_run_analysis.py#L41)

```python
actual_mock_run() -> Path
```

> Save one real mock run containing the normal N0 and rerouted W1 paths.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_working`, `asyncio.run`, `pytest.fixture`, `run`

</details>

<a id="fn-tests-test_run_analysis-test_actual_n0_w1_analysis_uses_observed_data_and_is_read_only"></a>
### `test_actual_n0_w1_analysis_uses_observed_data_and_is_read_only`

**함수** · [정의 위치 L62](../../tests/test_run_analysis.py#L62)

```python
test_actual_n0_w1_analysis_uses_observed_data_and_is_read_only(actual_mock_run: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_digest`, `actual_mock_run.glob`, `all`, `analyze_run`, `any`, `json.dumps`, `json.dumps(analysis, ensure_ascii=False).casefold`, `next`, `path.stat`, `sorted`

</details>

<a id="fn-tests-test_run_analysis-test_episode_outcomes_remain_distinct"></a>
### `test_episode_outcomes_remain_distinct`

**함수** · [정의 위치 L138](../../tests/test_run_analysis.py#L138)

```python
test_episode_outcomes_remain_distinct(outcome: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(episode_dir / 'result.json').write_text`, `(run_dir / 'manifest.json').write_text`, `_working`, `analyze_run`, `episode_dir.mkdir`, `json.dumps`, `pytest.mark.parametrize`

</details>

<a id="fn-tests-test_run_analysis-test_aborted_partial_and_malformed_artifacts_are_ready_but_unsealed"></a>
### `test_aborted_partial_and_malformed_artifacts_are_ready_but_unsealed`

**함수** · [정의 위치 L178](../../tests/test_run_analysis.py#L178)

```python
test_aborted_partial_and_malformed_artifacts_are_ready_but_unsealed() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(episode_dir / 'result.json').write_text`, `(run_dir / 'integrity.json').write_text`, `(run_dir / 'manifest.json').write_text`, `_working`, `analyze_run`, `episode_dir.mkdir`, `json.dumps`

</details>

<a id="fn-tests-test_run_analysis-_write_system_config"></a>
### `_write_system_config`

**함수** · [정의 위치 L210](../../tests/test_run_analysis.py#L210)

```python
_write_system_config(workspace: Path, output_root: Path) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ET.ElementTree`, `ET.ElementTree(root).write`, `ET.parse`, `ET.parse(PROJECT / 'configs/system.xml').getroot`, `output_root.resolve`, `path.parent.mkdir`, `paths.set`, `root.find`, `str`

</details>

<a id="fn-tests-test_run_analysis-_request"></a>
### `_request`

**함수** · [정의 위치 L221](../../tests/test_run_analysis.py#L221)

```python
_request(server: WebConsoleServer, path: str, *, token: bool=True) -> tuple[int, dict]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`HTTPConnection`, `connection.close`, `connection.getresponse`, `connection.request`, `json.loads`, `parse_qs`, `response.read`, `response.read().decode`, `urlencode`, `urlsplit`

</details>

<a id="fn-tests-test_run_analysis-test_studio_uses_shared_wired_story_and_topology_contract"></a>
### `test_studio_uses_shared_wired_story_and_topology_contract`

**함수** · [정의 위치 L233](../../tests/test_run_analysis.py#L233)

```python
test_studio_uses_shared_wired_story_and_topology_contract() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`all`, `set`

</details>

<a id="fn-tests-test_run_analysis-test_analysis_endpoint_requires_auth_known_path_and_controller_terminal"></a>
### `test_analysis_endpoint_requires_auth_known_path_and_controller_terminal`

**함수** · [정의 위치 L247](../../tests/test_run_analysis.py#L247)

```python
test_analysis_endpoint_requires_auth_known_path_and_controller_terminal(actual_mock_run: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `_request`, `_working`, `_write_system_config`, `actual_mock_run.parent.resolve`, `actual_mock_run.resolve`, `server._save_locked`, `server._state['runs'].append`, `server.start`, `server.stop`, `str`

</details>

<a id="module-tests-test_run_finalization"></a>
## `tests.test_run_finalization`

[소스 파일](../../tests/test_run_finalization.py) · [이 폴더 설명](../../tests/README.md)

<a id="class-tests-test_run_finalization-FakeActivity"></a>
### `FakeActivity`

**클래스** · [정의 위치 L21](../../tests/test_run_finalization.py#L21)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_run_finalization-FakeActivity-__init__"></a>
### `FakeActivity.__init__`

**메서드** · [정의 위치 L22](../../tests/test_run_finalization.py#L22)

```python
FakeActivity.__init__(self, failure: BaseException | None=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_run_finalization-FakeActivity-emit"></a>
### `FakeActivity.emit`

**메서드** · [정의 위치 L25](../../tests/test_run_finalization.py#L25)

```python
FakeActivity.emit(self, *args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_run_finalization-fixture_run"></a>
### `fixture_run`

**함수** · [정의 위치 L30](../../tests/test_run_finalization.py#L30)

```python
fixture_run(run_dir: Path) -> tuple[Path, dict, dict, SimpleNamespace]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'episodes' / 'episode-0001').mkdir`, `(run_dir / 'manifest.json').write_text`, `Decimal`, `SimpleNamespace`, `json.dumps`

</details>

<a id="fn-tests-test_run_finalization-call_finalize"></a>
### `call_finalize`

**함수** · [정의 위치 L44](../../tests/test_run_finalization.py#L44)

```python
call_finalize(run_dir: Path, manifest: dict, effective: dict, ai: SimpleNamespace, activity=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`FakeActivity`, `runner._finalize_run`

</details>

<a id="fn-tests-test_run_finalization-scratch_run"></a>
### `scratch_run`

**함수** · [정의 위치 L60](../../tests/test_run_finalization.py#L60)

```python
scratch_run() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORK_ROOT.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_run_finalization-mock_integrity_and_ledger"></a>
### `mock_integrity_and_ledger`

**함수** · [정의 위치 L65](../../tests/test_run_finalization.py#L65)

```python
mock_integrity_and_ledger(monkeypatch) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`monkeypatch.setattr`

</details>

<a id="fn-tests-test_run_finalization-test_finalization_errors_are_terminal_unsealed_and_safe"></a>
### `test_finalization_errors_are_terminal_unsealed_and_safe`

**함수** · [정의 위치 L87](../../tests/test_run_finalization.py#L87)

```python
test_finalization_errors_are_terminal_unsealed_and_safe(scratch_run, monkeypatch, phase, inject)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'finalization-error.json').read_text`, `(run_dir / 'manifest.json').read_text`, `(run_dir / 'report.html').exists`, `(run_dir / 'report.md').exists`, `FakeActivity`, `PermissionError`, `call_finalize`, `expected_error.update`, `fixture_run`, `inject`, `json.dumps`, `json.dumps(failure).lower`, `json.dumps(saved).lower`, `json.loads`, `mock_integrity_and_ledger`, `pytest.mark.parametrize`, `pytest.raises`, `saved.get`, `summary_path.exists`, `summary_path.read_text`

</details>

<a id="fn-tests-test_run_finalization-fail_write_for"></a>
### `fail_write_for`

**함수** · [정의 위치 L120](../../tests/test_run_finalization.py#L120)

```python
fail_write_for(monkeypatch, basename: str) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`monkeypatch.setattr`

</details>

<a id="fn-tests-test_run_finalization-fail_write_for-injected"></a>
### `fail_write_for.injected`

**함수 (중첩 handler)** · [정의 위치 L124](../../tests/test_run_finalization.py#L124)

```python
fail_write_for.injected(path, value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `PermissionError`, `original`

</details>

<a id="fn-tests-test_run_finalization-fail_seal_manifest_write"></a>
### `fail_seal_manifest_write`

**함수** · [정의 위치 L134](../../tests/test_run_finalization.py#L134)

```python
fail_seal_manifest_write(monkeypatch) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`monkeypatch.setattr`

</details>

<a id="fn-tests-test_run_finalization-fail_seal_manifest_write-injected"></a>
### `fail_seal_manifest_write.injected`

**함수 (중첩 handler)** · [정의 위치 L137](../../tests/test_run_finalization.py#L137)

```python
fail_seal_manifest_write.injected(path, value)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `original`, `value.get`, `win32_sharing_error`

</details>

<a id="fn-tests-test_run_finalization-test_finalization_success_writes_summary_and_seal"></a>
### `test_finalization_success_writes_summary_and_seal`

**함수** · [정의 위치 L145](../../tests/test_run_finalization.py#L145)

```python
test_finalization_success_writes_summary_and_seal(scratch_run, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').read_text`, `(run_dir / 'report.html').exists`, `(run_dir / 'report.md').exists`, `call_finalize`, `fixture_run`, `json.loads`, `mock_integrity_and_ledger`

</details>

<a id="fn-tests-test_run_finalization-win32_sharing_error"></a>
### `win32_sharing_error`

**함수** · [정의 위치 L162](../../tests/test_run_finalization.py#L162)

```python
win32_sharing_error() -> PermissionError
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`PermissionError`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_retries_transient_sharing_violation"></a>
### `test_write_json_retries_transient_sharing_violation`

**함수** · [정의 위치 L168](../../tests/test_run_finalization.py#L168)

```python
test_write_json_retries_transient_sharing_violation(scratch_run, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`json.loads`, `list`, `monkeypatch.setattr`, `runner.write_json`, `scratch_run.mkdir`, `target.read_text`, `target.with_name`, `target.with_name(target.name + '.writing').exists`, `target.write_text`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_retries_transient_sharing_violation-replace"></a>
### `test_write_json_retries_transient_sharing_violation.replace`

**함수 (중첩 handler)** · [정의 위치 L176](../../tests/test_run_finalization.py#L176)

```python
test_write_json_retries_transient_sharing_violation.replace(source, destination)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`real_replace`, `win32_sharing_error`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_permanent_sharing_violation_is_bounded_and_propagated"></a>
### `test_write_json_permanent_sharing_violation_is_bounded_and_propagated`

**함수** · [정의 위치 L194](../../tests/test_run_finalization.py#L194)

```python
test_write_json_permanent_sharing_violation_is_bounded_and_propagated(scratch_run, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`len`, `list`, `monkeypatch.setattr`, `pytest.raises`, `runner.write_json`, `scratch_run.mkdir`, `target.read_text`, `target.with_name`, `target.with_name(target.name + '.writing').exists`, `target.write_text`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_permanent_sharing_violation_is_bounded_and_propagated-replace"></a>
### `test_write_json_permanent_sharing_violation_is_bounded_and_propagated.replace`

**함수 (중첩 handler)** · [정의 위치 L202](../../tests/test_run_finalization.py#L202)

```python
test_write_json_permanent_sharing_violation_is_bounded_and_propagated.replace(source, destination)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`win32_sharing_error`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_recovers_from_native_win32_delete_share_lock"></a>
### `test_write_json_recovers_from_native_win32_delete_share_lock`

**함수** · [정의 위치 L221](../../tests/test_run_finalization.py#L221)

```python
test_write_json_recovers_from_native_win32_delete_share_lock(scratch_run, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ctypes.WinDLL`, `ctypes.WinError`, `ctypes.c_void_p`, `ctypes.get_last_error`, `json.loads`, `kernel.CloseHandle`, `kernel.CreateFileW`, `monkeypatch.setattr`, `pytest.mark.skipif`, `runner.write_json`, `scratch_run.mkdir`, `str`, `target.read_text`, `target.write_text`

</details>

<a id="fn-tests-test_run_finalization-test_write_json_recovers_from_native_win32_delete_share_lock-replace_and_release_after_retries"></a>
### `test_write_json_recovers_from_native_win32_delete_share_lock.replace_and_release_after_retries`

**함수 (중첩 handler)** · [정의 위치 L238](../../tests/test_run_finalization.py#L238)

```python
test_write_json_recovers_from_native_win32_delete_share_lock.replace_and_release_after_retries(source, destination)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`getattr`, `kernel.CloseHandle`, `real_replace`

</details>

<a id="fn-tests-test_run_finalization-test_run_abort_records_type_and_reraises_original_exception"></a>
### `test_run_abort_records_type_and_reraises_original_exception`

**비동기 함수** · [정의 위치 L263](../../tests/test_run_finalization.py#L263)

```python
async test_run_abort_records_type_and_reraises_original_exception(scratch_run, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').read_text`, `(run_dir / 'run-error.json').read_text`, `(run_dir / 'summary.json').exists`, `json.loads`, `manifest.get`, `monkeypatch.setattr`, `next`, `output_root.iterdir`, `output_root.mkdir`, `pytest.raises`, `runner.run`, `win32_sharing_error`

</details>

<a id="fn-tests-test_run_finalization-test_run_abort_records_type_and_reraises_original_exception-abort_episode"></a>
### `test_run_abort_records_type_and_reraises_original_exception.abort_episode`

**비동기 함수 (중첩 handler)** · [정의 위치 L268](../../tests/test_run_finalization.py#L268)

```python
async test_run_abort_records_type_and_reraises_original_exception.abort_episode(*args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="module-tests-test_runbook_discovery"></a>
## `tests.test_runbook_discovery`

[소스 파일](../../tests/test_runbook_discovery.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Repository documentation must not become Agent runbook input.

<a id="fn-tests-test_runbook_discovery-test_readme_is_excluded_from_discovery_snapshot_and_search"></a>
### `test_readme_is_excluded_from_discovery_snapshot_and_search`

**함수** · [정의 위치 L14](../../tests/test_runbook_discovery.py#L14)

```python
test_readme_is_excluded_from_discovery_snapshot_and_search(tmp_path)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(catalog / 'README.md').write_text`, `(nested / 'readme.md').write_text`, `RunbookStore`, `catalog.mkdir`, `len`, `nested.mkdir`, `runbook.write_text`, `runbook_files`, `snapshot_runbooks`, `store.close`, `store.search`

</details>

<a id="fn-tests-test_runbook_discovery-test_web_catalog_loads_six_runbooks_with_folder_readme"></a>
### `test_web_catalog_loads_six_runbooks_with_folder_readme`

**함수** · [정의 위치 L34](../../tests/test_runbook_discovery.py#L34)

```python
test_web_catalog_loads_six_runbooks_with_folder_readme(tmp_path)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(workspace / 'console-state.json').read_text`, `ET.parse`, `WebConsoleServer`, `all`, `item['source_name'].casefold`, `json.loads`, `len`, `str`, `tree.find`, `tree.find('paths').set`, `tree.write`

</details>

<a id="fn-tests-test_runbook_discovery-test_runtime_paths_use_explicit_environment_without_creating_files"></a>
### `test_runtime_paths_use_explicit_environment_without_creating_files`

**함수** · [정의 위치 L47](../../tests/test_runbook_discovery.py#L47)

```python
test_runtime_paths_use_explicit_environment_without_creating_files(tmp_path, monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(tmp_path / 'work').exists`, `monkeypatch.delenv`, `monkeypatch.setenv`, `str`, `web_workspace`, `working_root`

</details>

<a id="module-tests-test_runner_e2e"></a>
## `tests.test_runner_e2e`

[소스 파일](../../tests/test_runner_e2e.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Real TCP/child-process checks plus workflow failure-path coverage, without paid APIs.

<a id="fn-tests-test_runner_e2e-settings"></a>
### `settings`

**함수** · [정의 위치 L16](../../tests/test_runner_e2e.py#L16)

```python
settings(**overrides)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ET.parse`, `base.mkdir`, `overrides.items`, `str`, `tree.find`, `tree.find('workflow').set`, `tree.write`, `uuid.uuid4`

</details>

<a id="fn-tests-test_runner_e2e-test_memory_chain_over_real_three_process_wire"></a>
### `test_memory_chain_over_real_three_process_wire`

**비동기 함수** · [정의 위치 L24](../../tests/test_runner_e2e.py#L24)

```python
async test_memory_chain_over_real_three_process_wire()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(directory / 'events_merged.jsonl').read_text`, `(directory / 'events_merged.jsonl').read_text().splitlines`, `(directory / reads[0]['payload_ref']).read_text`, `json.loads`, `len`, `run`, `settings`, `verify_seal`

</details>

<a id="fn-tests-test_runner_e2e-test_wrong_action_rolls_back_and_never_writes_memory"></a>
### `test_wrong_action_rolls_back_and_never_writes_memory`

**비동기 함수** · [정의 위치 L38](../../tests/test_runner_e2e.py#L38)

```python
async test_wrong_action_rolls_back_and_never_writes_memory(monkeypatch)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(directory / 'episodes/episode-0001/oracle.json').read_text`, `(directory / 'episodes/episode-0001/result.json').read_text`, `json.loads`, `monkeypatch.setattr`, `run`, `settings`

</details>

<a id="fn-tests-test_runner_e2e-test_wrong_action_rolls_back_and_never_writes_memory-wrong"></a>
### `test_wrong_action_rolls_back_and_never_writes_memory.wrong`

**비동기 함수 (중첩 handler)** · [정의 위치 L39](../../tests/test_runner_e2e.py#L39)

```python
async test_wrong_action_rolls_back_and_never_writes_memory.wrong(*args, **kwargs)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_runner_e2e-test_declined_change_has_no_side_effect_or_memory"></a>
### `test_declined_change_has_no_side_effect_or_memory`

**비동기 함수** · [정의 위치 L51](../../tests/test_runner_e2e.py#L51)

```python
async test_declined_change_has_no_side_effect_or_memory()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(directory / 'episodes/episode-0001/oracle.json').read_text`, `(directory / 'episodes/episode-0001/result.json').read_text`, `json.loads`, `run`, `settings`

</details>

<a id="fn-tests-test_runner_e2e-test_diagnosis_budget_failure_is_finite_and_auditable"></a>
### `test_diagnosis_budget_failure_is_finite_and_auditable`

**비동기 함수** · [정의 위치 L60](../../tests/test_runner_e2e.py#L60)

```python
async test_diagnosis_budget_failure_is_finite_and_auditable()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(directory / 'episodes/episode-0001/result.json').read_text`, `json.loads`, `run`, `settings`

</details>

<a id="fn-tests-test_runner_e2e-test_state_machine_rejects_out_of_order_apply"></a>
### `test_state_machine_rejects_out_of_order_apply`

**함수** · [정의 위치 L68](../../tests/test_runner_e2e.py#L68)

```python
test_state_machine_rejects_out_of_order_apply()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Workflow`, `pytest.raises`, `settings`, `state.transition`

</details>

<a id="module-tests-test_runtime_conditions"></a>
## `tests.test_runtime_conditions`

[소스 파일](../../tests/test_runtime_conditions.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_runtime_conditions-work"></a>
### `work`

**함수** · [정의 위치 L23](../../tests/test_runtime_conditions.py#L23)

```python
work() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WORK.mkdir`, `path.mkdir`, `shutil.rmtree`, `uuid.uuid4`

</details>

<a id="fn-tests-test_runtime_conditions-_runbook"></a>
### `_runbook`

**함수** · [정의 위치 L33](../../tests/test_runtime_conditions.py#L33)

```python
_runbook(path: Path) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`path.write_text`

</details>

<a id="fn-tests-test_runtime_conditions-test_selected_runbook_and_seed_memory_are_snapshotted_with_explicit_provenance"></a>
### `test_selected_runbook_and_seed_memory_are_snapshotted_with_explicit_provenance`

**비동기 함수** · [정의 위치 L52](../../tests/test_runtime_conditions.py#L52)

```python
async test_selected_runbook_and_seed_memory_are_snapshotted_with_explicit_provenance(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'inputs/initial-memory.json').read_text`, `(run_dir / 'inputs/runbooks/selected.md').read_text`, `(selected / 'selected.md').read_text`, `_runbook`, `connection.close`, `connection.execute`, `json.loads`, `next`, `read_activity`, `run`, `selected.mkdir`, `sqlite3.connect`

</details>

<a id="fn-tests-test_runtime_conditions-test_empty_runbook_selection_and_disabled_rag_complete_mock_flow"></a>
### `test_empty_runbook_selection_and_disabled_rag_complete_mock_flow`

**비동기 함수** · [정의 위치 L114](../../tests/test_runtime_conditions.py#L114)

```python
async test_empty_runbook_selection_and_disabled_rag_complete_mock_flow(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'inputs/runbooks').rglob`, `any`, `empty.mkdir`, `list`, `next`, `read_activity`, `run`

</details>

<a id="fn-tests-test_runtime_conditions-test_runner_applies_real_delay_in_parent_and_child_activity"></a>
### `test_runner_applies_real_delay_in_parent_and_child_activity`

**비동기 함수** · [정의 위치 L147](../../tests/test_runtime_conditions.py#L147)

```python
async test_runner_applies_real_delay_in_parent_and_child_activity(work: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'effective-config.json').read_text`, `(run_dir / 'pacing').glob`, `any`, `json.loads`, `path.read_text`, `path.read_text(encoding='utf-8').splitlines`, `run`, `write_control`, `writer.startswith`

</details>

<a id="module-tests-test_seal_readonly"></a>
## `tests.test_seal_readonly`

[소스 파일](../../tests/test_seal_readonly.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_seal_readonly-sealed_run"></a>
### `sealed_run`

**함수** · [정의 위치 L22](../../tests/test_seal_readonly.py#L22)

```python
sealed_run() -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `EventBus`, `WORKING_ROOT.mkdir`, `artifact.is_file`, `artifact.read_bytes`, `artifact.relative_to`, `artifact.relative_to(run_dir).as_posix`, `bus.emit`, `hashlib.sha256`, `hashlib.sha256(artifact.read_bytes()).hexdigest`, `json.dumps`, `run_dir.mkdir`, `run_dir.rglob`, `shutil.rmtree`, `sorted`, `uuid.uuid4`, `validate_and_merge`

</details>

<a id="fn-tests-test_seal_readonly-test_report_and_compare_leave_modified_sealed_merge_untouched"></a>
### `test_report_and_compare_leave_modified_sealed_merge_untouched`

**함수** · [정의 위치 L46](../../tests/test_seal_readonly.py#L46)

```python
test_report_and_compare_leave_modified_sealed_merge_untouched(sealed_run: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`any`, `compare_runs`, `merged.read_bytes`, `merged.write_bytes`, `pytest.raises`, `verify_seal`

</details>

<a id="fn-tests-test_seal_readonly-test_report_keeps_existing_merge_when_source_events_fail_validation"></a>
### `test_report_keeps_existing_merge_when_source_events_fail_validation`

**함수** · [정의 위치 L61](../../tests/test_seal_readonly.py#L61)

```python
test_report_keeps_existing_merge_when_source_events_fail_validation(sealed_run: Path) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(sealed_run / 'events').glob`, `any`, `merged.read_bytes`, `next`, `shard.write_text`, `verify_seal`

</details>

<a id="module-tests-test_web_console"></a>
## `tests.test_web_console`

[소스 파일](../../tests/test_web_console.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Security, persistence and frozen-input checks for the local web console.

<a id="fn-tests-test_web_console-_working"></a>
### `_working`

**함수** · [정의 위치 L27](../../tests/test_web_console.py#L27)

```python
_working(name: str) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`path.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_web_console-_write_system_config"></a>
### `_write_system_config`

**함수** · [정의 위치 L33](../../tests/test_web_console.py#L33)

```python
_write_system_config(workspace: Path, output_root: Path) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ET.ElementTree`, `ET.ElementTree(root).write`, `ET.parse`, `ET.parse(PROJECT / 'configs/system.xml').getroot`, `output_root.resolve`, `path.parent.mkdir`, `paths.set`, `root.find`, `str`

</details>

<a id="fn-tests-test_web_console-_server"></a>
### `_server`

**함수** · [정의 위치 L44](../../tests/test_web_console.py#L44)

```python
_server(name: str) -> WebConsoleServer
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `_working`, `_write_system_config`

</details>

<a id="fn-tests-test_web_console-_request"></a>
### `_request`

**함수** · [정의 위치 L50](../../tests/test_web_console.py#L50)

```python
_request(server: WebConsoleServer, method: str, path: str, body: object | bytes | None=None, *, token: bool=True, origin: bool=True, content_type: str='application/json', headers: dict[str, str] | None=None) -> tuple[int, dict | str]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`HTTPConnection`, `connection.close`, `connection.getresponse`, `connection.request`, `dict`, `isinstance`, `json.dumps`, `json.dumps(body).encode`, `json.loads`, `parse_qs`, `response.read`, `response.read().decode`, `urlencode`, `urlsplit`

</details>

<a id="fn-tests-test_web_console-_start_payload"></a>
### `_start_payload`

**함수** · [정의 위치 L76](../../tests/test_web_console.py#L76)

```python
_start_payload(**updates: object) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`payload.update`

</details>

<a id="fn-tests-test_web_console-test_auth_origin_content_limits_and_fixed_routes"></a>
### `test_auth_origin_content_limits_and_fixed_routes`

**함수** · [정의 위치 L88](../../tests/test_web_console.py#L88)

```python
test_auth_origin_content_limits_and_fixed_routes() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`HTTPConnection`, `_request`, `_server`, `_server('http-security').start`, `connection.close`, `connection.getresponse`, `connection.request`, `parse_qs`, `response.read`, `server.stop`, `str`, `urlencode`, `urlsplit`

</details>

<a id="fn-tests-test_web_console-test_console_never_exposes_ai_keys_and_serves_same_origin_monitor"></a>
### `test_console_never_exposes_ai_keys_and_serves_same_origin_monitor`

**함수** · [정의 위치 L126](../../tests/test_web_console.py#L126)

```python
test_console_never_exposes_ai_keys_and_serves_same_origin_monitor() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `HTTPConnection`, `_request`, `_server`, `_start_payload`, `connection.close`, `connection.getresponse`, `connection.request`, `json.dumps`, `parse_qs`, `response.read`, `response.read().decode`, `run_dir.mkdir`, `server._save_locked`, `server._state['runs'].append`, `server.start`, `server.stop`, `urlencode`, `urlsplit`

</details>

<a id="fn-tests-test_web_console-test_terminal_index_overrides_stale_running_manifest_for_console_and_analysis"></a>
### `test_terminal_index_overrides_stale_running_manifest_for_console_and_analysis`

**함수** · [정의 위치 L164](../../tests/test_web_console.py#L164)

```python
test_terminal_index_overrides_stale_running_manifest_for_console_and_analysis() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').read_bytes`, `(run_dir / 'manifest.json').write_bytes`, `(run_dir / 'summary.json').exists`, `Path`, `WebConsoleServer`, `_request`, `_server`, `_start_payload`, `chr`, `json.dumps`, `json.dumps({'run_id': run_id, 'status': 'RUNNING', 'episodes': []}).encode`, `restarted.console_state`, `restarted.start`, `restarted.stop`, `run_dir.mkdir`, `run_dir.parent.resolve`, `run_dir.resolve`, `server._save_locked`, `server._state['runs'].append`, `server.console_state`, `str`

</details>

<a id="fn-tests-test_web_console-test_memory_clear_is_soft_and_prior_run_artifacts_are_untouched"></a>
### `test_memory_clear_is_soft_and_prior_run_artifacts_are_untouched`

**함수** · [정의 위치 L206](../../tests/test_web_console.py#L206)

```python
test_memory_clear_is_soft_and_prior_run_artifacts_are_untouched() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `evidence.read_text`, `evidence.write_text`, `next`, `old_run.mkdir`, `server.add_document`, `server.clear_memory`, `server.console_state`

</details>

<a id="fn-tests-test_web_console-test_selection_is_frozen_and_concurrent_start_is_rejected"></a>
### `test_selection_is_frozen_and_concurrent_start_is_rejected`

**함수** · [정의 위치 L222](../../tests/test_web_console.py#L222)

```python
test_selection_is_frozen_and_concurrent_start_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `_start_payload`, `all`, `any`, `entered.wait`, `isinstance`, `monkeypatch.setattr`, `pytest.raises`, `release.set`, `server.add_document`, `server.console_state`, `server.remove_document`, `server.select_document`, `server.start_run`, `threading.Event`, `time.monotonic`, `time.sleep`

</details>

<a id="fn-tests-test_web_console-test_selection_is_frozen_and_concurrent_start_is_rejected-fake_run"></a>
### `test_selection_is_frozen_and_concurrent_start_is_rejected.fake_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L231](../../tests/test_web_console.py#L231)

```python
async test_selection_is_frozen_and_concurrent_start_is_rejected.fake_run(_system: Path, _ai: Path, **options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `(run_dir / 'summary.json').write_text`, `Path`, `asyncio.to_thread`, `entered.set`, `json.dumps`, `options['on_created']`, `path.read_text`, `run_dir.mkdir`, `selected.glob`

</details>

<a id="fn-tests-test_web_console-test_delay_and_options_persist_without_mutating_source_config"></a>
### `test_delay_and_options_persist_without_mutating_source_config`

**함수** · [정의 위치 L266](../../tests/test_web_console.py#L266)

```python
test_delay_and_options_persist_without_mutating_source_config() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(PROJECT / 'configs/system.xml').read_bytes`, `WebConsoleServer`, `_working`, `_write_system_config`, `server.console_state`, `server.set_delay`, `set`, `system_path.read_bytes`

</details>

<a id="fn-tests-test_web_console-test_zero_selected_runbooks_is_a_valid_frozen_condition"></a>
### `test_zero_selected_runbooks_is_a_valid_frozen_condition`

**함수** · [정의 위치 L285](../../tests/test_web_console.py#L285)

```python
test_zero_selected_runbooks_is_a_valid_frozen_condition() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `_start_payload`, `config.is_file`, `list`, `runbooks.glob`, `server._freeze_inputs`, `server._validate_start`, `server.console_state`, `server.select_document`

</details>

<a id="fn-tests-test_web_console-test_stop_releases_force_delay_before_cancelling"></a>
### `test_stop_releases_force_delay_before_cancelling`

**함수** · [정의 위치 L297](../../tests/test_web_console.py#L297)

```python
test_stop_releases_force_delay_before_cancelling(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `_start_payload`, `entered.wait`, `monkeypatch.setattr`, `read_control`, `server.console_state`, `server.start_run`, `server.stop_run`, `threading.Event`, `time.monotonic`, `time.sleep`

</details>

<a id="fn-tests-test_web_console-test_stop_releases_force_delay_before_cancelling-waiting_run"></a>
### `test_stop_releases_force_delay_before_cancelling.waiting_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L303](../../tests/test_web_console.py#L303)

```python
async test_stop_releases_force_delay_before_cancelling.waiting_run(_system: Path, _ai: Path, **_options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.sleep`, `entered.set`

</details>

<a id="fn-tests-test_web_console-test_server_stop_waits_for_cancellation_cleanup"></a>
### `test_server_stop_waits_for_cancellation_cleanup`

**함수** · [정의 위치 L321](../../tests/test_web_console.py#L321)

```python
test_server_stop_waits_for_cancellation_cleanup(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `_start_payload`, `cleanup_finished.is_set`, `entered.wait`, `monkeypatch.setattr`, `read_control`, `server.console_state`, `server.start_run`, `server.stop`, `threading.Event`

</details>

<a id="fn-tests-test_web_console-test_server_stop_waits_for_cancellation_cleanup-cancellable_run"></a>
### `test_server_stop_waits_for_cancellation_cleanup.cancellable_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L328](../../tests/test_web_console.py#L328)

```python
async test_server_stop_waits_for_cancellation_cleanup.cancellable_run(_system: Path, _ai: Path, **_options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.sleep`, `cleanup_finished.set`, `entered.set`

</details>

<a id="fn-tests-test_web_console-test_server_stop_reports_worker_cleanup_timeout"></a>
### `test_server_stop_reports_worker_cleanup_timeout`

**함수** · [정의 위치 L350](../../tests/test_web_console.py#L350)

```python
test_server_stop_reports_worker_cleanup_timeout(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_server`, `_start_payload`, `entered.wait`, `monkeypatch.setattr`, `pytest.raises`, `release_cleanup.set`, `server.start_run`, `server.stop`, `threading.Event`, `worker.is_alive`, `worker.join`

</details>

<a id="fn-tests-test_web_console-test_server_stop_reports_worker_cleanup_timeout-resistant_run"></a>
### `test_server_stop_reports_worker_cleanup_timeout.resistant_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L357](../../tests/test_web_console.py#L357)

```python
async test_server_stop_reports_worker_cleanup_timeout.resistant_run(_system: Path, _ai: Path, **_options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`asyncio.sleep`, `asyncio.to_thread`, `entered.set`

</details>

<a id="fn-tests-test_web_console-test_workspace_symlink_is_rejected"></a>
### `test_workspace_symlink_is_rejected`

**함수** · [정의 위치 L381](../../tests/test_web_console.py#L381)

```python
test_workspace_symlink_is_rejected() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `_working`, `link.symlink_to`, `pytest.raises`, `pytest.skip`, `target.mkdir`

</details>

<a id="module-tests-test_web_lan"></a>
## `tests.test_web_lan`

[소스 파일](../../tests/test_web_lan.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: LAN mode retains the token, peer-network, Host and Origin boundaries.

<a id="fn-tests-test_web_lan-test_lan_requires_specific_host_and_narrow_allowlist"></a>
### `test_lan_requires_specific_host_and_narrow_allowlist`

**함수** · [정의 위치 L20](../../tests/test_web_lan.py#L20)

```python
test_lan_requires_specific_host_and_narrow_allowlist(tmp_path, host, networks)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `pytest.mark.parametrize`, `pytest.raises`

</details>

<a id="fn-tests-test_web_lan-handler"></a>
### `handler`

**함수** · [정의 위치 L26](../../tests/test_web_lan.py#L26)

```python
handler(peer='192.168.1.40', host='192.168.1.10:8123', token='test-capability', origin=None)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`SimpleNamespace`, `ipaddress.IPv4Network`, `object.__new__`

</details>

<a id="fn-tests-test_web_lan-test_lan_peer_and_exact_token_host_are_all_required"></a>
### `test_lan_peer_and_exact_token_host_are_all_required`

**함수** · [정의 위치 L39](../../tests/test_web_lan.py#L39)

```python
test_lan_peer_and_exact_token_host_are_all_required()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`h._parsed`, `handler`

</details>

<a id="fn-tests-test_web_lan-test_lan_post_requires_its_own_origin"></a>
### `test_lan_post_requires_its_own_origin`

**함수** · [정의 위치 L48](../../tests/test_web_lan.py#L48)

```python
test_lan_post_requires_its_own_origin()
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`h.do_POST`, `handler`

</details>

<a id="module-tests-test_web_output_root"></a>
## `tests.test_web_output_root`

[소스 파일](../../tests/test_web_output_root.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: Configured output-root and persisted web-run location regression checks.

<a id="fn-tests-test_web_output_root-_case"></a>
### `_case`

**함수** · [정의 위치 L25](../../tests/test_web_output_root.py#L25)

```python
_case(name: str) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`path.mkdir`, `uuid.uuid4`

</details>

<a id="fn-tests-test_web_output_root-_set_output_root"></a>
### `_set_output_root`

**함수** · [정의 위치 L31](../../tests/test_web_output_root.py#L31)

```python
_set_output_root(system_path: Path, output_root: Path) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ET.ElementTree`, `ET.ElementTree(root).write`, `ET.parse`, `ET.parse(source).getroot`, `output_root.resolve`, `paths.set`, `root.find`, `str`, `system_path.is_file`, `system_path.parent.mkdir`

</details>

<a id="fn-tests-test_web_output_root-_server"></a>
### `_server`

**함수** · [정의 위치 L42](../../tests/test_web_output_root.py#L42)

```python
_server(name: str, output_name: str='configured-output') -> tuple[WebConsoleServer, Path, Path, Path]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `_case`, `_set_output_root`, `output_root.resolve`, `workspace.mkdir`

</details>

<a id="fn-tests-test_web_output_root-_payload"></a>
### `_payload`

**함수** · [정의 위치 L52](../../tests/test_web_output_root.py#L52)

```python
_payload(**updates: object) -> dict[str, object]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`payload.update`

</details>

<a id="fn-tests-test_web_output_root-_wait_for_worker"></a>
### `_wait_for_worker`

**함수** · [정의 위치 L75](../../tests/test_web_output_root.py#L75)

```python
_wait_for_worker(server: WebConsoleServer) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`time.monotonic`, `time.sleep`

</details>

<a id="fn-tests-test_web_output_root-_create_fake_run"></a>
### `_create_fake_run`

**함수** · [정의 위치 L82](../../tests/test_web_output_root.py#L82)

```python
_create_fake_run(root: Path, run_id: str, on_created: object) -> tuple[Path, dict[str, object]]
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `(run_dir / 'summary.json').write_text`, `callable`, `json.dumps`, `on_created`, `root.is_dir`, `run_dir.mkdir`

</details>

<a id="fn-tests-test_web_output_root-test_start_uses_configured_output_for_snapshot_runner_and_public_record"></a>
### `test_start_uses_configured_output_for_snapshot_runner_and_public_record`

**함수** · [정의 위치 L97](../../tests/test_web_output_root.py#L97)

```python
test_start_uses_configured_output_for_snapshot_runner_and_public_record(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(base / 'mutable-decoy').resolve`, `(output_root / 'D0_mock_configured_root').resolve`, `(server.workspace / 'runs').exists`, `Path`, `_payload`, `_server`, `_wait_for_worker`, `captured['snapshot'].is_file`, `monkeypatch.setattr`, `output_root.exists`, `server.console_state`, `server.start_run`

</details>

<a id="fn-tests-test_web_output_root-test_start_uses_configured_output_for_snapshot_runner_and_public_record-fake_run"></a>
### `test_start_uses_configured_output_for_snapshot_runner_and_public_record.fake_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L109](../../tests/test_web_output_root.py#L109)

```python
async test_start_uses_configured_output_for_snapshot_runner_and_public_record.fake_run(system_path: Path, _ai_path: Path, **options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Path`, `Path(options['output_root']).resolve`, `Path(system_path).resolve`, `_create_fake_run`, `load_system`, `load_system(Path(system_path)).output_root.resolve`

</details>

<a id="fn-tests-test_web_output_root-test_start_uses_configured_output_for_snapshot_runner_and_public_record-freeze_then_change_mutable_root"></a>
### `test_start_uses_configured_output_for_snapshot_runner_and_public_record.freeze_then_change_mutable_root`

**함수 (중첩 handler)** · [정의 위치 L117](../../tests/test_web_output_root.py#L117)

```python
test_start_uses_configured_output_for_snapshot_runner_and_public_record.freeze_then_change_mutable_root(launch_id: str, conditions: dict[str, object])
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`original_freeze`

</details>

<a id="fn-tests-test_web_output_root-test_each_start_freezes_its_root_and_both_roots_survive_restart"></a>
### `test_each_start_freezes_its_root_and_both_roots_survive_restart`

**함수** · [정의 위치 L139](../../tests/test_web_output_root.py#L139)

```python
test_each_start_freezes_its_root_and_both_roots_survive_restart(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(base / 'output-b').resolve`, `(output_a / run_ids[0]).resolve`, `(output_b / run_ids[1]).resolve`, `Path`, `WebConsoleServer`, `_payload`, `_server`, `_set_output_root`, `_wait_for_worker`, `first_created.wait`, `monkeypatch.setattr`, `next`, `release_first.set`, `restarted._run_record`, `restarted.console_state`, `restarted.state_for_run`, `server.console_state`, `server.start_run`, `threading.Event`

</details>

<a id="fn-tests-test_web_output_root-test_each_start_freezes_its_root_and_both_roots_survive_restart-fake_run"></a>
### `test_each_start_freezes_its_root_and_both_roots_survive_restart.fake_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L149](../../tests/test_web_output_root.py#L149)

```python
async test_each_start_freezes_its_root_and_both_roots_survive_restart.fake_run(frozen_system: Path, _ai_path: Path, **options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(run_dir / 'manifest.json').write_text`, `(run_dir / 'summary.json').write_text`, `Path`, `Path(options['output_root']).resolve`, `asyncio.to_thread`, `callable`, `callback`, `calls.append`, `first_created.set`, `json.dumps`, `len`, `load_system`, `load_system(Path(frozen_system)).output_root.resolve`, `run_dir.mkdir`

</details>

<a id="fn-tests-test_web_output_root-test_legacy_workspace_run_is_preferred_pinned_and_left_untouched"></a>
### `test_legacy_workspace_run_is_preferred_pinned_and_left_untouched`

**함수** · [정의 위치 L201](../../tests/test_web_output_root.py#L201)

```python
test_legacy_workspace_run_is_preferred_pinned_and_left_untouched() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(configured_dir / 'manifest.json').write_text`, `(legacy_dir / 'manifest.json').write_text`, `(server.workspace / 'console-state.json').read_text`, `(server.workspace / 'runs').resolve`, `Path`, `WebConsoleServer`, `_payload`, `_server`, `configured_dir.mkdir`, `json.dumps`, `json.loads`, `legacy_dir.mkdir`, `legacy_dir.resolve`, `next`, `restarted.console_state`, `restarted.state_for_run`, `sealed.read_bytes`, `sealed.stat`, `sealed.write_bytes`, `server._save_locked`, `server._state['runs'].append`

</details>

<a id="fn-tests-test_web_output_root-test_client_cannot_supply_output_root"></a>
### `test_client_cannot_supply_output_root`

**함수** · [정의 위치 L235](../../tests/test_web_output_root.py#L235)

```python
test_client_cannot_supply_output_root() -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_payload`, `_server`, `pytest.raises`, `server.start_run`, `str`

</details>

<a id="fn-tests-test_web_output_root-test_runner_callback_outside_frozen_root_is_rejected"></a>
### `test_runner_callback_outside_frozen_root_is_rejected`

**함수** · [정의 위치 L243](../../tests/test_web_output_root.py#L243)

```python
test_runner_callback_outside_frozen_root_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`_payload`, `_server`, `_wait_for_worker`, `monkeypatch.setattr`, `server.console_state`, `server.start_run`

</details>

<a id="fn-tests-test_web_output_root-test_runner_callback_outside_frozen_root_is_rejected-fake_run"></a>
### `test_runner_callback_outside_frozen_root_is_rejected.fake_run`

**비동기 함수 (중첩 handler)** · [정의 위치 L247](../../tests/test_web_output_root.py#L247)

```python
async test_runner_callback_outside_frozen_root_is_rejected.fake_run(_system_path: Path, _ai_path: Path, **options: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(outside / 'manifest.json').write_text`, `Path`, `Path(options['output_root']).resolve`, `callable`, `callback`, `json.dumps`, `outside.mkdir`

</details>

<a id="module-tests-test_web_startup_errors"></a>
## `tests.test_web_startup_errors`

[소스 파일](../../tests/test_web_startup_errors.py) · [이 폴더 설명](../../tests/README.md)

> 소스의 모듈 설명: CLI messages for web-listener failures must distinguish bind from setup.

<a id="fn-tests-test_web_startup_errors-test_start_converts_only_listener_bind_errors"></a>
### `test_start_converts_only_listener_bind_errors`

**함수** · [정의 위치 L30](../../tests/test_web_startup_errors.py#L30)

```python
test_start_converts_only_listener_bind_errors(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, os_error: OSError, expected: str) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`OSError`, `PermissionError`, `WebConsoleServer`, `monkeypatch.setattr`, `pytest.mark.parametrize`, `pytest.raises`, `server.start`, `str`

</details>

<a id="fn-tests-test_web_startup_errors-test_start_converts_only_listener_bind_errors-fail_bind"></a>
### `test_start_converts_only_listener_bind_errors.fail_bind`

**함수 (중첩 handler)** · [정의 위치 L40](../../tests/test_web_startup_errors.py#L40)

```python
test_start_converts_only_listener_bind_errors.fail_bind(*_args: object, **_kwargs: object) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_web_startup_errors-test_workspace_permission_error_is_not_a_bind_error"></a>
### `test_workspace_permission_error_is_not_a_bind_error`

**함수** · [정의 위치 L52](../../tests/test_web_startup_errors.py#L52)

```python
test_workspace_permission_error_is_not_a_bind_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`WebConsoleServer`, `monkeypatch.setattr`, `pytest.raises`

</details>

<a id="fn-tests-test_web_startup_errors-test_workspace_permission_error_is_not_a_bind_error-denied_workspace"></a>
### `test_workspace_permission_error_is_not_a_bind_error.denied_workspace`

**함수 (중첩 handler)** · [정의 위치 L55](../../tests/test_web_startup_errors.py#L55)

```python
test_workspace_permission_error_is_not_a_bind_error.denied_workspace(_path: Path, *_args: object, **_kwargs: object) -> Path
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`PermissionError`

</details>

<a id="fn-tests-test_web_startup_errors-test_cli_reports_bind_failure_without_fallback_or_secret"></a>
### `test_cli_reports_bind_failure_without_fallback_or_secret`

**함수** · [정의 위치 L69](../../tests/test_web_startup_errors.py#L69)

```python
test_cli_reports_bind_failure_without_fallback_or_secret(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], port: int) -> None
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`capsys.readouterr`, `cli.main`, `monkeypatch.setattr`, `pytest.mark.parametrize`, `str`

</details>

<a id="class-tests-test_web_startup_errors-test_cli_reports_bind_failure_without_fallback_or_secret-FakeServer"></a>
### `test_cli_reports_bind_failure_without_fallback_or_secret.FakeServer`

**클래스** · [정의 위치 L74](../../tests/test_web_startup_errors.py#L74)

상속/계약: 별도 상속 없음

선언된 필드: 없음. 생성자나 메서드에서 상태를 만들 수 있습니다.

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<a id="fn-tests-test_web_startup_errors-test_cli_reports_bind_failure_without_fallback_or_secret-FakeServer-__init__"></a>
### `test_cli_reports_bind_failure_without_fallback_or_secret.FakeServer.__init__`

**메서드 (중첩 handler)** · [정의 위치 L75](../../tests/test_web_startup_errors.py#L75)

```python
test_cli_reports_bind_failure_without_fallback_or_secret.FakeServer.__init__(self, *_args: object, port: int, host: str, **_kwargs: object)
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`requested.append`

</details>

<a id="fn-tests-test_web_startup_errors-test_cli_reports_bind_failure_without_fallback_or_secret-FakeServer-start"></a>
### `test_cli_reports_bind_failure_without_fallback_or_secret.FakeServer.start`

**메서드 (중첩 handler)** · [정의 위치 L78](../../tests/test_web_startup_errors.py#L78)

```python
test_cli_reports_bind_failure_without_fallback_or_secret.FakeServer.start(self) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`OSError`, `WebConsoleBindError`

</details>

<a id="module-tests-test_wired_catalog"></a>
## `tests.test_wired_catalog`

[소스 파일](../../tests/test_wired_catalog.py) · [이 폴더 설명](../../tests/README.md)

<a id="fn-tests-test_wired_catalog-test_old_catalog_is_archived_once_and_never_reused_for_new_runs"></a>
### `test_old_catalog_is_archived_once_and_never_reused_for_new_runs`

**함수** · [정의 위치 L10](../../tests/test_wired_catalog.py#L10)

```python
test_old_catalog_is_archived_once_and_never_reused_for_new_runs(tmp_path)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(workspace / 'archive').glob`, `Path`, `WebConsoleServer`, `all`, `archive.read_text`, `json.dumps`, `json.loads`, `len`, `list`, `server.console_state`, `set`, `state.write_text`, `workspace.mkdir`

</details>

<a id="fn-tests-test_wired_catalog-test_legacy_scenario_and_target_are_rejected"></a>
### `test_legacy_scenario_and_target_are_rejected`

**함수** · [정의 위치 L33](../../tests/test_wired_catalog.py#L33)

```python
test_legacy_scenario_and_target_are_rejected(tmp_path)
```

테스트 함수입니다. 어떤 정상/실패 조건을 확인하는지는 [테스트 안내](../../tests/README.md)와 assertion을 함께 읽으세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`create_world`, `pytest.raises`

</details>

<a id="module-tools-check_repository"></a>
## `tools.check_repository`

[소스 파일](../../tools/check_repository.py) · [이 폴더 설명](../../tools/README.md)

> 소스의 모듈 설명: Read-only Git publication preflight. Findings never print credential values.

<a id="fn-tools-check_repository-git_files"></a>
### `git_files`

**함수** · [정의 위치 L25](../../tools/check_repository.py#L25)

```python
git_files(staged: bool=False) -> list[str]
```

> List only Git-eligible paths, without staging or changing any file.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`RuntimeError`, `process.stdout.decode`, `process.stdout.decode('utf-8', 'surrogateescape').split`, `set`, `sorted`, `str`, `subprocess.run`

</details>

<a id="fn-tools-check_repository-markdown_without_code"></a>
### `markdown_without_code`

**함수** · [정의 위치 L36](../../tools/check_repository.py#L36)

```python
markdown_without_code(text: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`re.sub`

</details>

<a id="fn-tools-check_repository-markdown_anchors"></a>
### `markdown_anchors`

**함수** · [정의 위치 L40](../../tools/check_repository.py#L40)

```python
markdown_anchors(text: str) -> set[str]
```

> Recognize explicit IDs and the common GitHub heading-slug convention.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`counts.get`, `label.lower`, `markdown_without_code`, `markdown_without_code(text).splitlines`, `match.group`, `re.findall`, `re.match`, `re.sub`, `re.sub('[^\\w\\-\\s]', '', label.lower()).strip`, `re.sub('[^\\w\\-\\s]', '', label.lower()).strip().replace`, `result.add`, `set`

</details>

<a id="fn-tools-check_repository-audit"></a>
### `audit`

**함수** · [정의 위치 L56](../../tools/check_repository.py#L56)

```python
audit(staged: bool=False) -> dict
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(folder / 'README.md').as_posix`, `(node.text or '').strip`, `ET.fromstring`, `LINK.finditer`, `PATTERNS.items`, `Path`, `ROOT.resolve`, `any`, `content`, `content(target_relative).decode`, `enumerate`, `finding`, `git_files`, `int`, `len`, `markdown_anchors`, `markdown_without_code`, `match.group`, `max`, `min`, `name.endswith`, `name.startswith`, `part.casefold`, `path.exists`, `path.is_file`, `path.name.casefold`, `path.relative_to`, `path.resolve`, `path.resolve().is_relative_to`, `path.suffix.lower`, `path_text.startswith`, `pattern.search`, `raw.decode`, `re.findall`, `re.fullmatch`, `re.match`, `re.search`, `relative.lower`, `relative.lower().endswith`, `set`, `sorted`, `target.partition`, `target_path.is_dir`, `target_path.is_relative_to`, `target_path.relative_to`, `target_path.relative_to(ROOT).as_posix`, `target_path.resolve`, `target_path.suffix.lower`, `text.splitlines`, `text_cache.get`, `text_cache.get(target_relative, content(target_relative).decode('utf-8-sig')).splitlines`, `text_cache.items`, `tree.iter`, `unquote`, `urlsplit`, `warnings.append`

</details>

<a id="fn-tools-check_repository-audit-content"></a>
### `audit.content`

**함수 (중첩 handler)** · [정의 위치 L63](../../tools/check_repository.py#L63)

```python
audit.content(relative: str) -> bytes
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`(ROOT / relative).read_bytes`, `OSError`, `str`, `subprocess.run`

</details>

<a id="fn-tools-check_repository-audit-finding"></a>
### `audit.finding`

**함수 (중첩 handler)** · [정의 위치 L71](../../tools/check_repository.py#L71)

```python
audit.finding(kind: str, path: str, line: int | None=None, detail: str | None=None) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`issues.append`

</details>

<a id="fn-tools-check_repository-main"></a>
### `main`

**함수** · [정의 위치 L172](../../tools/check_repository.py#L172)

```python
main() -> int
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`argparse.ArgumentParser`, `args.json_out.parent.mkdir`, `args.json_out.write_text`, `audit`, `json.dumps`, `parser.add_argument`, `parser.parse_args`, `print`, `str`

</details>

<a id="module-tools-generate_reference"></a>
## `tools.generate_reference`

[소스 파일](../../tools/generate_reference.py) · [이 폴더 설명](../../tools/README.md)

> 소스의 모듈 설명: Generate deterministic source/function reference pages without importing the app.

<a id="fn-tools-generate_reference-module_name"></a>
### `module_name`

**함수** · [정의 위치 L16](../../tools/generate_reference.py#L16)

```python
module_name(path: Path) -> str
```

> Use import-like names, keeping __init__ files explicit for file coverage.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'.'.join`, `list`, `path.relative_to`, `path.relative_to(ROOT).with_suffix`

</details>

<a id="fn-tools-generate_reference-anchor"></a>
### `anchor`

**함수** · [정의 위치 L25](../../tools/generate_reference.py#L25)

```python
anchor(prefix: str, name: str) -> str
```

> Return the explicit HTML anchor shared by folder README links.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`name.replace`

</details>

<a id="fn-tools-generate_reference-direct_calls"></a>
### `direct_calls`

**함수** · [정의 위치 L30](../../tools/generate_reference.py#L30)

```python
direct_calls(node: ast.AST) -> list[str]
```

> Collect syntactic call expressions, without claiming runtime dispatch resolution.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ast.iter_child_nodes`, `ast.unparse`, `found.add`, `isinstance`, `len`, `list`, `pending.extend`, `pending.pop`, `set`, `sorted`

</details>

<a id="fn-tools-generate_reference-symbols"></a>
### `symbols`

**함수** · [정의 위치 L49](../../tools/generate_reference.py#L49)

```python
symbols(tree: ast.AST, module: str) -> list[dict]
```

> Enumerate classes, functions, methods, and nested handlers from Python AST.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`Counter`, `anchor`, `visit`

</details>

<a id="fn-tools-generate_reference-symbols-visit"></a>
### `symbols.visit`

**함수 (중첩 handler)** · [정의 위치 L53](../../tools/generate_reference.py#L53)

```python
symbols.visit(node: ast.AST, parents: list[str], parent_kinds: list[str]) -> None
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'.'.join`, `ast.get_docstring`, `ast.iter_child_nodes`, `ast.unparse`, `bool`, `direct_calls`, `isinstance`, `result.append`, `visit`

</details>

<a id="fn-tools-generate_reference-inventory"></a>
### `inventory`

**함수** · [정의 위치 L87](../../tools/generate_reference.py#L87)

```python
inventory() -> list[dict]
```

> Read only source, tests and repository tools; never load local configuration.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`ROOT.joinpath`, `ROOT.joinpath('src').rglob`, `ROOT.joinpath('tests').glob`, `ROOT.joinpath('tools').glob`, `ast.get_docstring`, `ast.parse`, `hashlib.sha256`, `hashlib.sha256(text.encode('utf-8')).hexdigest`, `module_name`, `modules.append`, `path.read_text`, `path.relative_to`, `path.relative_to(ROOT).as_posix`, `sorted`, `str`, `symbols`, `text.encode`

</details>

<a id="fn-tools-generate_reference-escape"></a>
### `escape`

**함수** · [정의 위치 L102](../../tools/generate_reference.py#L102)

```python
escape(text: str) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`text.replace`, `text.replace('\|', '\\\|').replace`, `text.replace('\|', '\\\|').replace('\n', ' ').replace`, `text.replace('\|', '\\\|').replace('\n', ' ').replace('&lt;', '&lt;').replace`

</details>

<a id="fn-tools-generate_reference-build_python_reference"></a>
### `build_python_reference`

**함수** · [정의 위치 L106](../../tools/generate_reference.py#L106)

```python
build_python_reference(modules: list[dict]) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`', '.join`, `'\n'.join`, `Path`, `anchor`, `escape`, `item.get`, `item['short_name'].split`, `item['short_name'].split('.')[-1].startswith`, `len`, `lines.append`, `module['path'].startswith`, `str`, `str(Path(source).parent).replace`, `sum`

</details>

<a id="fn-tools-generate_reference-web_inventory"></a>
### `web_inventory`

**함수** · [정의 위치 L156](../../tools/generate_reference.py#L156)

```python
web_inventory() -> list[dict]
```

> Catalog named JS declarations/assigned arrows embedded in the three UI sources.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`functions.append`, `match.group`, `match.start`, `path.read_text`, `path.relative_to`, `path.relative_to(ROOT).as_posix`, `pattern.finditer`, `re.compile`, `result.append`, `sorted`, `text[:match.start()].count`, `zip`

</details>

<a id="fn-tools-generate_reference-build_web_reference"></a>
### `build_web_reference`

**함수** · [정의 위치 L173](../../tools/generate_reference.py#L173)

```python
build_web_reference(groups: list[dict]) -> str
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`'\n'.join`, `Path`, `escape`, `len`, `lines.append`, `sum`

</details>

<a id="fn-tools-generate_reference-generate"></a>
### `generate`

**함수** · [정의 위치 L188](../../tools/generate_reference.py#L188)

```python
generate(check: bool=False) -> bool
```

상세 동작은 위 정의 위치와 이 폴더의 파일별 역할 설명을 함께 확인하세요.

<details><summary>본문에 직접 적힌 호출 표현</summary>

`OUTPUT.mkdir`, `build_python_reference`, `build_web_reference`, `inventory`, `json.dumps`, `len`, `mismatches.append`, `outputs.items`, `print`, `sum`, `target.exists`, `target.read_text`, `target.write_text`, `web_inventory`

</details>
