# 함수 참조 읽는 법

[문서 목차](../README.md) · [전체 구조](../ARCHITECTURE.md) · [프로젝트 처음으로](../../README.md)

이 폴더는 “함수가 어디에 있고 무엇을 받는가?”를 찾는 사전입니다. 먼저 역할을 이해한 뒤 필요한 함수의 구현으로 이동하세요.

| 파일 | 내용 | 생성 방식 |
|---|---|---|
| [python_functions.md](python_functions.md) | 모든 Python 파일의 클래스·함수·메서드·중첩 handler, signature, 위치, docstring, 호출 표현 | Python AST |
| [web_functions.md](web_functions.md) | Python 문자열에 포함된 이름 있는 JavaScript 함수/arrow 선언 | 명시적 선언 패턴 |
| [function_inventory.json](function_inventory.json) | 같은 정보와 정규화한 source hash의 구조화 목록 | 같은 생성기 |

## 따라 읽기

1. [src/ccs README](../../src/ccs/README.md)에서 관심 있는 파일을 고릅니다.
2. 폴더 설명에서 그 함수가 전체 과정의 어느 역할인지 읽습니다.
3. 전체 참조의 module 링크로 이동합니다.
4. signature에서 입력·기본값을 보고 `소스 L...`로 구현을 엽니다.
5. 필요할 때만 호출 표현을 펼칩니다.

| 표기 | 뜻 |
|---|---|
| `self` | 현재 클래스 객체 |
| `async` / `await` | 다른 서비스의 응답 등을 비동기로 기다리는 함수/호출 |
| `*` 뒤 인자 | 이름을 붙여 전달하는 인자 |
| `**kwargs` | 추가 이름 인자 묶음 |
| `-> dict` | 반환값의 type annotation |
| `_helper` | 내부용 이름이라는 관례. 접근 권한 통제는 아님 |

## 정확성 범위와 갱신

Python 목록은 앱을 import하지 않고 AST로 수집합니다. 함수가 없는 파일도 포함합니다. 호출 표현은 실제 실행 순서·동적 구현체·HTTP 건너편 호출을 자동 확정하지 않습니다. 예를 들어 `backend.call()`의 구현체는 설정과 생성 코드를 함께 확인해야 합니다.

`normalized_sha256`은 UTF-8 BOM을 제거하고 줄바꿈을 LF로 읽은 텍스트의 hash입니다. Windows와 Git checkout 사이의 CRLF/LF 차이만으로 함수 문서를 오래됐다고 판정하지 않도록 합니다. 이것은 문서 동기화용 값이며 실험 manifest/seal의 **원본 파일 바이트 hash와 다른 기준**입니다. 실험 무결성 검사의 계산 방식은 바꾸지 않습니다.

JavaScript 목록은 이름 있는 선언을 대상으로 하며 익명 callback까지 재구성한 완전한 AST call graph는 아닙니다. 버튼과 API 연결은 [웹 흐름](../ARCHITECTURE.md#web-flow)에 설명합니다.

```powershell
python tools/generate_reference.py
python tools/generate_reference.py --check
```

첫 명령은 생성 문서를 갱신합니다. `--check`는 오래된 문서가 있는지만 검사하고 쓰지 않습니다. source line이 바뀌면 다시 생성하세요. API Key 파일은 생성 대상이 아닙니다.
