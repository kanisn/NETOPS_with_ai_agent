"""Operator-facing stories for the wired scenario catalog."""
CATALOG_ID = "wired-v1"
SCENARIOS = {
    "W1": {
        "title": {"ko": "중간 스위치가 멈췄어요", "en": "A switch has gone down"},
        "impact": {"ko": "업무 서버로 가는 주 경로가 끊겨 팀 전체의 접속이 멈췄습니다.", "en": "The primary path to the work server is interrupted, disconnecting the team."},
        "goal": {"ko": "장애 스위치를 확인하고 정상 대체 경로로 우회해 연결을 복구합니다.", "en": "Locate the failed switch and restore connectivity through a healthy backup path."},
        "technical": {"ko": "중간 스위치 장애 · 대체 경로 우회", "en": "Intermediate switch failure · path failover"}},
    "W2": {
        "title": {"ko": "사내 서버에 접속할 수 없어요", "en": "I cannot reach the company server"},
        "impact": {"ko": "네트워크 설정을 바꾼 뒤 업무 서비스에 연결되지 않습니다.", "en": "Work services are unreachable after a network configuration change."},
        "goal": {"ko": "잘못된 기본 게이트웨이를 찾아 올바른 경로로 다시 연결합니다.", "en": "Correct the default gateway and reconnect to the server network."},
        "technical": {"ko": "기본 게이트웨이 설정 오류", "en": "Incorrect default gateway"}},
    "W3": {
        "title": {"ko": "회의가 자꾸 끊겨요", "en": "Our video call keeps breaking up"},
        "impact": {"ko": "화상 회의 중 목소리가 빠지고 영상이 반복해서 끊깁니다.", "en": "Audio drops out and video repeatedly freezes during a meeting."},
        "goal": {"ko": "회의 경로의 패킷 손실 원인을 찾아 안정적인 전송을 회복합니다.", "en": "Find packet loss on the meeting path and restore reliable delivery."},
        "technical": {"ko": "전송 경로 패킷 손실", "en": "Packet loss on the service path"}},
    "W4": {
        "title": {"ko": "파일 전송이 너무 느려요", "en": "File transfers are painfully slow"},
        "impact": {"ko": "공유 서버로 자료를 옮기는 데 오래 걸려 업무가 지연됩니다.", "en": "Slow transfers to the shared server are delaying work."},
        "goal": {"ko": "잘못 적용된 대역폭 제한을 바로잡아 전송 처리량을 회복합니다.", "en": "Correct the bandwidth limit and restore transfer throughput."},
        "technical": {"ko": "대역폭 제한 설정 오류", "en": "Misconfigured bandwidth limit"}},
    "W5": {
        "title": {"ko": "대화가 한 박자씩 늦어요", "en": "Every conversation feels delayed"},
        "impact": {"ko": "영상과 음성이 늦게 도착해 회의 참석자들의 말이 겹칩니다.", "en": "Delayed audio and video cause participants to talk over one another."},
        "goal": {"ko": "경로에 추가된 지연을 줄이고 회의 트래픽의 응답성을 회복합니다.", "en": "Remove excessive path delay and restore responsive meeting traffic."},
        "technical": {"ko": "과도한 네트워크 지연", "en": "Excessive network delay"}},
    "N0": {
        "title": {"ko": "신고는 들어왔지만 지금은 정상이에요", "en": "An issue was reported, but all looks normal"},
        "impact": {"ko": "잠깐 끊겼다는 신고가 들어왔지만 현재 서비스는 정상입니다.", "en": "A brief interruption was reported, but the service is currently healthy."},
        "goal": {"ko": "현재 연결과 성능을 확인하고 불필요한 설정 변경 없이 종료합니다.", "en": "Verify connectivity and performance, then close without unnecessary changes."},
        "technical": {"ko": "정상 상태 · 변경 없음", "en": "Healthy service · no change"}},
}
