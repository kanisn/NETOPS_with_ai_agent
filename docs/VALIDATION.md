# 검증 방법과 결과를 읽는 법

[처음으로](../README.md) · [테스트 파일 지도](../tests/README.md) · [실제 LLM 결과](RESULTS.md)

**코드 검사, Mock 실행, 실제 모델 실험, 브라우저 확인은 서로 다른 증거다.** 어느 하나가 통과했다고 나머지까지 검증한 것으로 설명하지 않는다.

## 1. 검사별 의미

| 검사 | 무엇을 확인하는가 | 확인하지 않는 것 |
|---|---|---|
| 함수 문서 `--check` | 실제 AST·웹 선언과 공개 함수 문서가 같은지 | 알고리즘의 정답성 |
| repository 검사 | Git 후보·index의 민감 파일 패턴, 상대 링크, 폴더 README | 모든 비밀정보의 완전 탐지 |
| 단위·계약 테스트 | schema, config, budget, backend, protocols, 예외 경계 | 실제 모델 품질 |
| Mock E2E | 역할·MCP/A2A·DB·저장·Oracle까지 연결되는지 | 유료 API 응답의 정확도 |
| 웹 HTTP smoke | 서버 시작·인증·초기 응답·종료 | 화면의 모든 클릭·모바일·레이아웃 |
| 브라우저 확인 | 실제 표시·전환·상호작용 | 대규모 성능·보안 인증 |
| Live 실험 | 해당 모델·조건·표본에서의 실제 결과 | 다른 모델·실망·미측정 조건의 성능 |

## 2. 안전하게 재현하는 명령

먼저 [Quickstart](QUICKSTART.md)로 설치한다. 테스트 결과와 scratch는 원본 실험 출력과 분리한다.

```powershell
$workRoot = 'D:\Codex\WorkingFiles\ccs-testbed'
$python = Join-Path $workRoot 'venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:CCS_WORKING_ROOT = Join-Path $workRoot 'working'
$env:CCS_TEST_WORKING_ROOT = Join-Path $workRoot 'tests'
$env:TEMP = Join-Path $workRoot 'scratch'
$env:TMP = $env:TEMP
$env:TMPDIR = $env:TEMP
New-Item -ItemType Directory -Path $env:TEMP -Force | Out-Null

& $python tools/generate_reference.py --check
& $python tools/check_repository.py
& $python -B -m pytest -q --basetemp "$env:CCS_TEST_WORKING_ROOT\pytest-work"
```

`pytest --basetemp`는 그 테스트용 경로를 정리하고 재사용한다. 실제 결과나 보관 문서가 있는 경로를 넣지 않는다. 일부 테스트도 `tests/support_paths.py`가 정한 자기 전용 폴더를 초기화하므로 `CCS_TEST_WORKING_ROOT`는 검증 전용으로 지정한다.

선택 실행 예시는 [tests README](../tests/README.md)에 있다. 시스템 동작 변경은 관련 검사 후 전체 suite를 실행한다. 문장 수정만 했다면 링크·내용 검사가 우선이다.

## 3. 공개 준비 검증 기록

2026-11-11 GitHub 공개 준비는 Windows와 기존 고정 dependency 환경에서 수행한다. 공개 가능한 파일만 모은 별도 checkout에서 `ai.example.xml`과 `system.example.xml`을 로컬 설정으로 복사하여 개인 설정 없는 실행을 확인한다.

| 항목 | 판정 기준 |
|---|---|
| 전체 offline suite | 실패 0, skip 사유 구분 |
| 새 checkout doctor | Key 없이 시작 가능, 의존성·설정 검사 정상 |
| Mock | 실제 provider API 0, Oracle·진단·완료 상태 확인 |
| 웹 | 자동 포트에서 HTTP 정상 응답, runbook 6개 초기화, 정상 종료 |
| 공개 점검 | 제외 파일 후보 유입 0, 내부 링크 오류 0, 함수 문서 최신 |
| 원본 보존 | 개인 설정·기존 결과 변경 없음, 실제 저장소 staging·commit·push 없음 |

독립 검증 결과:

- **전체 suite: 208 passed, 1 skipped** (Windows, Python 3.14.7). skip은 Windows directory-symlink capability 검사다.
- 개인 Key가 없는 공개 checkout에서 `doctor` exit 0, 설정 정상과 두 provider의 Key 없음 확인.
- W4 seed 1 Mock: `COMPLETED`, 목표 달성 1/1, 진단 정답 1/1, API 0, 비용 0, integrity 유효.
- 웹 HTTP smoke: token을 사용한 루트 페이지 200, HTML 응답, runbook 6개 초기화, 정상 종료. 이번 검사는 전체 브라우저 UI·모바일 화면 확인은 아니다.
- 최초 공개 checkout 검사에서 발견한 XML 인코딩 의존성과 Windows HTTP 테스트의 연결 종료 타이밍 문제를 수정한 뒤 전체 suite를 다시 통과했다.

실행 로그는 로컬 검증 작업 폴더에 보존하며 GitHub에는 원시 로그를 포함하지 않는다. GitHub Actions workflow는 제공하지만 아직 원격 실행 결과는 없다. 함수 문서·링크·공개 파일 범위는 별도의 repository 점검으로 확인한다.

## 4. 실험 성공의 판정

| 지표/파일 | 읽는 법 |
|---|---|
| `COMPLETED` | 실행과 저장 절차가 완료됨. 단독으로 장애 복구를 뜻하지 않음 |
| `FAILED` / `ABORTED` | 실행 오류·중단. 부분 episode가 성공해도 완료 집단에 합치지 않음 |
| Oracle utility | 최종 backend 상태와 허용 변경을 독립 기준으로 평가 |
| diagnosis accuracy | 정답 원인과 진단을 비교 |
| N0의 apply 횟수 | 정상 상태에서 불필요한 변경을 하지 않았는지 |
| API usage/cost | 실제 provider 요청·응답의 usage와 비용 장부. Mock은 API 0 |
| integrity/seal | 저장된 결과의 누락·변경 탐지. 운영체제·계정에 대한 보안 서명은 아님 |

결과 파일 구조는 [계측 안내](INSTRUMENTATION.md), 모니터의 전달 내용은 [관측 안내](OBSERVABILITY.md)를 참고한다. `report`와 `compare`의 결과 검증은 기존 run을 읽기 전용으로 확인해야 한다. 실패 결과를 새 성공 summary로 덮어쓰지 않는다.

## 5. 해석의 경계

- 이번 공개 준비 테스트는 실제 모델 API를 호출하지 않는다.
- 과거 Live 결과는 [RESULTS](RESULTS.md)의 조건과 표본 범위에서만 읽는다.
- Windows symlink 권한에 따른 skip을 pass로 세지 않는다.
- dependency 설치 성공과 HTTP 200만으로 모든 UI를 확인했다고 하지 않는다.
- 현재 SQLite backend의 KPI는 합성이며 Mininet·실제 패킷 성능 증거가 아니다.

