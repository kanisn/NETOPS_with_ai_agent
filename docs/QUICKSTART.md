# 처음 설치하고 무료로 실행하기

[문서 목차](README.md) · [프로젝트 처음으로](../README.md) · [웹 화면 안내](WEB_CONSOLE.md)

이 안내의 첫 목표는 **API Key 없이 Mock 실험을 한 번 끝내는 것**입니다. Mock은 AI 판단을 정해진 코드로 대신합니다. MCP/A2A 통신, 별도 프로세스, 설정 적용·검증·기록은 실제로 실행합니다.

## 1. 준비물 확인

현재 확인한 환경은 Windows PowerShell과 Python 3.14입니다. 프로젝트의 선언상 최소 Python은 3.11이지만 버전마다 의존성 지원이 다를 수 있어 처음에는 3.14를 권합니다. `requirements.lock`에는 Windows용 `pywin32`가 있으므로 이 안내를 그대로 Linux 설치 안내로 사용하지 마세요.

PowerShell에서 다음을 실행합니다.

```powershell
python --version
git --version
```

버전 문자열이 나오면 명령을 찾은 것입니다. `python`이 없거나 다른 버전을 가리키면 설치된 Python의 전체 경로를 `setup.ps1 -PythonExecutable`에 전달할 수 있습니다. Git은 GitHub에서 clone/commit/push할 때 필요합니다. 이미 파일을 받아 둔 경우 프로그램 실행 자체에 Git이 꼭 필요한 것은 아닙니다.

## 2. 올바른 폴더에서 시작

PowerShell의 현재 폴더는 `README.md`, `ccs.ps1`, `setup.ps1`이 보이는 저장소 루트여야 합니다.

```powershell
Get-Location
Get-ChildItem
```

GitHub clone을 사용할 때는 실제 저장소 URL을 넣습니다. 아래 주소는 예시입니다.

```powershell
$repoUrl = 'https://github.com/OWNER/REPOSITORY.git'
git clone $repoUrl
# 만들어진 저장소 폴더로 이동한 뒤 아래 단계를 진행합니다.
```

`04.Testbed`라는 폴더 이름 자체는 필수가 아닙니다. 코드가 자신의 위치를 기준으로 설정·소스를 찾습니다.

## 3. 작업 위치 정하기

가상환경은 Python 패키지를 따로 모아 두는 폴더입니다. 실험 결과는 프로그램을 실행할 때 만들어지는 데이터입니다. 둘 다 소스 코드와 구분합니다.

OneDrive 등 동기화 폴더에 소스가 있다면 환경·작업·실험 출력은 별도 작업 폴더에 두는 편이 좋습니다. 아래 예제는 D 드라이브를 사용합니다. 다른 PC에 D:가 없다면 쓰기 가능한 경로로 바꿉니다.

```powershell
$workRoot = 'D:\Codex\WorkingFiles\ccs-testbed'
$env:CCS_WORKING_ROOT = Join-Path $workRoot 'working'
$env:CCS_WEB_WORKSPACE = Join-Path $workRoot 'web'
$env:CCS_TEST_WORKING_ROOT = Join-Path $workRoot 'tests'
```

| 이름 | 쓰임 |
|---|---|
| `$workRoot` | 이 PowerShell 창에서 사용할 기준 경로 변수 |
| `CCS_WORKING_ROOT` | child process의 작업·임시 출력 위치 |
| `CCS_WEB_WORKSPACE` | 웹의 문서 목록·실행 index·Delay 제어 정보 |
| `CCS_TEST_WORKING_ROOT` | pytest가 만드는 DB·fixture 출력 위치 |

이 환경변수들은 현재 PowerShell 창에 적용됩니다. 새 창을 열면 다시 설정하거나 명령어 옵션으로 경로를 명시하세요. 웹의 과거 문서 목록을 이어 쓰려면 같은 workspace 경로를 사용해야 합니다.

## 4. 설치 스크립트 실행

```powershell
.\setup.ps1 -VenvPath (Join-Path $workRoot 'venv') -WorkDirectory (Join-Path $workRoot 'setup-cache')
```

이 명령은 다음 일을 순서대로 합니다.

1. 지정한 Python 가상환경이 없으면 만듭니다.
2. Python 최소 버전을 확인합니다.
3. `configs/ai.local.xml`이 없으면 `ai.example.xml`에서 만듭니다.
4. `configs/system.xml`이 없으면 `system.example.xml`에서 만듭니다.
5. 선택한 Python 경로를 `.ccs-python`에 저장합니다. 이 파일은 Git에서 제외됩니다.
6. `requirements.lock`의 고정 패키지를 설치합니다.

**이미 있는 로컬 XML은 덮어쓰지 않습니다.** 기존 Key, 결과 경로, 비용 장부를 초기화하지 않습니다. `-SkipDependencyInstall`은 필요한 패키지가 이미 설치된 환경을 재사용할 때만 사용합니다. 빈 가상환경에서 이 옵션을 쓰면 모듈을 찾지 못할 수 있습니다.

PowerShell이 스크립트를 차단하면 조직 정책과 파일 출처를 먼저 확인하세요. 허용되는 환경에서는 해당 PowerShell 창에 한해서 다음을 사용할 수 있습니다. 전체 PC의 정책을 임의로 바꿀 필요는 없습니다.

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 5. 설정 검사

```powershell
.\ccs.ps1 doctor
```

`configuration: valid`와 package 버전, 모델 이름, Key 존재 여부 등이 표시됩니다. Key 원문은 표시하지 않습니다. **`key_present: false`여도 Mock은 가능합니다.** `doctor`는 실제 모델 API가 계정에서 사용 가능한지 시험하지 않습니다.

설정 경로 규칙은 [configs README](../configs/README.md)에 자세히 있습니다.

| 설정 | 상대 경로 기준 |
|---|---|
| system XML의 output/runbooks/prompts | 저장소 루트 |
| AI XML의 ledger_path | 해당 AI XML이 들어 있는 폴더 |

## 6. 첫 Mock 실행

```powershell
.\ccs.ps1 run --mode mock --faults W4 --seeds 1 --output-root (Join-Path $workRoot 'runs')
```

| 옵션 | 뜻 |
|---|---|
| `run` | 실험을 실행 |
| `--mode mock` | 유료 모델 대신 정해진 판단 코드 사용 |
| `--faults W4` | 파일 전송 저하 상황 |
| `--seeds 1` | 합성 데이터 초기값 1 |
| `--output-root ...` | 이번 CLI 실행의 결과 폴더 |

Console의 `Run directory` 경로를 복사해 두세요. 그 아래에 `summary.json`, `report.html`, `manifest.json`, `episodes/` 등이 생성됩니다. 성공적인 기본 W4 Mock에서는 실행 완료와 복구 판정, API 호출 0을 확인할 수 있습니다.

`COMPLETED`는 실행이 마무리됐다는 뜻이고, `successful_episodes`와 Oracle utility는 실제 목표 달성 여부입니다. 오류가 나도 결과 폴더를 지우기보다 해당 기록으로 원인을 확인합니다.

## 7. 웹 화면 열기

```powershell
.\ccs.ps1 web --port 0 --workspace (Join-Path $workRoot 'web')
```

`--port 0`은 OS가 빈 포트를 고르게 합니다. `Web console:` 다음에 나온 URL 전체를 사용하세요. 마지막 `?token=...`도 포함해야 합니다. Key와 이 URL token은 서로 다른 것입니다. URL token은 이번 로컬 웹 서버 접속용이며 재시작하면 바뀝니다.

처음 화면에서는 다음 순서로 진행합니다.

1. **Mock**을 선택합니다. 화면에 API 호출 없음이 표시되는지 확인합니다.
2. 시나리오 **W4**, seed **1**, 반복 **1**을 선택합니다.
3. 빠른 확인에는 **No Delay**를 선택합니다.
4. **실험 시작**을 누릅니다.
5. 실시간 모니터링에서 Agent·도구·자료 검색 기록을 봅니다.
6. 완료 후 결과 분석에서 조치 전후와 독립 검증 결과를 봅니다.

웹의 결과 경로는 **로컬 `configs/system.xml`의 `paths.output_root`**입니다. `--workspace`는 결과 경로를 바꾸지 않습니다. 새 설정 예제의 기본값은 `local-data/runs`입니다. 웹 결과도 D:에 두려면 로컬 XML에서 해당 값만 실제 경로로 바꾸세요.

```xml
<paths output_root="D:/Codex/WorkingFiles/ccs-testbed/runs"
       runbooks="knowledge/runbooks" prompts="prompts" />
```

## 8. 종료와 재접속

웹 서버를 실행한 PowerShell에서 `Ctrl+C`를 누르면 종료합니다. 브라우저 탭만 닫는 것은 서버 종료와 다릅니다. 다시 실행할 때는 같은 `--workspace`를 사용하되 새로 출력된 URL로 접속하세요. 같은 workspace를 여러 서버에서 동시에 열지 마세요.

이전 결과의 무결성 검사는 다음처럼 합니다. 예시의 경로는 실제 Run directory로 바꿉니다.

```powershell
.\ccs.ps1 report 'D:\Codex\WorkingFiles\ccs-testbed\runs\실제_run_id'
```

<a id="live"></a>
## 9. 실제 LLM을 사용하려면

Live는 유료 API를 호출합니다. Mock 완료 후 다음을 준비합니다.

1. 사용할 공급사와 model profile을 고릅니다. 예제의 모델 ID·가격은 설정 예시이므로 계정 접근 가능 여부와 현재 단가를 확인합니다.
2. 로컬 환경변수 또는 Git에서 제외된 로컬 XML로 Key를 설정합니다. **Key를 README·소스·issue·채팅·로그에 복사하지 않습니다.**
3. `configs/ai.local.xml`의 누적 예산과 ledger 경로를 확인합니다. 장부를 바꾸면 과거 누적 비용이 자동으로 합쳐지지 않습니다.
4. `doctor`와 `budget`을 확인하고 1개 상황부터 실행합니다.

```powershell
.\ccs.ps1 budget
.\ccs.ps1 run --mode live --profile luna6 --faults W4 --seeds 1 --memory-off --output-root (Join-Path $workRoot 'runs')
```

XML에 Key 값이 있으면 환경변수보다 우선합니다. 모델을 선택할 수 있다는 사실과 해당 계정에서 실제 호출이 가능한지는 다릅니다. 공급사 실패 시 다른 모델로 자동 교체하지 않습니다. 자세한 Key 취급은 [SECURITY](../SECURITY.md), 모델/설정은 [configs README](../configs/README.md)를 참고하세요.

## 10. 자주 막히는 부분

| 증상 | 먼저 확인할 것 |
|---|---|
| Python environment is missing | setup 완료 여부, `.ccs-python` 경로, `CCS_PYTHON` |
| ModuleNotFoundError | 선택한 가상환경에 lockfile 설치 여부 |
| Invalid system/AI configuration | XML 태그·attribute 오타와 경로 기준. 예제와 비교 |
| could not bind / socket error 10013 또는 10048 | 지정한 포트 충돌·거부 가능. `--port 0`으로 실행 |
| 브라우저 403 | 새로 출력된 token 포함 주소인지, host를 바꾸지 않았는지 |
| 과거 기록이 안 보임 | 이전과 같은 `--workspace`인지 |
| Mock은 되지만 Live 실패 | Key·모델 접근·예산·usage 오류를 확인. Key 원문 출력 금지 |
| COMPLETED지만 복구 0건 | 실행 완료와 Oracle 목표 달성은 별개. episode 결과 확인 |

다음 읽기: [웹 콘솔](WEB_CONSOLE.md) → [전체 구조](ARCHITECTURE.md) → [테스트](../tests/README.md).
