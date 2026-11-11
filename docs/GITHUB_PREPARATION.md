# GitHub에 올리기 전 준비와 등록 순서

[처음으로](../README.md) · [문서 지도](README.md) · [설치·실행](QUICKSTART.md)

이 문서는 **소스와 설명서를 GitHub에 공유하는 과정**을 안내한다. GitHub는 코드를 보관하는 곳이며, 이 Python 웹 서버가 자동으로 실행되는 호스팅 서비스는 아니다. GitHub Pages에 파일을 올리는 것만으로 NetOps Studio의 서버·SQLite·Agent가 실행되지는 않는다.

## 1. 무엇을 공유하는가

| 구분 | GitHub 포함 | 이유 |
|---|---|---|
| `src/`, `tests/`, `tools/` | 포함 | 실행 코드, 검증 코드, 문서 생성·등록 전 점검 도구 |
| README와 공개 `docs/` | 포함 | 사용법·구조·검증 범위를 함께 전달 |
| `prompts/`, `knowledge/runbooks/` | 포함 | 실행에 필요한 공개 프롬프트와 6개 runbook |
| `configs/*.example.xml` | 포함 | 각 사용자가 자기 설정을 만들 수 있는 빈 Key 예제 |
| `requirements.lock`, `pyproject.toml` | 포함 | 재현 가능한 설치 버전과 프로젝트 정보. lock 파일은 빌드 찌꺼기가 아님 |
| `ccs.ps1`, `setup.ps1`, `.github/` | 포함 | Windows 실행·설치와 무료 CI 검사 |
| `configs/ai.local.xml`, `configs/system.xml`, `.ccs-python` | 제외 | 개인 Key·예산·저장 경로·Python 위치 |
| `.env`, 개인 `*.local.xml`, 인증서·개인키 | 제외 | 비밀정보 및 컴퓨터별 설정 |
| `.venv/`, 캐시, `build/`, `dist/` | 제외 | 설치·빌드할 때 다시 생성되는 산출물 |
| `local-data/`, `runs/`, `outputs/`, 로그·DB 및 sidecar | 제외 | 원시 실험 데이터, 대화, 내부망 정보, 비용 장부 |
| 개인 경로를 담은 과거 상세 검토 문서 4개 | 제외 | 로컬 원본은 보존하고 공개 요약은 [RESULTS](RESULTS.md)로 제공 |

실제 제외 규칙은 [`.gitignore`](../.gitignore), 줄바꿈 규칙은 [`.gitattributes`](../.gitattributes)에 있다. **제외는 파일 삭제가 아니다.** 원본은 로컬에 남는다. Git은 빈 폴더 자체를 저장하지 않는다.

## 2. 처음 알아둘 Git 용어

```text
작업 폴더 → git add → staging area → git commit → 로컬 이력
                                              ↓ git push
                                           GitHub 원격 저장소
```

| 용어 | 초보자 설명 |
|---|---|
| repository / repo | 소스와 변경 이력을 함께 보관하는 저장소 |
| working tree | 지금 편집하고 있는 파일들 |
| staging area / index | 다음 commit에 담기로 선택한 파일의 사본 |
| commit | 선택한 변경을 설명과 함께 로컬 이력에 기록 |
| branch | 독립적으로 변경을 이어 가는 이력의 이름 |
| remote / origin | GitHub 저장소 주소와 그 별칭 |
| push | 로컬 commit을 원격 저장소로 전송 |
| clone | 원격 저장소의 코드와 이력을 내 컴퓨터로 복사 |

파일을 고친 뒤 `git add`를 다시 하지 않으면 **이전 staging 사본**이 commit될 수 있다. 그래서 점검 도구는 작업 파일 검사와 실제 index 검사 두 가지를 제공한다.

## 3. 등록 전에 결정할 사항

1. **공개 범위:** 개인/조직 저장소와 Public/Private를 정한다. Public이면 누구나 파일과 공개 이력을 볼 수 있다.
2. **이용 허가:** 현재 `LICENSE`를 임의로 추가하지 않았다. 소유권·소속 기관 정책을 확인한 뒤 원하는 license를 선택한다. 공개한다고 자유로운 재사용 허가가 자동으로 생기지 않는다.
3. **공유할 결과:** 공개 요약만 포함한다. 원시 대화·실제망 데이터는 별도 검토 없이 추가하지 않는다.
4. **검사 환경:** 현재 안내는 Windows PowerShell과 Python 환경을 기준으로 한다. [호환성](COMPATIBILITY.md)을 먼저 확인한다.

## 4. 현재 폴더에서 등록 전 점검

PowerShell을 **이 README가 있는 `04.Testbed` 폴더**에서 연다. 저장소가 처음부터 없다면 `git init`을 한 번 사용한다. 이미 `.git`이 있는 폴더에서는 다시 만들 필요가 없다.

```powershell
git status --short
git remote -v
```

첫 명령은 변경 목록, 둘째는 원격 주소를 보여준다. `??`는 아직 Git이 추적하지 않는 파일이다. `fatal: not a git repository`일 때만 `git init` 후 다시 확인한다. 원격 주소가 비어 있으면 아직 연결하지 않은 상태다.

[Quickstart](QUICKSTART.md)의 설치를 마친 Python을 사용한다. 아래 예제 경로는 Quickstart에서 만든 환경과 같다.

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

성공 기준은 함수 문서 일치, repository 검사 `"passed": true`, pytest 실패 0건이다. 각 명령이 실패하면 다음 단계로 넘기지 말고 원인을 해결한다. 테스트는 실제 API Key 없이 실행한다. 자세한 범위는 [검증 안내](VALIDATION.md), [테스트 지도](../tests/README.md)에 있다.

함수 문서가 오래됐다면 아래로 갱신한 뒤 위 점검을 다시 한다.

```powershell
& $python tools/generate_reference.py
```

## 5. 올릴 파일을 눈으로 확인하고 선택

```powershell
git add --dry-run .
git status --short --ignored
```

`--dry-run`은 실제 staging 없이 포함될 파일 이름만 보여준다. `--ignored` 출력의 `!!`는 제외된 항목이다. 개인 XML, `.env`, 원시 결과, DB, venv가 업로드 후보에 들어가면 멈추고 제외 규칙을 수정한다. 파일 내용·Key를 터미널에 출력할 필요는 없다.

목록 확인 후 사용자가 등록을 진행할 때 실행한다.

```powershell
git add .
& $python tools/check_repository.py --staged
git diff --cached --stat
git status --short
```

`--staged`는 디스크의 최신 파일이 아니라 **Git index에 들어간 실제 내용**을 검사한다. `git diff --cached --stat`은 commit에 들어갈 파일별 변경량을 보여준다. 점검기는 Key 원문을 출력하지 않으며 의심 파일·줄 번호만 알린다. 자동 검사는 보조 수단이므로 결과 파일을 새로 포함할 때는 내용의 공개 적절성도 확인한다.

## 6. 첫 commit과 원격 연결

아래는 **사용자가 GitHub 등록을 진행할 때의 안내**다. 준비 작업 자체는 commit·push를 수행하지 않는다.

```powershell
git commit -m "Prepare NetOps testbed source and beginner guides"
git branch -M main
```

Git 사용자 이름·이메일이 없다는 오류가 나면 사용할 공개 작성자 정보를 결정해 이 저장소에만 `git config user.name`과 `git config user.email`로 설정한다. GitHub의 비공개 이메일 옵션도 선택할 수 있다. 컴퓨터 전체 설정을 바꾸는 `--global`은 필요한 경우에만 사용한다.

GitHub에서 빈 repository를 생성한다. 이미 로컬 README가 있으므로 원격 생성 화면에서 README·license·gitignore 자동 생성을 추가하면 처음부터 서로 다른 commit을 병합해야 할 수 있다. 원격 주소를 복사하고 다음의 예제 주소를 자신의 주소로 교체한다.

```powershell
git remote add origin https://github.com/OWNER/REPOSITORY.git
git remote -v
git push -u origin main
```

`origin`이 이미 있으면 새로 추가하지 말고 먼저 기존 주소가 맞는지 확인한다. URL에 토큰을 붙이지 않는다. 인증은 GitHub가 안내하는 로그인·credential manager를 사용한다. 원격에 기존 내용이 있다면 `--force`로 덮어쓰지 말고 이력을 확인한다.

## 7. 업로드 후 확인

- GitHub 첫 화면에서 루트 README, Mermaid 구조도, 상대 링크가 보이는지 확인한다.
- `src → ccs → 하위 패키지 → 함수 목록`을 따라가며 파일·함수 설명이 연결되는지 확인한다.
- Actions에서 `Offline baseline checks`가 통과하는지 확인한다. 현재 제공된 workflow와 **실제 원격 실행 결과는 별개**다.
- 별도 폴더에 clone하고 Quickstart의 설치 → doctor → Mock → 웹을 따라 한다.
- 개인 XML·원시 로그·DB·venv가 저장소 파일 목록에 없는지 확인한다.

## 8. 제외 규칙의 한계와 복구

`.gitignore`는 이미 commit된 파일을 이력에서 지우지 않는다. 추적 중인 개인 파일은 로컬 원본을 보존하면서 index에서 제외하는 절차가 필요하다. Key가 공개됐다면 파일을 지우는 것만으로 끝내지 말고 먼저 해당 Key를 폐기·재발급한다. [보안 안내](../SECURITY.md)를 참고한다.

GitHub 웹 화면에 폴더 전체를 끌어 올리는 방식은 이 문서의 Git 후보·index 검사를 거치지 않는다. 이 저장소는 위 Git 명령 순서로 등록하는 것을 권장한다.

공식 참고: [GitHub 파일 제외](https://docs.github.com/en/get-started/git-basics/ignoring-files), [저장소 운영 권장 사항](https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories), [파일 업로드와 비밀정보 주의사항](https://docs.github.com/en/repositories/working-with-files/managing-files/adding-a-file-to-a-repository).
