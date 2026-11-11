"""Observe real child processes without any paid model request."""
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET

import pytest

from tests.support_paths import isolated_ai_config, workspace_for
from ccs.runner import run
from ccs.reporting import verify_seal

PROJECT = Path(__file__).resolve().parents[1]
WORK = workspace_for("test_observability_e2e")
AI_CONFIG = isolated_ai_config("test_observability_e2e")


@pytest.mark.asyncio
async def test_activity_spans_real_memory_chain_and_is_sealed():
    from ccs.monitor import read_activity
    directory = WORK / uuid.uuid4().hex
    directory.mkdir(parents=True)
    observed_before_completion = []
    def created(path):
        observed_before_completion.extend(read_activity(path))
        assert json.loads((path / 'manifest.json').read_text())['status'] == 'RUNNING'
    run_dir, summary = await run(PROJECT/'configs/system.xml', AI_CONFIG,
        faults=['W4'], seeds=[1], repeat=2, output_root=directory/'runs',
        request_override='Video conferencing quality degraded; identify the cause and restore service.',
        on_created=created)
    assert summary['status'] == 'COMPLETED' and summary['successful_episodes'] == 2
    assert summary['api_calls'] == 0
    assert any(e['action'] == 'run' and e['status'] == 'started' for e in observed_before_completion)
    events = read_activity(run_dir)
    assert len({e['event_id'] for e in events}) == len(events)
    assert {'runner','operation','diagnosis','runbook','memory','mcp','a2a'} <= {e['component'] for e in events}
    assert any(e['action']=='request_received' and 'Video conferencing' in json.dumps(e['details']) for e in events)
    for ep in ['episode-0001','episode-0002']:
        local = [e for e in events if e['episode_id']==ep]
        handoff = next(e for e in local if e['action']=='delegate_diagnosis' and e['status']=='started' and e['component']=='a2a')
        response = next(e for e in local if e['operation_id']==handoff['operation_id'] and e['status']=='succeeded')
        assert response['details']['response']['root_cause'] == 'bandwidth_limit_misconfiguration'
        assert response['details']['response']['evidence']
        saved = next(e for e in local if e['component']=='memory' and e['action']=='write' and e['status']=='succeeded')
        assert saved['details']['record']['verified_outcome']=='verified'
    second = [e for e in events if e['episode_id']=='episode-0002' and e['component']=='memory' and e['status']=='succeeded']
    assert any('episode-0001' in json.dumps(e['details']) for e in second)
    serialized=json.dumps(events)
    assert 'raw_response' not in serialized and 'encrypted_content' not in serialized
    assert (run_dir/'monitor.html').is_file()
    manifest=json.loads((run_dir/'manifest.json').read_text())
    assert 'monitor.html' in manifest['artifact_hashes']
    assert any(k.startswith('activity/') for k in manifest['artifact_hashes'])
    assert verify_seal(run_dir)['valid']


@pytest.mark.asyncio
async def test_observed_failure_is_terminal_and_memory_is_not_saved():
    from ccs.monitor import read_activity
    directory=WORK/uuid.uuid4().hex
    directory.mkdir(parents=True)
    tree=ET.parse(PROJECT/'configs/system.xml')
    tree.find('workflow').set('diagnosis_tool_budget','1')
    configuration=directory/'system.xml'
    tree.write(configuration,encoding='utf-8')
    run_dir,summary=await run(configuration,AI_CONFIG,faults=['W3'],seeds=[1],output_root=directory/'runs')
    assert summary['status']=='FAILED'
    events=read_activity(run_dir)
    assert any(e['action']=='delegate_diagnosis' and e['status']=='failed' for e in events)
    assert events[-1]['component']=='runner' and events[-1]['action']=='run' and events[-1]['status']=='failed'
    assert not any(e['component']=='memory' and e['action']=='write' and e['status']=='succeeded' for e in events)
    assert (run_dir/'monitor.html').is_file() and verify_seal(run_dir)['valid']
