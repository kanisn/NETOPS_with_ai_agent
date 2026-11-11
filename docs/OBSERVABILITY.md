# 실행 중인 실험 관찰하기

이 문서는 실행 중인 Agent·도구 작업을 읽는 방법과 각 화면이 근거로 삼는 파일을 설명합니다. 큰 구성요소가 어떤 순서로 움직이는지는 [전체 구조와 함수 흐름](ARCHITECTURE.md), 브라우저 화면의 사용법은 [웹 콘솔 안내](WEB_CONSOLE.md)를 참고하세요.

## CLI에서 실시간 관찰하기

프로젝트 루트 PowerShell에서 무료 Mock 실행에 `--dashboard`를 추가하면 별도 브라우저 monitor가 열립니다.

```powershell
# Mock은 유료 API 없이 별도 process와 MCP/A2A 통신 경계를 실행합니다.
.\ccs.ps1 run --mode mock --faults W4 --seeds 1 --repeat 2 --dashboard

# 브라우저를 자동으로 열지 않고 접속 URL만 출력
.\ccs.ps1 run --mode mock --faults W4 --seeds 1 --dashboard --no-browser

# 모니터 대신 Console에 안전 요약만 표시 (기본값 compact)
.\ccs.ps1 run --mode mock --faults W4 --seeds 1 --progress compact

# 선택된 합성 장애에 대한 영어 요청 전달 예
.\ccs.ps1 run --mode mock --faults W4 --request 'File transfers to the internal server are unusually slow. Identify the cause and restore service.' --dashboard
```

`--dashboard` 없이 실행해도 Console에 `--progress` 설정에 따라 진행 요약이 표시됩니다.

| `--progress` 값 | Console 동작 | 유의사항 |
|---|---|---|
| `compact` | 기본값. 안전한 활동 요약을 표시 | 처음 관찰할 때 권장 |
| `detailed` | 선택적으로 허용한 activity payload 세부사항도 표시 | 요청·문서·도구 결과가 포함될 수 있으니 공유 로그에 복사하지 않음 |
| `off` | activity 진행 출력 생략 | run artifact와 최종 요약은 계속 저장 |

별도 monitor URL은 임의 capability token을 포함합니다. 같은 실행을 보는 사람에게 URL 전체를 안전한 방법으로 전달하고, 공개 issue/chat/문서에 붙이지 마세요. 이 문서에는 실제 접속 URL이나 token을 넣지 않습니다. 모니터는 기본적으로 `127.0.0.1`에만 열립니다.

### Live 실행은 유료 호출입니다

설정된 profile을 실제 provider에 요청하려면 `--mode live`가 필요합니다. 예시 명령은 문법 안내일 뿐 현재 문서 준비 중 실행한 명령은 아니며, Live는 API 비용을 발생시킬 수 있습니다. 현재 또는 과거 실제 LLM 결과를 해석할 때는 공개 요약 [RESULTS.md](RESULTS.md)의 실행 조건과 한계를 읽고, 실험을 시작하기 전에 누적 예산과 provider 설정을 확인하세요.

```powershell
# 이 명령은 구성된 provider에 실제 유료 API 요청을 보냅니다.
.\ccs.ps1 run --mode live --profile luna6 --faults W4 --seeds 1 --dashboard
```

## 화면에서 무엇을 볼 수 있나요?

| 관찰 대상 | 기록되는 근거 |
|---|---|
| 요청 접수 | 입력 요청, target, ticket, episode ID와 mock/live mode |
| Operation Agent | workflow phase, 선택한 작업, 진단 수신, 변경 선택, 승인/거부, 보고 |
| Runbook 검색 | 검색어, 반환된 문서와 metadata, 결과 개수 |
| Memory 검색·저장 | 이전 기록, 비활성/빈 결과의 구분, 초안/승인/저장 결과 |
| A2A 진단 위임 | Operation→Diagnosis payload, Diagnosis 수신, 원인·근거·변경안 응답 |
| Diagnosis Agent | 수행 단계, 선택한 조회, 실제 관측 근거, 결론 |
| MCP Network Tools | tool 이름·인자, 시도 시작/완료/실패, 결과와 소요 시간 |
| 변경·검증 | preview/apply/verify/rollback 및 ticket 갱신과 실행 결과 |
| 독립 판정 | Agent report와 별도로 저장된 Oracle utility/verify 결과 |

Episode와 Component 필터, 검색, 상태 필터를 사용해 기록을 좁힐 수 있습니다. 화면을 필터링하거나 닫아도 진행 중인 Agent 작업이나 망 상태는 바뀌지 않습니다. 구조도는 활동의 경로를 표시하지만 그 자체가 데이터베이스 변경 명령은 아닙니다.

화면 설명은 model이 실제 반환한 `reason`, `evidence`, `root_cause`, `proposed_change`와 기록된 도구 결과에서 만듭니다. Model이 반환하지 않은 설명을 UI가 대신 추론해 만들지 않습니다. 비공개 reasoning 원문/Chain-of-Thought를 activity 화면에 복사하지 않습니다. Mock의 선택은 고정된 검증 코드에 따른 값이지 실제 모델의 reasoning 증거가 아닙니다.

## 종료 후 다시 보기

Console이 출력한 run 경로를 `run_dir`로 사용해 `monitor.html`을 브라우저에서 열거나, 실행 artifact를 읽는 독립 loopback monitor를 시작할 수 있습니다.

```powershell
# 실제 경로를 자기 run 폴더로 바꿉니다. 예: local-data/runs/<run_id>
.\ccs.ps1 monitor 'local-data/runs/<run_id>' --open
```

정상 완료 run에는 self-contained `monitor.html` snapshot이 생성됩니다. 중단된 run도 보존 가능한 범위에서 부분 기록이 있을 수 있지만, 완료된 run처럼 모든 snapshot/seal이 있다는 뜻은 아닙니다. 이전 관찰 activity가 기록되기 전 생성된 오래된 실행에는 세부 timeline이 없을 수 있습니다. 이 화면은 과거 run을 수정하거나 재실행하지 않습니다.

## 어떤 파일에 무엇이 남나요?

| 파일/폴더 | 목적 | 보관 범위 |
|---|---|---|
| `activity/*.jsonl` | 사람이 확인할 수 있는, caller가 고른 활동 요약과 세부정보 | Restricted. 원문 요청·문서·도구 결과 포함 가능 |
| `monitor.html` | 활동을 검색/필터링해 보는 self-contained browser snapshot | Activity와 동일한 접근 제한 |
| `events/*.jsonl` | lifecycle crossing의 event metadata | Restricted disclosure 증거 |
| `blobs/*.json` | disclosure event가 가리키는 원본 payload | Restricted 원문 |
| `manifest.json` | 조건, 모델/provider 식별, source/config hash, artifact hash와 상태 | 실행 artifact. 공개 전에 세부정보 검토 |
| `report.html`, `summary.json` | 집계 결과, 비용 및 episode 결과 | 세부 로그보다 좁지만, 공유 전에 공개 정책에 맞는지 검토 |

`activity`는 `events`/`blobs`의 disclosure audit와 다릅니다. Activity는 사람이 보도록 골라진 요약이고, event/blob은 payload 전달 경계를 정확히 검사하기 위한 기록입니다. 둘 다 요청·Memory·도구 출력의 민감한 synthetic operational detail을 담을 수 있습니다. Git에 올리거나 공개할 자료로 사용하지 말고, [보안 안내](../SECURITY.md)의 제외 규칙을 확인하세요.

`manifest`의 artifact seal 검증은 기존 파일 hash와 event integrity를 읽기 전용으로 확인합니다. UI가 열린 순간마다 전체 파일을 다시 검사하는 것은 아닙니다. `COMPLETED`는 runner가 끝났다는 뜻입니다. 실제 복구 성공은 Oracle utility와 `verify_service` 근거를 같이 확인하세요. 중단 기록에는 완성된 seal이 없을 수 있습니다.

## 시간과 인과관계

Activity 화면은 event의 관측 시간을 기준으로 표시하고 `operation_id`를 이용해 한 작업의 시작/종료를 묶습니다. 여러 process의 시계 timestamp만으로 전체 인과 순서를 확정하지 않습니다. 엄밀한 process 간 event 관계는 `causation_event_id`, `parent_span_id`, logical order를 보존하고 검증하는 [계측 안내](INSTRUMENTATION.md)의 `validate_events`/`validate_and_merge` 경로로 확인합니다.

## 접근·검증 한계

독립 CLI monitor는 loopback 전용이고, Web Console도 기본은 localhost 전용입니다. Web Console LAN mode에는 명시적인 `--host`와 `--allow-network`가 필요하고 client, Host/Origin, token 검사가 추가됩니다. LAN 접속 예제와 한계는 [웹 콘솔 안내](WEB_CONSOLE.md#lan에서-접속-허용하기)를 보세요.

무료 Mock은 실제 별도 process, MCP/A2A transport, 화면 전달과 SQLite 합성망 동작을 확인하는 데 쓸 수 있습니다. 이것만으로 유료 provider의 판단 품질, 물리 네트워크나 Mininet 동작, Disclosure Protection 효과를 입증하지 않습니다. 현재 테스트 범위는 [VALIDATION](VALIDATION.md), 과거 LLM 결과 범위는 [RESULTS](RESULTS.md)에 정리됩니다.

