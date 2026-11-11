# Test workflow

`test.yml`은 저장소의 offline 회귀검사입니다. Windows runner에서 Python 3.14와 `requirements.lock`을 사용합니다. 설정 단계는 runner가 제공하는 `RUNNER_TEMP` 아래에 scratch, subprocess work, test work, pip cache를 지정하고 keyless public config를 ignore 대상 local config로 복사합니다. 검사 순서는 `generate_reference.py --check`, `check_repository.py`, pytest입니다. API key는 비우며 모델 API를 호출하지 않습니다. 어느 검사든 실패하면 workflow도 실패합니다.
