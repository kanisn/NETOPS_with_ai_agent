"""Real TCP/child-process checks plus workflow failure-path coverage, without paid APIs."""
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
import pytest

from tests.support_paths import isolated_ai_config, workspace_for
from ccs.runner import run,Workflow
from ccs.reporting import verify_seal

PROJECT=Path(__file__).resolve().parents[1]
WORK = workspace_for("test_runner_e2e")
AI_CONFIG = isolated_ai_config("test_runner_e2e")

def settings(**overrides):
    base=WORK/uuid.uuid4().hex;base.mkdir(parents=True)
    tree=ET.parse(PROJECT/'configs/system.xml')
    for key,value in overrides.items():tree.find('workflow').set(key,str(value))
    path=base/'system.xml';tree.write(path,encoding='utf-8')
    return base,path

@pytest.mark.asyncio
async def test_memory_chain_over_real_three_process_wire():
    base,config=settings()
    directory,summary=await run(config,AI_CONFIG,faults=['W2'],seeds=[2],repeat=2,output_root=base/'runs')
    assert summary['status']=='COMPLETED' and summary['successful_episodes']==2
    assert summary['api_calls']==0 and verify_seal(directory)['valid']
    events=[json.loads(line) for line in (directory/'events_merged.jsonl').read_text().splitlines()]
    assert {e['stage'] for e in events}=={'G1','G2','G3r','G3w','G4.call','G4.ret','G5.req','G5.res','G6'}
    for episode in ['episode-0001','episode-0002']:
        assert len({e['trace_id'] for e in events if e['episode_id']==episode})==1
    reads=[e for e in events if e['episode_id']=='episode-0002' and e['stage']=='G3r']
    records=json.loads((directory/reads[0]['payload_ref']).read_text())
    assert records and records[0]['scope_id']=='episode-0001'

@pytest.mark.asyncio
async def test_wrong_action_rolls_back_and_never_writes_memory(monkeypatch):
    async def wrong(*args,**kwargs):
        return {'target':'HOST-001','param':'bandwidth_mbps','value':35.0,'reason':'Deliberately wrong test action'}
    monkeypatch.setattr('ccs.runner.select_change',wrong)
    base,config=settings()
    directory,summary=await run(config,AI_CONFIG,faults=['W2'],seeds=[3],output_root=base/'runs')
    result=json.loads((directory/'episodes/episode-0001/result.json').read_text())
    assert result['outcome']=='ROLLED_BACK' and 'ROLLED_BACK' in result['workflow']
    assert not result['memory_written'] and summary['successful_episodes']==0
    oracle=json.loads((directory/'episodes/episode-0001/oracle.json').read_text())
    assert oracle['forbidden_changes']==[] and summary['integrity_valid']

@pytest.mark.asyncio
async def test_declined_change_has_no_side_effect_or_memory():
    base,config=settings(approval='deny')
    directory,summary=await run(config,AI_CONFIG,faults=['W1'],seeds=[4],output_root=base/'runs')
    result=json.loads((directory/'episodes/episode-0001/result.json').read_text())
    assert result['outcome']=='DECLINED' and not result['memory_written']
    oracle=json.loads((directory/'episodes/episode-0001/oracle.json').read_text())
    assert oracle['details']['actual_config_changes']==[] and summary['integrity_valid']

@pytest.mark.asyncio
async def test_diagnosis_budget_failure_is_finite_and_auditable():
    base,config=settings(diagnosis_tool_budget=1)
    directory,summary=await run(config,AI_CONFIG,faults=['W3'],seeds=[5],output_root=base/'runs')
    assert summary['status']=='FAILED' and summary['integrity_valid']
    result=json.loads((directory/'episodes/episode-0001/result.json').read_text())
    assert result['workflow'][-3:]==['FAILED','REPORTED','CLOSED']
    assert not result['memory_written']

def test_state_machine_rejects_out_of_order_apply():
    base,_=settings();state=Workflow(base/'workflow.jsonl')
    with pytest.raises(RuntimeError):state.transition('APPLIED')
