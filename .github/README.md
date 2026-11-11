# GitHub 자동 검사

`workflows/test.yml`은 push와 pull request마다 Windows runner에서 실행됩니다. 현재 runtime lock에는 Windows 의존성인 `pywin32`가 포함되어 있어 Linux runner는 선언하지 않습니다.

작업은 고정된 Python 버전을 준비하고 `requirements.lock`을 설치한 다음 참조자료 검사, 저장소 검사, pytest 회귀검사를 실행합니다. `RUNNER_TEMP` 아래에 `CCS_WORKING_ROOT`, `CCS_TEST_WORKING_ROOT`, pip cache, `TEMP`, `TMP`, `TMPDIR`을 둡니다. public XML 예제를 ignore 대상 local 설정으로 복사하고, provider key 환경변수는 빈 값으로 설정합니다. LLM API는 호출하지 않습니다.
