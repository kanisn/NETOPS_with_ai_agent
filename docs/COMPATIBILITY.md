# 확인한 런타임과 API 호환성

이 문서는 세 가지를 구분합니다. **최소 Python 버전은 project metadata의 선언**, **Python 3.14.7은 확인한 Windows 환경**, **dependency version은 `requirements.lock`의 고정 설치 입력**입니다. 하나의 버전으로 확인했다고 모든 Python/OS 조합이 지원된다고 볼 수 없습니다.

## Python과 OS 범위

| 항목 | 값 | 해석 |
|---|---|---|
| 선언된 최소 Python | Python 3.11 이상 (`pyproject.toml`의 `requires-python`) | packaging metadata가 허용한다고 선언한 하한. 3.11 전체 세부 버전을 모두 검증했다는 뜻은 아님 |
| 직접 확인한 Windows Python | Python 3.14.7 | `setup.ps1`, project dependency/runtime와 Mock 실행 검증 기준으로 사용 |
| GitHub Actions workflow 설정 | `windows-latest`, Python 3.14 | offline 검사 자동화용 설정. workflow 파일의 존재만으로 원격 GitHub run이 실행됐다고 주장하지 않음 |
| Linux/macOS | 검증 범위 밖 | `requirements.lock`에 `pywin32==312`가 포함되어 있어 Linux/macOS 지원을 주장하지 않음 |

처음 설치한다면 Windows PowerShell에서 [빠른 시작](QUICKSTART.md)의 `setup.ps1` 절차를 따르세요. 다른 Python/OS 조합은 실행이 될 수 있어도 이 프로젝트에서 확인한 조합과 구별하고 별도로 검사해야 합니다.

## 주요 고정 dependency

정확한 전체 dependency 목록은 저장소의 [`requirements.lock`](../requirements.lock)입니다. 아래 항목은 API·실행 경계를 이해하는 데 중요한 package입니다.

| Package | 고정 버전 | 사용하는 부분 |
|---|---:|---|
| `mcp` | `2.2.0` | MCP Streamable HTTP server/client |
| `a2a-sdk[http-server]` | `1.1.5` | A2A AgentCard, client, JSON-RPC task server |
| `openai` | `3.19.2` | native OpenAI Responses API adapter |
| `anthropic` | `1.8.0` | native Anthropic Messages API adapter |
| `httpx` | `0.28.1` | A2A HTTP client transport |
| `httpx2` | `2.13.1` | MCP 2.x HTTP transport. `httpx`와 별도 package/import |
| `pydantic` | `2.13.5` | Agent request/result와 로컬 설정의 schema validation |
| `uvicorn` | `0.54.0` | local MCP/A2A child application server |
| `pywin32` | `312` | Windows process/console 동작용 dependency |
| `pytest` / `pytest-asyncio` | `9.1.1` / `1.4.0` | offline 회귀검사 |

`requirements.lock`은 설치의 재현성을 위한 고정 입력입니다. 새 버전 전체를 무작정 업그레이드하지 않습니다. SDK 변경은 dependency만 바꾸는 일이 아니라 protocol wire contract와 regression coverage를 다시 확인해야 하는 compatibility change입니다.

## LLM provider 호출 경계

| Provider | 현재 adapter | 문서로 확인할 점 |
|---|---|---|
| OpenAI | `AsyncOpenAI.responses.create`를 쓰는 Responses API 경로 | 이전 GPT-6 Luna Live 결과는 역사적 실행입니다. 실행 조건과 해석 범위는 [공개 결과 요약](RESULTS.md)을 봅니다. |
| Anthropic | `AsyncAnthropic.messages.create`를 쓰는 Messages API 경로 | adapter/config와 offline SDK 계약은 있지만, 이 문서 준비 시 Claude API key가 없어 Live 호출은 검증되지 않았습니다. |
| Mock | 고정된 offline 판단 경로 | API 요청 없이 Runner와 실제 MCP/A2A protocol 경계, 합성 SQLite network workflow를 확인하는 데 사용 |

**이번 GitHub/docs 준비 작업은 유료 provider API 호출을 하지 않았습니다.** 공개 결과 문서에 적힌 과거 OpenAI usage는 현재 설정의 재호출이나 이번 변경의 검증이 아닙니다. 모델 이름/config가 있다는 것만으로 현재 계정에서 해당 모델을 사용할 수 있다고 보증하지 않습니다. 실제 Live 실행은 비용이 발생할 수 있으므로 [Quickstart의 Live 절차](QUICKSTART.md#live)를 보고 설정된 누적 예산과 Key를 먼저 확인하세요. Key는 환경변수 또는 Git에서 제외된 `ai.local.xml`에만 보관하며 Git 추적 파일에 넣지 않습니다.

## 응답 형식과 오류 처리

- OpenAI function-call history를 보낼 때 API alias 기준으로 `by_alias=True, exclude_none=True`를 적용하고, 공급사가 돌려주는 encrypted reasoning content는 protocol history 보존에 필요한 범위에서 다루되 사람이 읽을 수 있는 Chain-of-Thought로 해독하지 않습니다.
- 도구 호출과 자유형 `evidence`/`context` object를 Pydantic contract로 확인합니다. 모든 도구에 OpenAI strict Structured Outputs를 일괄 적용하지 않습니다.
- schema가 맞지 않으면 제한된 횟수의 repair feedback 뒤 오류 상태로 마칩니다. 잘못된 provider 응답을 임의로 성공 결과로 만들지 않습니다.
- A2A idempotency cache는 Diagnosis server process lifetime 동안 유지됩니다. SQLite network change idempotency key와 결과는 backend DB에 저장되므로 서로 다른 보존 범위입니다.
- Provider adapter, MCP/A2A transport, timeout/error type 설명은 [PROTOCOLS.md](PROTOCOLS.md)에 있습니다.

## 검증 범위 읽는 법

설치 성공은 Mock/Live API 사용 가능성이나 research result를 검증하지 않습니다. Windows offline suite는 provider Key 없이 실행되며 MCP/A2A SDK 계약, schema, event/run artifact 등을 확인합니다. 과거 실제 LLM 결과는 source/config snapshot과 해당 run의 usage/Oracle evidence로 판독하고, 현재 코드에 대한 Live 성능 주장은 별도 실행 없이는 하지 않습니다. GitHub Actions 설정은 Windows Python 3.14에서 offline 검사하도록 구성했으며 원격 workflow 결과는 해당 GitHub run을 확인해야 합니다.

다음 문서를 함께 읽으세요.

- [QUICKSTART.md](QUICKSTART.md): 설치·무료 Mock·선택적 Live 절차
- [PROTOCOLS.md](PROTOCOLS.md): MCP/A2A SDK와 HTTP/wire 경계
- [RESULTS.md](RESULTS.md): 과거 공개 가능한 Live 결과와 조건·한계
- [VALIDATION.md](VALIDATION.md): 실제 검사 방법과 기록


