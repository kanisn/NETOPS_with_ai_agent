from copy import deepcopy
import json
import os
from pathlib import Path
import uuid
import pytest

from tests.support_paths import workspace_for
from pydantic import ValidationError
from ccs.config import load_ai,load_system
from ccs.reporting import comparison_identity
from ccs.contracts import ProposedChange
from ccs.agent_runtime import select_change
from ccs.llm import ToolCall

ROOT=Path(__file__).resolve().parents[1]
WORK = workspace_for("test_review_regressions")

def work():
    p=WORK/uuid.uuid4().hex;p.mkdir(parents=True);return p

def comparison_fixture(path,config,scenario_hash='same-scenario'):
    (path/'effective-config.json').write_text(json.dumps(config),encoding='utf-8')
    manifest={'source_hashes':{'code':'same-code'},'seeds':[1],'faults':['W4'],'repeat':1,'network_backend':'sqlite',
        'episodes':[{'episode_id':'episode-0001'}],'artifact_hashes':{'episodes/episode-0001/scenario.restricted.json':scenario_hash}}
    return comparison_identity(path,manifest)

@pytest.mark.parametrize('key,value',[('target','HOST-002'),('difficulty','L3'),('memory_enabled',False)])
def test_different_execution_settings_not_paired(key,value):
    config={'system':load_system(ROOT/'configs/system.xml').public(),'ai':load_ai(ROOT/'configs/ai.example.xml').public(),'profile_override':None}
    initial=comparison_fixture(work(),config)
    changed=deepcopy(config);changed['system'][key]=value
    assert initial!=comparison_fixture(work(),changed)

def test_custom_request_and_profile_generation_settings_not_paired():
    config={'system':load_system(ROOT/'configs/system.xml').public(),'ai':load_ai(ROOT/'configs/ai.example.xml').public(),'profile_override':None}
    initial=comparison_fixture(work(),config)
    assert initial!=comparison_fixture(work(),config,'different-request-scenario')
    changed=deepcopy(config);changed['ai']['profiles']['luna6']['max_output_tokens']=3600
    assert initial!=comparison_fixture(work(),changed)
    # Model-only changes are the intended comparison axis, not an accidental condition mismatch.
    changed=deepcopy(config);changed['ai']['profiles']['luna6']['model']='another-model'
    assert initial==comparison_fixture(work(),changed)

def test_proposed_change_rejects_nonexistent_route_parameter():
    with pytest.raises(ValidationError):ProposedChange(target='LINK-001-P',param='route',value='10.0.1.1')

@pytest.mark.asyncio
async def test_operation_repairs_invalid_proposal_before_preview(monkeypatch):
    class ScriptedConversation:
        replies=0
        def __init__(self,*args,**kwargs):pass
        async def next(self,schemas,**kwargs):
            type(self).replies+=1
            param='route' if type(self).replies==1 else 'default_gateway'
            return [ToolCall(str(type(self).replies),'submit_action',{'change':{'target':'HOST-001','param':param,'value':'10.0.1.1','reason':'Observed healthy alternate'}})]
        def result(self,*args):pass
        async def close(self):pass
    monkeypatch.setattr('ccs.agent_runtime.Conversation',ScriptedConversation)
    result=await select_change(load_ai(ROOT/'configs/ai.example.xml'),load_system(ROOT/'configs/system.xml'),{},work(),mode='live')
    assert result['param']=='default_gateway' and ScriptedConversation.replies==2
