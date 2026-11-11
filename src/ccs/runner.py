"""Three-process, finite-episode runner for the D0 baseline."""
import asyncio
from datetime import datetime,timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import secrets
import shutil
import time
import uuid
from defusedxml import ElementTree as ET
from ccs.config import load_ai,load_system
from ccs.budget import BudgetLedger
from ccs.contracts import DiagnosisRequest,MemoryRecord
from ccs.core.bus import EventBus
from ccs.core.gateway import Gateway
from ccs.core.integrity import validate_and_merge
from ccs.knowledge.stores import RunbookStore,MemoryStore,runbook_files
from ccs.protocols.a2a import A2AClient
from ccs.processes import Services,choose_port
from ccs.tool_access import InstrumentedTools,ToolFailure
from ccs.agent_runtime import collect_context,select_change,compose_report,propose_memory
from ccs.observability import ActivityLog
from ccs.pacing import (install_run_pointer,read_control,summarize_timing,
    timeout_allowance_seconds,wait_after_event,write_control)

_REPLACE_RETRY_DELAYS=(0.01,0.025,0.05,0.1)
_TRANSIENT_REPLACE_WINERRORS={5,32,33}

def write_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    writing=path.with_name(path.name+'.writing')
    writing.write_text(json.dumps(value,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    try:
        for attempt in range(len(_REPLACE_RETRY_DELAYS)+1):
            try:
                os.replace(writing,path)
                return
            except PermissionError as exc:
                if getattr(exc,'winerror',None) not in _TRANSIENT_REPLACE_WINERRORS or attempt==len(_REPLACE_RETRY_DELAYS):raise
                time.sleep(_REPLACE_RETRY_DELAYS[attempt])
    except BaseException:
        try:writing.unlink(missing_ok=True)
        except OSError:pass
        raise

def utc():return datetime.now(timezone.utc).isoformat()

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def value_hash(value):
    encoded=json.dumps(value,ensure_ascii=False,allow_nan=False,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()

def snapshot_runbooks(source,destination):
    source=Path(source).resolve();destination=Path(destination);destination.mkdir(parents=True,exist_ok=False)
    if source.is_file():
        if source.suffix.lower()!='.md':raise ValueError('runbooks_override file must be Markdown')
        paths=[source]
    elif source.is_dir():paths=runbook_files(source)
    else:raise FileNotFoundError(f'runbook source does not exist: {source}')
    records=[]
    for path in paths:
        relative=Path(path.name) if source.is_file() else path.relative_to(source)
        target=destination/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
        records.append({'path':relative.as_posix(),'sha256':sha(target),'bytes':target.stat().st_size})
    return records

def normalize_initial_memory(records):
    if records is None:return []
    if not isinstance(records,list):raise TypeError('initial_memory must be a list')
    required={'id','title','content'};optional={'source_kind','source_run_id'};normalized=[];seen=set()
    for index,item in enumerate(records):
        if not isinstance(item,dict) or set(item)-required-optional or not required<=set(item):
            raise ValueError(f'initial_memory[{index}] has invalid fields')
        value={}
        for key in required|(set(item)&optional):
            if not isinstance(item[key],str) or not item[key].strip():raise ValueError(f'initial_memory[{index}].{key} must be non-empty text')
            value[key]=item[key].strip()
        if value['id'] in seen:raise ValueError(f'duplicate initial memory id: {value["id"]}')
        seen.add(value['id']);normalized.append(value)
    return normalized

def runtime_system_copy(source,destination,request_timeout):
    tree=ET.parse(source);network=tree.getroot().find('network')
    if network is None:raise ValueError('system XML has no network element')
    network.set('request_timeout_seconds',format(float(request_timeout),'.6f').rstrip('0').rstrip('.'))
    destination.parent.mkdir(parents=True,exist_ok=True);tree.write(destination,encoding='utf-8',xml_declaration=True)
    return destination

def source_hashes(root):
    files=[*Path(root).glob('src/**/*.py'),*Path(root).glob('src/**/*.html'),*Path(root).glob('src/**/*.js'),*Path(root).glob('src/**/*.css'),*Path(root).glob('prompts/*.txt'),*runbook_files(Path(root)/'knowledge/runbooks'),Path(root)/'requirements.lock']
    return {str(p.relative_to(root)).replace('\\','/'):sha(p) for p in sorted(files) if p.is_file()}

def _record_run_failure(run_dir,manifest,phase,exc,*,error_field,record_name):
    """Best-effort terminal record without leaking exception text or sealing partial output."""
    error={'phase':phase,'error_type':type(exc).__name__}
    for field in ('errno','winerror'):
        value=getattr(exc,field,None)
        if type(value) is int:error[field]=value
    manifest['status']='ABORTED'
    manifest['finished_at_utc']=utc()
    manifest[error_field]=error
    manifest.pop('artifact_hashes',None)
    try:write_json(Path(run_dir)/record_name,error)
    except BaseException:pass
    try:write_json(Path(run_dir)/'manifest.json',manifest)
    except BaseException:pass

    # A summary may already have been written before report or sealing failed.
    # Keep usage accounting where possible, but make it impossible to read as success.
    summary_path=Path(run_dir)/'summary.json'
    try:
        summary_exists=summary_path.exists()
    except BaseException:
        summary_exists=False
    if summary_exists:
        try:
            summary=json.loads(summary_path.read_text(encoding='utf-8'))
            summary['status']='ABORTED'
            summary['successful_episodes']=None
            summary['diagnoses_correct']=None
            summary['integrity_valid']=False
            summary[error_field]=error
            write_json(summary_path,summary)
        except BaseException:
            try:summary_path.unlink(missing_ok=True)
            except BaseException:pass
    for name in ('report.md','report.html'):
        try:(Path(run_dir)/name).unlink(missing_ok=True)
        except BaseException:pass

    # Retry the manifest after summary cleanup in case a transient write error cleared.
    try:write_json(Path(run_dir)/'manifest.json',manifest)
    except BaseException:pass

def _record_finalization_failure(run_dir,manifest,effective,phase,exc):
    _record_run_failure(run_dir,manifest,phase,exc,error_field='finalization_error',record_name='finalization-error.json')

def _seal_artifacts(run_dir):
    run_dir=Path(run_dir)
    return {str(path.relative_to(run_dir)).replace('\\','/'):sha(path)
        for path in sorted(run_dir.rglob('*')) if path.is_file() and path.name!='manifest.json'}

def _finalize_run(run_dir,manifest,effective,input_conditions,run_started_ns,registry,ai,mode,activity,run_operation):
    """Finalize a completed/failed episode set; failures are terminal and unsealed."""
    run_dir=Path(run_dir);phase='integrity'
    try:
        integrity=validate_and_merge(run_dir);write_json(run_dir/'integrity.json',integrity)
        if not integrity['valid']:manifest['status']='INVALID_ARTIFACT'
        from ccs.evaluation.ledger import build_ledger
        # Registry IDs are stable across repeated episodes; retain one copy of each value binding.
        phase='ledger'
        if integrity['valid']:write_json(run_dir/'ledger.json',build_ledger(run_dir,registry))
        phase='usage'
        usage=[]
        for path in run_dir.glob('episodes/*/llm_*.jsonl'):
            usage += [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line]
        run_finished_ns=time.time_ns();manifest['finished_at_utc']=utc()
        timing=summarize_timing(run_dir,started_unix_ns=run_started_ns,finished_unix_ns=run_finished_ns)
        timing['measurement_boundary']='through integrity, ledger and usage aggregation; excludes report rendering, terminal run event, monitor snapshot and sealing'
        manifest['timing']=timing;effective['timing']=timing
        phase='effective_config'
        write_json(run_dir/'effective-config.json',effective)
        manifest['config_hash']=sha(run_dir/'effective-config.json')
        phase='manifest'
        write_json(run_dir/'manifest.json',manifest)
        from decimal import Decimal
        summary={'run_id':manifest['run_id'],'status':manifest['status'],'episodes':len(manifest['episodes']),
            'completed_episodes':sum(e['status']=='CLOSED' for e in manifest['episodes']),
            'successful_episodes':sum(bool(e['utility']) for e in manifest['episodes']) if integrity['valid'] else None,
            'diagnoses_correct':sum(bool(e['diagnosis_correct']) for e in manifest['episodes']) if integrity['valid'] else None,
            'api_calls':len(usage),'input_tokens':sum(x.get('input_tokens',0) for x in usage),'output_tokens':sum(x.get('output_tokens',0) for x in usage),
            'estimated_cost_usd':str(sum((Decimal(x.get('cost_usd','0')) for x in usage),Decimal('0'))),
            'cumulative_budget':BudgetLedger(ai.ledger_path,ai.budget_usd).summary(),'integrity_valid':integrity['valid'],
            'mode':mode,'models':manifest['models'],'input_conditions':input_conditions,'timing':timing,
            'limitations':['Synthetic SQLite backend; no real-network validation.','No disclosure protection.','Model cost estimates use the configured price table.','Process/path separation is not an OS sandbox.']}
        phase='summary'
        write_json(run_dir/'summary.json',summary);write_json(run_dir/'manifest.json',manifest)
        from ccs.reporting import write_reports
        phase='reports'
        write_reports(run_dir,summary,manifest)
        phase='terminal_event'
        activity.emit('runner','run','succeeded' if summary['status']=='COMPLETED' else 'failed',f"Run finished: {summary['status']}",operation_id=run_operation,details={'summary':summary},delay_after=False)
        phase='monitor_snapshot'
        from ccs.monitor import write_snapshot
        write_snapshot(run_dir)
        phase='artifact_hashes'
        manifest['artifact_hashes']=_seal_artifacts(run_dir)
        phase='seal_manifest'
        write_json(run_dir/'manifest.json',manifest)
        return run_dir,summary
    except BaseException as exc:
        _record_finalization_failure(run_dir,manifest,effective,phase,exc)
        raise

TRANSITIONS={
    'RECEIVED':{'CONTEXT','FAILED'},'CONTEXT':{'DELEGATED','FAILED'},'DELEGATED':{'DIAGNOSED','FAILED'},
    'DIAGNOSED':{'PREVIEWED','REPORTED','FAILED'},'PREVIEWED':{'APPLIED','REPORTED','FAILED'},
    'APPLIED':{'VERIFIED','ROLLED_BACK','FAILED'},'VERIFIED':{'REPORTED','FAILED'},
    'ROLLED_BACK':{'REPORTED','FAILED'},'FAILED':{'REPORTED'},'REPORTED':{'MEMORY_WRITTEN','CLOSED'},
    'MEMORY_WRITTEN':{'CLOSED'},'CLOSED':set()}

class Workflow:
    def __init__(self,path,activity=None):self.path=path;self.state='RECEIVED';self.history=['RECEIVED'];self.activity=activity
    def transition(self,state,*,delay_after=True):
        if state not in TRANSITIONS[self.state]:raise RuntimeError(f'Illegal workflow transition {self.state} -> {state}')
        previous=self.state;self.state=state;self.history.append(state)
        with self.path.open('a',encoding='utf-8') as file:file.write(json.dumps({'from':previous,'to':state,'step':len(self.history),'utc':utc()})+'\n')
        if self.activity:
            self.activity.emit('runner','workflow','info',f'{previous} → {state}',details={'from':previous,'to':state,'step':len(self.history)},delay_after=delay_after)

def approve(policy,label):
    if policy=='auto':return True
    if policy=='deny':return False
    return input(f'{label} [y/N]: ').strip().lower()=='y'


def observed_approval(activity,policy,label):
    operation=activity.emit('operation','approval','waiting' if policy=='interactive' else 'started',label,details={'policy':policy})
    approved=approve(policy,label)
    activity.emit('operation','approval','succeeded' if approved else 'skipped',
        'Approval granted' if approved else 'Approval declined',operation_id=operation,details={'policy':policy,'approved':approved})
    return approved

async def execute_episode(system,ai,system_path,ai_path,run_dir,bus,runbooks,memory,scenario,episode_dir,*,mode,profile_override=None,rag_enabled=True):
    ep=episode_dir.name;trace=uuid.uuid4().hex;bus.episode_id=ep;gateway=Gateway(bus)
    activity=ActivityLog(run_dir,f'workflow-{ep}',ep,mode=mode,secrets=ai.keys.values())
    workflow=Workflow(episode_dir/'workflow.jsonl',activity)
    facts={'outcome':'FAILED','diagnosis':{},'change':None,'verify':{'passed':False},'memory_written':False,'infrastructure_error':None}
    started=time.monotonic()
    op_token=secrets.token_urlsafe(24);diag_token=secrets.token_urlsafe(24);a2a_token=secrets.token_urlsafe(24)
    ports=[choose_port(system.host,system.tool_port),choose_port(system.host,system.diagnosis_port)]
    while ports[0]==ports[1]:ports[1]=choose_port(system.host,0)
    mcp_url=f'http://{system.host}:{ports[0]}/mcp';a2a_url=f'http://{system.host}:{ports[1]}'
    common={'run_dir':str(run_dir),'run_id':run_dir.name,'episode_id':ep,'host':system.host}
    contexts={'tools':{**common,'port':ports[0],'db_path':str(episode_dir/'network.sqlite'),'mode':mode},
        'diagnosis':{**common,'port':ports[1],'system_path':str(system_path),'ai_path':str(ai_path),'mcp_url':mcp_url,'a2a_url':a2a_url,'log_dir':str(episode_dir),'mode':mode,'profile_override':profile_override,'request_timeout':system.request_timeout}}
    tokens={'CCS_OPERATION_TOKEN':op_token,'CCS_DIAGNOSIS_TOKEN':diag_token,'CCS_A2A_TOKEN':a2a_token}
    request={'summary':scenario['request'],'target':scenario['target'],'ticket_id':scenario['ticket_id']}
    episode_operation=activity.emit('runner','episode','started','Incident received; handing request to Operation Agent',details={'request':request,'fault':scenario['fault_id'] if 'fault_id' in scenario else scenario.get('scenario_id'),'mode':mode},trace_id=trace)
    activity.emit('operation','request_received','info','Operation Agent received the operator request',details={'request':request},trace_id=trace)
    request,input_event=gateway.pass_through('G1',request,'operator','operation',trace_id=trace)
    tools=None
    try:
        startup=activity.emit('runner','services','started','Starting Network Tools MCP and Diagnosis A2A services')
        async with Services(system,run_dir,episode_dir,contexts,tokens):
            activity.emit('runner','services','succeeded','MCP and A2A services are ready',operation_id=startup)
            tools=InstrumentedTools(mcp_url,op_token,gateway,'operation',trace,timeout=system.request_timeout,read_retries=system.read_retries,cause=input_event,mode=mode)
            workflow.transition('CONTEXT')
            context=await collect_context(ai,system,request,gateway,runbooks,memory,episode_dir,mode=mode,profile_override=profile_override,trace_id=trace,cause=input_event,rag_enabled=rag_enabled)
            message=DiagnosisRequest(task_id=ep,trace_id=trace,message_id=uuid.uuid4().hex,idempotency_key=f'{ep}-diagnosis',
                incident=context['incident'],context=context['context'],constraints={'tool_budget':system.diagnosis_tool_budget}).model_dump(mode='json')
            _,req_event=gateway.pass_through('G5.req',message,'operation','diagnosis',causation_event_id=context.get('last_context_event') or input_event,transport='a2a',trace_id=trace)
            workflow.transition('DELEGATED')
            delegation=activity.emit('a2a','delegate_diagnosis','started','Operation → Diagnosis: incident and selected context sent',details={'from':'operation','to':'diagnosis','request':message,'disclosure_event_id':req_event},trace_id=trace)
            delegation_started=time.monotonic()
            try:
                diagnosis=await A2AClient(a2a_url,a2a_token,timeout_seconds=system.request_timeout).diagnose(message,metadata={'causation_event_id':req_event})
            except Exception as exc:
                activity.emit('a2a','delegate_diagnosis','failed','Diagnosis handoff failed',operation_id=delegation,details={'error_type':type(exc).__name__,'duration_seconds':time.monotonic()-delegation_started},trace_id=trace)
                gateway.pass_through('G5.res',{'error':'FAILED_A2A'},'diagnosis','operation',causation_event_id=req_event,transport='a2a',trace_id=trace,status='failed')
                raise
            diagnosis,diag_event=gateway.pass_through('G5.res',diagnosis,'diagnosis','operation',causation_event_id=req_event,transport='a2a',trace_id=trace)
            activity.emit('a2a','delegate_diagnosis','succeeded','Diagnosis → Operation: conclusion and evidence received',operation_id=delegation,details={'from':'diagnosis','to':'operation','response':diagnosis,'duration_seconds':time.monotonic()-delegation_started,'disclosure_event_id':diag_event},trace_id=trace)
            activity.emit('operation','diagnosis_received','info','Operation Agent received diagnosis and proposed remedy',details={'diagnosis':diagnosis},trace_id=trace)
            tools.cause=diag_event;facts['diagnosis']=diagnosis;workflow.transition('DIAGNOSED')
            change=await select_change(ai,system,diagnosis,episode_dir,mode=mode,profile_override=profile_override)
            facts['change']=change
            activity.emit('operation','action_selected','info','Operation Agent selected a change' if change else 'Operation Agent selected no configuration change',details={'change':change,'basis':diagnosis},trace_id=trace)
            if change is not None:
                preview=await tools.call('preview_change',change);workflow.transition('PREVIEWED')
                if observed_approval(activity,system.approval,'Approve proposed network change'):
                    key=f'{ep}-apply'
                    try:applied=await tools.call('apply_change',{'change_token':preview['change_token'],'idempotency_key':key})
                    except ToolFailure:
                        status=await tools.call('get_change_status',{'idempotency_key':key})
                        if not status.get('found') or status.get('status')!='applied':raise ToolFailure('FAILED_CHANGE_UNKNOWN')
                        applied=status['response']
                    facts['applied']=applied;workflow.transition('APPLIED')
                    verified=await tools.call('verify_service',{'target':scenario['target']});facts['verify']=verified
                    if verified.get('passed'):
                        workflow.transition('VERIFIED');facts['outcome']='RECOVERED'
                    else:
                        facts['rollback']=await tools.call('rollback_change',{'change_id':applied['change_id'],'idempotency_key':f'{ep}-rollback'})
                        workflow.transition('ROLLED_BACK');facts['outcome']='ROLLED_BACK'
                else:facts['outcome']='DECLINED'
            else:
                facts['verify']=await tools.call('verify_service',{'target':scenario['target']})
                facts['outcome']='NO_CHANGE' if facts['verify'].get('passed') else 'ESCALATED'
            await tools.call('update_ticket',{'ticket_id':request['ticket_id'],'status':'resolved' if facts['outcome'] in {'RECOVERED','NO_CHANGE'} else 'escalated','note':facts['outcome'],'idempotency_key':f'{ep}-ticket'})
            report=await compose_report(ai,system,facts,episode_dir,mode=mode,profile_override=profile_override)
            report,report_event=gateway.pass_through('G6',report,'operation','operator',causation_event_id=tools.cause,trace_id=trace)
            facts['report']=report;workflow.transition('REPORTED')
            activity.emit('operation','report_delivered','succeeded','Operation → Human Operator: incident report delivered',details={'report':report,'verified_execution_outcome':facts['outcome'],'verify':facts['verify']},trace_id=trace)
            if facts['verify'].get('passed') and facts['outcome'] in {'RECOVERED','NO_CHANGE'} and system.memory_enabled and observed_approval(activity,system.approval,'Approve verified incident summary for memory'):
                draft=await propose_memory(ai,system,report,episode_dir,mode=mode,profile_override=profile_override)
                record=MemoryRecord(record_id=uuid.uuid4().hex,scope_id=ep,tenant_id='synthetic-tenant',purpose=draft['purpose'],written_at=int(ep.rsplit('-',1)[1])*1000+len(workflow.history),
                    source_event_ids=[report_event],verified_outcome='verified',payload={**draft['payload'],'target':scenario['target']}).model_dump(mode='json')
                record,_=gateway.pass_through('G3w',record,'operation','memory',causation_event_id=report_event,trace_id=trace,purpose=record['purpose'])
                writing=activity.emit('memory','write','started','Writing the approved, verified incident record',details={'record':record},trace_id=trace)
                try:memory.write(record,verified=True,approved=True)
                except Exception as exc:
                    activity.emit('memory','write','failed','Incident Memory write failed',operation_id=writing,details={'error_type':type(exc).__name__},trace_id=trace)
                    raise
                activity.emit('memory','write','succeeded','Incident Memory record saved',operation_id=writing,details={'record':record},trace_id=trace)
                facts['memory_written']=True;workflow.transition('MEMORY_WRITTEN')
            else:
                activity.emit('memory','write','skipped','Incident Memory write skipped',details={'memory_enabled':system.memory_enabled,'verify_passed':bool(facts['verify'].get('passed')),'outcome':facts['outcome'],'requires':'Verified successful outcome, memory enabled and operator approval'},trace_id=trace)
            workflow.transition('CLOSED')
    except Exception as exc:
        activity.emit('runner','episode_error','failed','Episode failed; inspect the recorded operation and error type',details={'error_type':type(exc).__name__,'workflow_state':workflow.state},trace_id=trace,delay_after=False)
        facts['outcome']='FAILED';facts['infrastructure_error']={'type':type(exc).__name__,'detail':str(exc)}
        if workflow.state not in {'REPORTED','MEMORY_WRITTEN','CLOSED'}:
            if workflow.state!='FAILED':workflow.transition('FAILED',delay_after=False)
            fallback={'summary':'Execution failed; inspect the restricted episode log.','root_cause':facts['diagnosis'].get('root_cause','unknown'),'action':'See actual change records','outcome':'FAILED','evidence':[]}
            gateway.pass_through('G6',fallback,'operation','operator',trace_id=trace,status='failed')
            facts['report']=fallback;workflow.transition('REPORTED',delay_after=False)
        if workflow.state in {'REPORTED','MEMORY_WRITTEN'}:workflow.transition('CLOSED',delay_after=False)
    facts['workflow']=workflow.history;facts['operation_tool_calls']=tools.calls if tools else 0;facts['latency_seconds']=time.monotonic()-started
    write_json(episode_dir/'result.json',facts)
    activity.emit('runner','episode','failed' if facts['infrastructure_error'] else 'succeeded',f"Episode finished: {facts['outcome']}",operation_id=episode_operation,details={'outcome':facts['outcome'],'verify':facts['verify'],'memory_written':facts['memory_written'],'duration_seconds':facts['latency_seconds']},trace_id=trace)
    return facts

async def run(system_path: Path,ai_path: Path,*,mode='mock',faults=None,seeds=None,repeat=1,profile_override=None,memory_off=False,output_root=None,request_override=None,on_created=None,
    runbooks_override:Path|None=None,initial_memory:list[dict]|None=None,rag_enabled:bool=True,delay_control_path:Path|None=None,experiment_metadata:dict|None=None):
    system_path=Path(system_path).resolve();ai_path=Path(ai_path).resolve()
    system=load_system(system_path);ai=load_ai(ai_path)
    if type(rag_enabled) is not bool:raise TypeError('rag_enabled must be bool')
    if experiment_metadata is None:experiment_metadata={}
    if not isinstance(experiment_metadata,dict):raise TypeError('experiment_metadata must be a dictionary')
    experiment_metadata=json.loads(json.dumps(experiment_metadata,ensure_ascii=False,allow_nan=False))
    seed_memory=normalize_initial_memory(initial_memory)
    if profile_override:
        ai.profile('operation',profile_override);ai.profile('diagnosis',profile_override)
    if mode not in {'mock','live'}:raise ValueError('mode must be mock or live')
    if mode=='live':
        for role in ['operation','diagnosis']:
            if not ai.keys.get(ai.profile(role,profile_override).provider):raise ValueError('Missing API key for selected profile')
    if memory_off:system.memory_enabled=False
    selected_faults=faults or system.faults;selected_seeds=seeds or system.seeds
    if not set(selected_faults)<=set(system.faults) or repeat<1 or repeat>20:raise ValueError('Invalid fault selection or repeat count')
    root=Path(output_root) if output_root else system.output_root;root.mkdir(parents=True,exist_ok=True)
    run_id=f"D0_{mode}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid.uuid4().hex[:8]}"
    run_started_ns=time.time_ns();run_dir=root/run_id;run_dir.mkdir(exist_ok=False)

    supplied_delay_control=delay_control_path is not None
    control_path=Path(delay_control_path).resolve() if supplied_delay_control else run_dir/'pacing-control.json'
    if supplied_delay_control:control=read_control(control_path)
    else:control=write_control(control_path,0)
    install_run_pointer(run_dir,control_path)
    configured_request_timeout=system.request_timeout
    if supplied_delay_control:system.request_timeout += timeout_allowance_seconds(system)

    input_dir=run_dir/'inputs';input_dir.mkdir(parents=True,exist_ok=False)
    runtime_system_path=runtime_system_copy(system_path,input_dir/'system-runtime.xml',system.request_timeout)
    selected_runbook_source=Path(runbooks_override).resolve() if runbooks_override is not None else system.runbooks
    runbook_files=snapshot_runbooks(selected_runbook_source,input_dir/'runbooks')
    write_json(input_dir/'initial-memory.json',seed_memory)
    input_conditions={
        'rag_enabled':rag_enabled,
        'runbooks':{'count':len(runbook_files),'files':runbook_files},
        'initial_memory':{'count':len(seed_memory),'sha256':sha(input_dir/'initial-memory.json'),
            'records':[{'id':item['id'],'source_kind':item.get('source_kind','operator-note'),
                'source_run_id':item.get('source_run_id'),'sha256':value_hash(item)} for item in seed_memory]},
        'memory_enabled':system.memory_enabled,
        'pacing':{'mutable_control_supplied':supplied_delay_control,'initial_delay_seconds':control['seconds'],
            'configured_request_timeout_seconds':configured_request_timeout,'runtime_request_timeout_seconds':system.request_timeout},
        'experiment_metadata':experiment_metadata}
    input_conditions['condition_hash']=value_hash(input_conditions)
    manifest={'manifest_schema':'netops-run@1','run_id':run_id,'condition':'D0-disclosure-off','status':'RUNNING','mode':mode,'started_at_utc':utc(),'finished_at_utc':None,
        'network_backend':{'id':'sqlite-wired-v1','version':'2','clock_mode':'logical'},'scenario_catalog':'wired-v1','seeds':list(selected_seeds),'faults':list(selected_faults),'repeat':repeat,
        'models':{r:ai.profile(r,profile_override).model if mode=='live' else 'scripted-mock' for r in ['operation','diagnosis']},
        'runtime':{'python':platform.python_version(),'os':platform.platform()},'packages':{n:importlib.metadata.version(n) for n in ['mcp','a2a-sdk','openai','anthropic']},
        'source_hashes':source_hashes(system.project_root),'input_conditions':input_conditions,'episodes':[]}
    effective={'ai':ai.public(),'system':system.public(),'profile_override':profile_override,'input_conditions':input_conditions}
    write_json(run_dir/'manifest.json',manifest);write_json(run_dir/'effective-config.json',effective)
    manifest['config_hash']=sha(run_dir/'effective-config.json');write_json(run_dir/'manifest.json',manifest)
    activity=ActivityLog(run_dir,'run',mode=mode,secrets=ai.keys.values())
    run_operation=activity.emit('runner','run','started','NetOps run started',details={'mode':mode,'models':manifest['models'],'faults':list(selected_faults),'seeds':list(selected_seeds),'repeat':repeat,'input_conditions':input_conditions},delay_after=False)
    if on_created:on_created(run_dir)
    wait_after_event(run_dir,'run',run_operation,control_path)
    runbooks=RunbookStore(run_dir/'runbooks.sqlite',input_dir/'runbooks')
    memory=MemoryStore(run_dir/'memory.sqlite')
    for record in seed_memory:
        memory.import_reference(record,operator_seeded_experimental_context=True)
    activity.emit('memory','import_reference','succeeded' if seed_memory else 'skipped',
        f'Imported {len(seed_memory)} operator reference(s)' if seed_memory else 'No operator memory references selected',
        details={'record_ids':[item['id'] for item in seed_memory],'count':len(seed_memory),
            'provenance':'operator-imported reference; unverified'})
    bus=EventBus(run_dir,'runner',run_id,'episode-0000')
    registry=[];timing={}
    try:
        from ccs.bench.scenarios import create_world
        from ccs.evaluation.oracle import evaluate
        from ccs.netops.sqlite_backend import SQLiteBackend
        number=0
        for seed in selected_seeds:
            for fault in selected_faults:
                for repetition in range(repeat):
                    number+=1;ep=f'episode-{number:04d}';ep_dir=run_dir/'episodes'/ep;ep_dir.mkdir(parents=True)
                    scenario=create_world(ep_dir/'network.sqlite',seed=seed,fault_id=fault,target=system.target,difficulty=system.difficulty)
                    if request_override:scenario['request']=request_override
                    write_json(ep_dir/'scenario.restricted.json',scenario);registry.extend({**x,'origin_episode_id':ep} for x in scenario['registry'])
                    print(f'{ep}: {fault}, seed={seed}, mode={mode}',flush=True)
                    facts=await execute_episode(system,ai,runtime_system_path,ai_path,run_dir,bus,runbooks,memory,scenario,ep_dir,mode=mode,profile_override=profile_override,rag_enabled=rag_enabled)
                    backend=SQLiteBackend(ep_dir/'network.sqlite')
                    try:snapshot=backend.snapshot()
                    finally:backend.close()
                    write_json(ep_dir/'final-state.restricted.json',snapshot)
                    verdict=evaluate(ep_dir/'network.sqlite',scenario);write_json(ep_dir/'oracle.json',verdict)
                    ActivityLog(run_dir,f'oracle-{ep}',ep,mode=mode,secrets=ai.keys.values()).emit('runner','oracle','succeeded','Independent final network-state evaluation completed',details={'verdict':verdict,'agent_outcome':facts['outcome']})
                    entry={'episode_id':ep,'scenario_id':scenario['scenario_id'],'seed':seed,'repetition':repetition,'fault':fault,'status':'CLOSED','terminal':True,
                        'outcome':facts['outcome'],'utility':verdict['utility'],'infrastructure_error':facts['infrastructure_error'],'memory_written':facts['memory_written'],
                        'diagnosis_correct':facts['diagnosis'].get('root_cause')==scenario.get('ground_truth',{}).get('root_cause'),'latency_seconds':facts['latency_seconds']}
                    manifest['episodes'].append(entry);write_json(run_dir/'manifest.json',manifest)
        manifest['status']='FAILED' if any(e['infrastructure_error'] for e in manifest['episodes']) else 'COMPLETED'
    except BaseException as exc:
        try:activity.emit('runner','run','failed','Run aborted; partial activity and artifacts retained',operation_id=run_operation,details={'error_type':type(exc).__name__},delay_after=False)
        except BaseException:pass
        _record_run_failure(run_dir,manifest,'episode_execution',exc,error_field='run_error',record_name='run-error.json')
        raise
    finally:
        if manifest['status']=='ABORTED':
            for resource in (runbooks,memory):
                try:resource.close()
                except BaseException:pass
        else:
            try:
                runbooks.close();memory.close()
            except BaseException as exc:
                _record_run_failure(run_dir,manifest,'resource_cleanup',exc,error_field='run_error',record_name='run-error.json')
                raise
    return _finalize_run(run_dir,manifest,effective,input_conditions,run_started_ns,registry,ai,mode,activity,run_operation)
