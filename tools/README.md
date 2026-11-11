# 저장소 관리 도구

[프로젝트 처음으로](../README.md) · [문서 목차](../docs/README.md) · [관리 도구 함수](../docs/reference/python_functions.md#tools)

이 스크립트는 Agent 실험과 별개입니다. 유료 API를 호출하지 않고 문서를 만들거나 공개할 파일을 확인합니다.

| 파일 | 역할 | 함수 흐름 |
|---|---|---|
| [generate_reference.py](generate_reference.py) | source의 함수 참조 생성 | `inventory` → `symbols`/`direct_calls` → `build_python_reference`/`web_inventory` → `generate` |
| [check_repository.py](check_repository.py) | 공개 후보·credential 의심 패턴·문서 링크·README 확인 | `git_files` → `audit` → `main` |

## 함수 문서 관리

```powershell
python tools/generate_reference.py
python tools/generate_reference.py --check
```

`inventory()`가 파일을 모으고, `symbols()`가 정의를 읽고, Markdown builder가 설명용 목록으로 바꿉니다. 앱을 import하지 않아 서버나 실제 실험을 시작하지 않습니다. `--check`는 파일을 변경하지 않습니다.

## 공개 전 검사

```powershell
python tools/check_repository.py
# git add 후 실제 index 내용을 확인합니다.
python tools/check_repository.py --staged
```

기본 모드는 추적 중인 파일과 ignore되지 않은 새 파일의 현재 내용을 봅니다. `--staged`는 Git index의 blob을 읽습니다. Key를 stage한 뒤 작업 파일에서만 지운 경우도 구분할 수 있습니다. 검출된 값은 출력하지 않고 파일명·행 번호·종류만 알려줍니다.

검사는 파일을 stage/commit/push하지 않습니다. 실제 local 설정은 읽지 않으며, 해당 이름이 추적 대상으로 들어오면 파일명만으로 문제를 보고합니다. 이 도구는 알려진 패턴과 링크를 보는 보조 수단이지 모든 secret·과거 history를 검증하는 완전한 보안 도구는 아닙니다.

각 함수의 전체 입력과 정의 위치는 [관리 도구 함수 목록](../docs/reference/python_functions.md#tools)에 있습니다.
