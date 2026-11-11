# `ccs.netops` — Network Tool 계약과 SQLite backend

이 패키지는 Agent가 볼 수 있는 Network Tools 표면과 실제 network state 저장 구현을 분리합니다. Agent/`tool_access`는 이름·인자·JSON schema를 알고, MCP tools service는 `NetworkBackend.call(tool, arguments)` 계약으로 backend를 실행합니다. 현재 구현 backend는 [`SQLiteBackend`](sqlite_backend.py)입니다.

## 조회와 변경 데이터 흐름

```mermaid
flowchart LR
  Role[operation / diagnosis role] --> Schema[tool_schemas(role)]
  Schema --> MCP[protocols.mcp]
  MCP --> Handler[services.py tools handler]
  Handler --> Contract[NetworkBackend.call]
  Contract --> SQLite[SQLiteBackend]
  SQLite --> State[(episode SQLite DB)]
  SQLite --> Preview[preview token + expected version]
  Preview --> Approve[runner approval gate]
  Approve --> Apply[apply_change]
  Apply --> Verify[verify_service / get_kpi]
  Verify -->|검증 실패| Rollback[rollback_change]
```

MCP server의 role별 schema 목록 제공은 첫 경계이고, backend schema/role 검증은 호출 시 재검사됩니다. Diagnosis는 read-only 도구만 받으며 Operation에는 필요한 변경 도구도 보입니다. DB 저장은 본질적으로 SQLite synthetic network simulation입니다. 외부 emulator나 실제 물리 망에 접속하지 않습니다.

## 폴더 내 파일

| 파일 | 역할과 주요 심볼 | 전체 함수·메서드 참조 |
|---|---|---|
| [`__init__.py`](__init__.py) | 안정된 tool contract와 SQLite 구현 package 설명. | [module](../../../docs/reference/python_functions.md#module-ccs-netops-__init__) |
| [`backend.py`](backend.py) | 추상 `NetworkBackend` 계약: `call`로 도구 실행, `snapshot`으로 canonical offline state, `close`로 자원 종료. concrete 저장 구조는 계약 밖으로 숨깁니다. | [module](../../../docs/reference/python_functions.md#module-ccs-netops-backend) |
| [`errors.py`](errors.py) | backend 오류를 의미별로 구분: 잘못된 입력/미지 도구, 미존재 ID, stale preview/version, idempotency key 충돌, 부적절한 change lifecycle. | [module](../../../docs/reference/python_functions.md#module-ccs-netops-errors) |
| [`sqlite_backend.py`](sqlite_backend.py) | `SQLiteBackend.call`이 안정된 tool 이름을 handler로 분배합니다. read path는 alarm/log/config/topology/flow/KPI 조회, write path는 preview/apply/status/rollback, ticket path는 incident 갱신입니다. helper method가 입력 제약, version, idempotency, KPI 재계산 및 transaction을 처리합니다. | [module](../../../docs/reference/python_functions.md#module-ccs-netops-sqlite_backend) |
| [`tools.py`](tools.py) | MCP 공개 tool schema를 역할별로 생성합니다. `tool_schemas(role)`은 backend class/SQLite 테이블 이름을 노출하지 않고 허용 도구와 input shape만 제공합니다. | [module](../../../docs/reference/python_functions.md#module-ccs-netops-tools) |

## 변경 lifecycle을 처음 읽을 때

1. `tools.py:tool_schemas(role)`에서 해당 Agent가 어떤 도구를 사용할 수 있는지 확인합니다.
2. `sqlite_backend.py:SQLiteBackend.call`에서 이름이 어디로 전달되는지 봅니다.
3. 변경 전 `preview_change`에서 parameter/value를 정규화하고 예상 상태 version을 반환하는지 확인합니다. Preview는 실제 변경이 아닙니다.
4. Operation workflow가 승인 조건을 충족해야 `apply_change`가 실행됩니다. idempotency key는 같은 요청 재시도에 같은 결과를 연결합니다.
5. `verify_service` 및 KPI 조회로 결과를 점검합니다. 상태 version이 달라졌거나 verify가 실패한 경우 상태를 확인하고 rollback 경로를 봅니다.

변경 제안은 agent output일 뿐 승인이나 실행이 아닙니다. Runner가 approval policy를 적용하고 MCP 도구 호출만으로 backend state가 바뀝니다. Preview token, idempotency, stale version 정책의 자세한 계약은 [BACKEND.md](../../../docs/BACKEND.md)를 기준으로 하세요.

## 오류를 해석하는 법

`ContractError`는 tool schema/domain 입력이 계약과 맞지 않음을, `UnknownToolError`는 안정된 tool 목록 밖 이름을 뜻합니다. `NotFoundError`는 요청한 장비·preview·change·ticket이 없음을 나타냅니다. `VersionConflictError`는 preview를 만든 뒤 네트워크 상태가 변했음을 나타내므로 새 상태를 다시 읽어야 합니다. `IdempotencyConflictError`와 `ChangeConflictError`도 임의 재시도하지 말고 현재 lifecycle과 key 사용을 확인하세요.

상위 진입점: [`services.py`](../services.py), [`protocols`](../protocols/README.md), [`ccs` 흐름](../README.md#한-건의-실행-흐름).
