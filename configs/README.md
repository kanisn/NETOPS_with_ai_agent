# 새 clone용 설정 파일

프로그램은 `configs/ai.local.xml`과 `configs/system.xml`을 기본 설정으로 읽습니다. 배포 가능한 기본값은 `ai.example.xml`과 `system.example.xml`입니다. `setup.ps1`은 실제 설정 중 없는 파일만 예제에서 만들며, 이미 있는 파일은 덮어쓰지 않습니다.

## 빠른 시작

Windows PowerShell에서 프로젝트 폴더로 이동해 가상환경을 D:에 만들고 실행합니다.

```powershell
.\setup.ps1 -VenvPath 'D:\Codex\WorkingFiles\ccs-testbed\venv'
.\ccs.ps1 doctor
.\ccs.ps1 run --mode mock --faults W4 --seeds 1
.\ccs.ps1 web
```

다른 드라이브에서 사용하려면 `-VenvPath`로 쓰기 가능한 경로를 지정합니다. 프로젝트 안의 무시 대상 `.venv`를 사용하려면 `-VenvPath (Join-Path $PWD '.venv')`를 전달하세요. 이미 필요한 패키지가 설치된 Python 가상환경을 선택하면 `-SkipDependencyInstall`로 설치 단계를 건너뛸 수 있습니다. setup scratch와 pip cache는 `-WorkDirectory` 또는 `CCS_WORKING_ROOT` 아래에 둡니다. Python 3.11 이상이 필요합니다. `setup.ps1`은 고정된 `requirements.lock`을 설치하고, 최신 버전 일괄 업그레이드는 하지 않습니다.

## AI 설정: `configs/ai.local.xml`

`ai.example.xml`에는 API key 값이 없으며 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`라는 환경변수 이름만 있습니다. Mock 실행과 웹 화면은 API key 없이 동작합니다. Live 실행은 선택한 공급사의 key가 필요하며 실제 API 비용이 발생합니다.

- `active_profile`: 기본 provider/model 조합입니다.
- `providers/provider`: provider별 key 환경변수 이름입니다. key 자체를 XML이나 저장소에 넣지 마세요.
- `profiles/profile`: provider, 모델 ID, reasoning effort, 출력 상한 및 비용표입니다.
- `agents`: Operation/Diagnosis Agent별 profile입니다. 값이 비어 있으면 `active_profile`을 사용합니다.
- `requests`: API timeout, schema 재시도 및 입력 크기 제한입니다.
- `budget`: 누적 비용 상한과 SQLite 장부 파일입니다. 예제의 장부는 프로젝트 `local-data/cost-ledger.sqlite`에 둡니다.

설정 파일에 직접 입력한 값은 환경변수보다 우선할 수 있습니다. 개인 key가 들어간 `ai.local.xml`은 ignore 규칙으로 보호합니다. 공유 전에 `git status`와 `git check-ignore`로 추적 여부를 확인하세요. 기존 local XML은 setup에서 건드리지 않으며 기존 장부도 복사·초기화하지 않습니다.

## 시스템 설정: `configs/system.xml`

`system.example.xml`은 현재 다른 실행 설정을 유지하고 결과 경로를 `local-data/runs`로 지정한 공개 템플릿입니다. 프로그램은 경로를 프로젝트 루트 기준으로 해석합니다.

- `paths`: 실행 결과, runbook, prompt 경로입니다.
- `network`: localhost 주소, tool/diagnosis port, process 및 request timeout입니다.
- `workflow`: 진단 도구 호출 수, context/agent 단계 상한, 재시도, 승인, Memory 및 검색 개수입니다.
- `experiment`: 기본 seed, fault, difficulty, target입니다.
- `protection`: 비교 기준 mode입니다.

기본 결과는 `local-data/runs/<run_id>`에 생성됩니다. 실행 폴더에는 prompt, 요청, 도구 응답, model 응답 등 제한된 자료가 포함될 수 있습니다. 결과와 비용 장부는 로컬 데이터이므로 저장소에 추가하지 마세요. `local-data/`, `runs/`, `outputs/`, SQLite, log, pid 파일은 `.gitignore` 대상입니다.

## 지원 범위와 Python 선택 순서

현재 bootstrap은 Windows PowerShell과 Python 3.11 이상을 대상으로 합니다. `requirements.lock`에 Windows용 `pywin32`가 있으므로 Linux 지원을 주장하지 않습니다. `ccs.ps1`은 다음 순서로 Python을 찾습니다.

1. `CCS_PYTHON` 환경변수
2. setup이 기록한 ignore 대상 `.ccs-python` 경로 파일
3. 프로젝트 `.venv`
4. PATH의 `python`

기존 로컬 환경을 계속 사용하도록 현재 checkout에는 `.ccs-python`을 한 번 기록할 수 있습니다. 이 포인터 파일은 Git에서 제외되며 public launcher에는 사용자별 절대경로를 넣지 않습니다.

직접 Python을 지정할 때는 다음처럼 사용합니다.

```powershell
$env:CCS_PYTHON = 'D:\MyEnvironments\ccs\Scripts\python.exe'
.\ccs.ps1 doctor
```

PowerShell을 실행할 수 없는 환경에서는 같은 Python으로 `-m ccs`를 실행하고 `PYTHONPATH`를 `src`로 지정합니다. GitHub Actions는 Windows에서 고정 의존성을 설치하고 API key 없이 무료 pytest 회귀검사를 실행합니다.
