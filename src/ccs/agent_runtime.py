"""Agent decisions, isolated from the network backend and evaluator."""
import json
import uuid
from pathlib import Path
from ccs.contracts import DiagnosisRequest,DiagnosisResult,ProposedChange,Report
from ccs.llm import Conversation,ProviderSchemaError,object_tool,model_tool
from ccs.observability import activity_for_episode

class AgentFailure(RuntimeError): pass

def prompt(system,role):
    return (system.prompts/f'{role}.txt').read_text(encoding='utf-8')

async def call_model(conv,schemas,retries):
    for attempt in range(retries+1):
        try:return await conv.next(schemas,attempt=attempt+1)
        except ProviderSchemaError:
            if attempt==retries:raise AgentFailure('FAILED_LLM_SCHEMA')
            conv.feedback('Return a complete call to one of the currently available tools.')

async def collect_context(ai,system,request,gateway,runbooks,memory,run_dir,*,mode,profile_override=None,trace_id=None,cause=None,rag_enabled=True):
    """The live Operation Agent selects search queries, repetitions and delegation content."""
    activity=activity_for_episode(Path(run_dir),'operation',mode,secrets=ai.keys.values())
    phase=activity.emit('operation','collect_context','started','Operation Agent started context collection',
        details={'incident':request,'context_step_budget':system.context_steps,'runbook_k':system.runbook_k,
            'memory_k':system.memory_k,'memory_enabled':system.memory_enabled,'rag_enabled':rag_enabled},trace_id=trace_id)
    context={"runbooks":[],"history":[]}
    if mode=='mock':
        try:
            query=' '.join([request['summary'],request['target']])
            if rag_enabled:
                search=activity.emit('runbook','search','started','Searching runbooks',details={'query':query,'limit':system.runbook_k},trace_id=trace_id)
                docs=runbooks.search(query,system.runbook_k)
                activity.emit('runbook','search','succeeded',f'Runbook search returned {len(docs)} result(s)',operation_id=search,
                    details={'query':query,'results':docs,'empty':not docs,'disabled':False},trace_id=trace_id)
            else:
                docs=[]
                activity.emit('runbook','search','skipped','Runbook retrieval is disabled',
                    details={'query':query,'results':[],'empty':True,'disabled':True},trace_id=trace_id)
            docs,retrieval_event=gateway.pass_through('G2',docs,'runbook','operation',trace_id=trace_id,causation_event_id=cause)
            if system.memory_enabled:
                memory_query=request['target']
                search=activity.emit('memory','search','started','Searching incident memory',details={'query':memory_query,'limit':system.memory_k},trace_id=trace_id)
                histories=memory.search(memory_query,system.memory_k)
                activity.emit('memory','search','succeeded',f'Memory search returned {len(histories)} result(s)',operation_id=search,
                    details={'query':memory_query,'results':histories,'empty':not histories,'disabled':False},trace_id=trace_id)
            else:
                histories=[]
                activity.emit('memory','search','skipped','Incident memory search is disabled',
                    details={'query':request['target'],'results':[],'empty':True,'disabled':True},trace_id=trace_id)
            histories,last_context_event=gateway.pass_through('G3r',histories,'memory','operation',trace_id=trace_id,causation_event_id=retrieval_event)
            selected={'incident':request,'context':{'runbooks':docs,'history':histories},'last_context_event':last_context_event}
            activity.emit('operation','collect_context','succeeded','Operation Agent prepared diagnosis context',operation_id=phase,
                details={'incident':request,'context':selected['context']},trace_id=trace_id)
            return selected
        except Exception as exc:
            activity.emit('operation','collect_context','failed','Operation Agent context collection failed',operation_id=phase,
                details={'error_type':type(exc).__name__},trace_id=trace_id)
            raise
    schemas=[]
    if rag_enabled:
        schemas.append(object_tool('search_runbook','Search English operational runbooks by words.',{'query':{'type':'string'}},['query']))
    else:
        activity.emit('runbook','search','skipped','Runbook retrieval is disabled',
            details={'query':None,'results':[],'empty':True,'disabled':True},trace_id=trace_id)
        _,cause=gateway.pass_through('G2',[],'runbook','operation',trace_id=trace_id,causation_event_id=cause)
    if system.memory_enabled:
        schemas.append(object_tool('read_memory','Search approved incident history; verify current facts independently.',{'query':{'type':'string'}},['query']))
    else:
        activity.emit('memory','search','skipped','Incident memory search is disabled',
            details={'query':None,'results':[],'empty':True,'disabled':True},trace_id=trace_id)
        _,cause=gateway.pass_through('G3r',[],'memory','operation',trace_id=trace_id,causation_event_id=cause)
    schemas.append(object_tool('delegate_diagnosis','Send the incident and chosen runbook/history context to the Diagnosis Agent.',{'incident':{'type':'object'},'context':{'type':'object'}},['incident','context']))
    conv=Conversation(ai,'operation',prompt(system,'operation'),{'phase':'context','incident':request,'context_step_budget':system.context_steps},run_dir,profile_override)
    try:
        for step in range(system.context_steps):
            offered=schemas if step<system.context_steps-1 else [schemas[-1]]
            calls=await call_model(conv,offered,ai.schema_retries)
            for call in calls:
                if call.name=='delegate_diagnosis':
                    incident=call.arguments.get('incident'); selected=call.arguments.get('context')
                    if not isinstance(incident,dict) or not isinstance(selected,dict):
                        conv.result(call,{'error':'incident and context must be objects'}); continue
                    selected=dict(selected)
                    if not rag_enabled:selected['runbooks']=[]
                    if not system.memory_enabled:selected['history']=[]
                    prepared={'incident':incident,'context':selected,'last_context_event':cause}
                    activity.emit('operation','collect_context','succeeded','Operation Agent selected context for diagnosis',operation_id=phase,
                        details={'incident':incident,'context':selected},trace_id=trace_id)
                    return prepared
                if call.name=='search_runbook' and rag_enabled and step<system.context_steps-1:
                    query=str(call.arguments.get('query',''))
                    search=activity.emit('runbook','search','started','Searching runbooks',details={'query':query,'limit':system.runbook_k},trace_id=trace_id)
                    result=runbooks.search(query,system.runbook_k)
                    activity.emit('runbook','search','succeeded',f'Runbook search returned {len(result)} result(s)',operation_id=search,
                        details={'query':query,'results':result,'empty':not result},trace_id=trace_id)
                    result,cause=gateway.pass_through('G2',result,'runbook','operation',trace_id=trace_id,causation_event_id=cause); context['runbooks'].extend(result)
                elif call.name=='read_memory' and system.memory_enabled and step<system.context_steps-1:
                    query=str(call.arguments.get('query',''))
                    search=activity.emit('memory','search','started','Searching incident memory',details={'query':query,'limit':system.memory_k},trace_id=trace_id)
                    result=memory.search(query,system.memory_k)
                    activity.emit('memory','search','succeeded',f'Memory search returned {len(result)} result(s)',operation_id=search,
                        details={'query':query,'results':result,'empty':not result,'disabled':False},trace_id=trace_id)
                    result,cause=gateway.pass_through('G3r',result,'memory','operation',trace_id=trace_id,causation_event_id=cause); context['history'].extend(result)
                else:result={'error':'Tool unavailable in context phase'}
                conv.result(call,result)
        raise AgentFailure('FAILED_CONTEXT_BUDGET')
    except Exception as exc:
        activity.emit('operation','collect_context','failed','Operation Agent context collection failed',operation_id=phase,
            details={'error_type':type(exc).__name__},trace_id=trace_id)
        raise
    finally:await conv.close()

_CAUSE_BY_PARAM={
    'active_path':'intermediate_switch_failure','admin_state':'interface_down',
    'default_gateway':'incorrect_default_gateway','loss_pct':'packet_loss_misconfiguration',
    'bandwidth_mbps':'bandwidth_limit_misconfiguration','delay_ms':'excessive_delay_misconfiguration'}

async def diagnose(ai,system,payload,tools,run_dir,*,mode,profile_override=None):
    request=DiagnosisRequest.model_validate(payload)
    budget=min(int(request.constraints.get('tool_budget',system.diagnosis_tool_budget)),system.diagnosis_tool_budget)
    activity=activity_for_episode(Path(run_dir),'diagnosis',mode,secrets=ai.keys.values())
    phase=activity.emit('diagnosis','investigate','started','Diagnosis Agent started investigation',
        details={'incident':request.incident,'context':request.context,'tool_budget':budget},trace_id=request.trace_id)
    if budget<1:
        activity.emit('diagnosis','investigate','failed','Diagnosis tool budget is exhausted',operation_id=phase,
            details={'tool_budget':budget},trace_id=request.trace_id)
        raise AgentFailure('FAILED_DIAGNOSIS_BUDGET')
    def complete(value):
        activity.emit('diagnosis','investigate','succeeded','Diagnosis Agent submitted an evidence-based conclusion',operation_id=phase,
            details={'root_cause':value.get('root_cause'),'confidence':value.get('confidence'),
                'evidence':value.get('evidence',[]),'proposed_change':value.get('proposed_change'),'notes':value.get('notes','')},trace_id=request.trace_id)
        return value
    read_count=0
    async def read(name,arguments):
        nonlocal read_count
        if read_count>=budget:raise AgentFailure('FAILED_DIAGNOSIS_BUDGET')
        read_count+=1
        return await tools.call(name,arguments)
    try:schemas=await tools.list_tools()
    except Exception as exc:
        activity.emit('diagnosis','investigate','failed','Diagnosis Agent could not discover MCP tools',operation_id=phase,
            details={'error_type':type(exc).__name__},trace_id=request.trace_id)
        raise
    final=model_tool('submit_diagnosis','Submit evidence-supported root cause and an unexecuted remedy, or null change.',DiagnosisResult)
    if mode=='mock':
        try:
            target=request.incident.get('target') or request.incident.get('targets',['HOST-001'])[0]
            alarms=await read('list_alarms',{})
            primary=next((a for a in alarms['alarms'] if a.get('status')=='active' and a.get('severity') in {'ERROR','CRITICAL'}),None)
            config=await read('get_config',{'target':target})
            kpi=await read('get_kpi',{'target':target}) if budget>=3 else {}
            abnormal=[x for x in config.get('items',[]) if not x.get('is_at_reference',True)]
            if not abnormal:
                if target.startswith('HOST-') and budget>=4:
                    topology=await read('get_topology',{'target':target})
                    active=next((x['current_value'] for x in config.get('items',[]) if x.get('param')=='active_path'),None)
                    nodes={x.get('node_id'):x for x in topology.get('nodes',[])}
                    active_switch='SWITCH-PRIMARY' if active=='primary' else 'SWITCH-BACKUP'
                    backup='backup' if active=='primary' else 'primary'
                    backup_switch='SWITCH-BACKUP' if backup=='backup' else 'SWITCH-PRIMARY'
                    active_down=nodes.get(active_switch,{}).get('status')=='down' or any(x.get('path')==active and x.get('status')=='down' for x in topology.get('links',[]))
                    backup_up=nodes.get(backup_switch,{}).get('status')=='up' and all(x.get('status')=='up' for x in topology.get('links',[]) if x.get('path')==backup)
                    if active_down and backup_up:
                        return complete(DiagnosisResult(root_cause='intermediate_switch_failure',evidence=[{'config':config},{'topology':topology},{'kpi':kpi}],proposed_change=ProposedChange(target=target,param='active_path',value=backup,reason='Reroute around the observed failed intermediate switch over the healthy alternate path'),confidence=1).model_dump(mode='json'))
                return complete(DiagnosisResult(root_cause='no_fault_detected',evidence=[{'config':config},{'kpi':kpi}],confidence=1).model_dump(mode='json'))
            item=abnormal[0]
            cause=item.get('root_cause') or _CAUSE_BY_PARAM.get(item['param'],'unknown')
            change=ProposedChange(target=item.get('target',target),param=item['param'],value=item['reference_value'],reason='Restore observed deviation from operational reference')
            return complete(DiagnosisResult(root_cause=cause,evidence=[{'config':config},{'kpi':kpi}],proposed_change=change,confidence=1).model_dump(mode='json'))
        except Exception as exc:
            activity.emit('diagnosis','investigate','failed','Diagnosis Agent investigation failed',operation_id=phase,
                details={'error_type':type(exc).__name__,'tools_used':read_count,'tool_budget':budget},trace_id=request.trace_id)
            raise
    conv=Conversation(ai,'diagnosis',prompt(system,'diagnosis'),request.model_dump(mode='json'),run_dir,profile_override)
    used=0
    try:
        for step in range(system.max_agent_steps):
            offered=schemas+[final] if used<budget else [final]
            calls=await call_model(conv,offered,ai.schema_retries)
            for call in calls:
                if call.name=='submit_diagnosis':
                    try:return complete(DiagnosisResult.model_validate(call.arguments).model_dump(mode='json'))
                    except Exception:
                        conv.result(call,{'error':'Invalid DiagnosisResult schema'}); continue
                if call.name not in {s['name'] for s in schemas} or used>=budget:
                    conv.result(call,{'error':'Read-only tool budget exhausted or tool unavailable'}); continue
                used+=1
                try:result=await read(call.name,call.arguments)
                except Exception as exc:result={'error':type(exc).__name__}
                conv.result(call,result)
        raise AgentFailure('FAILED_DIAGNOSIS_BUDGET')
    except Exception as exc:
        activity.emit('diagnosis','investigate','failed','Diagnosis Agent investigation failed',operation_id=phase,
            details={'error_type':type(exc).__name__,'tools_used':used,'tool_budget':budget},trace_id=request.trace_id)
        raise
    finally:await conv.close()

async def select_change(ai,system,diagnosis,run_dir,*,mode,profile_override=None):
    activity=activity_for_episode(Path(run_dir),'operation',mode,secrets=ai.keys.values())
    phase=activity.emit('operation','select_change','started','Operation Agent started change selection',details={'diagnosis':diagnosis})
    if mode=='mock':
        change=diagnosis.get('proposed_change')
        activity.emit('operation','select_change','succeeded','Operation Agent selected the proposed change' if change else 'Operation Agent selected no change',
            operation_id=phase,details={'change':change,'root_cause':diagnosis.get('root_cause'),'evidence':diagnosis.get('evidence',[])})
        return change
    schema=object_tool('submit_action','Propose the exact change for preview, or null if no action is justified.',{
        'change':{'anyOf':[ProposedChange.model_json_schema(),{'type':'null'}]}},['change'])
    conv=Conversation(ai,'operation',prompt(system,'operation'),{'phase':'action_selection','diagnosis':diagnosis},run_dir,profile_override)
    try:
        for _ in range(ai.schema_retries+1):
            for call in await call_model(conv,[schema],ai.schema_retries):
                try:
                    if call.name!='submit_action' or 'change' not in call.arguments:raise ValueError()
                    change=call.arguments['change']
                    selected=None if change is None else ProposedChange.model_validate(change).model_dump(mode='json')
                    activity.emit('operation','select_change','succeeded','Operation Agent selected a change' if selected else 'Operation Agent selected no change',
                        operation_id=phase,details={'change':selected,'root_cause':diagnosis.get('root_cause'),'evidence':diagnosis.get('evidence',[])})
                    return selected
                except Exception:conv.result(call,{'error':'Invalid change; use target,param,value,reason or null'})
        raise AgentFailure('FAILED_LLM_SCHEMA')
    except Exception as exc:
        activity.emit('operation','select_change','failed','Operation Agent change selection failed',operation_id=phase,
            details={'error_type':type(exc).__name__})
        raise
    finally:await conv.close()

async def compose_report(ai,system,facts,run_dir,*,mode,profile_override=None):
    activity=activity_for_episode(Path(run_dir),'operation',mode,secrets=ai.keys.values())
    phase=activity.emit('operation','compose_report','started','Operation Agent started the verified report',details={'facts':facts})
    if mode=='mock':
        report=Report(summary=f"Incident finished with outcome {facts['outcome']}.",root_cause=facts.get('diagnosis',{}).get('root_cause','unknown'),action=str(facts.get('change') or 'No change'),outcome=facts['outcome']).model_dump(mode='json')
        activity.emit('operation','compose_report','succeeded','Operation Agent completed the incident report',operation_id=phase,details={'report':report})
        return report
    conv=Conversation(ai,'operation',prompt(system,'operation'),{'phase':'report','verified_execution_facts':facts},run_dir,profile_override)
    try:
        report_schema=Report.model_json_schema()
        report_schema['properties']['outcome']={
            'type':'string',
            'enum':[facts['outcome']],
            'description':'Copy the verified execution outcome exactly, with no explanation or additional wording.'}
        report_tool={'name':'submit_report','description':'Write a report grounded in verified execution facts. Copy outcome exactly; use narrative fields for explanations.', 'parameters':report_schema}
        for _ in range(ai.schema_retries+1):
            for call in await call_model(conv,[report_tool],ai.schema_retries):
                try:
                    if call.name!='submit_report':
                        raise ValueError('tool')
                    report=Report.model_validate(call.arguments)
                    if report.outcome!=facts['outcome']:
                        raise ValueError('outcome')
                    rendered=report.model_dump(mode='json')
                    activity.emit('operation','compose_report','succeeded','Operation Agent completed the incident report',operation_id=phase,details={'report':rendered})
                    return rendered
                except ValueError as exc:
                    if str(exc)=='outcome':
                        message=f'Invalid outcome: copy the verified execution outcome exactly as "{facts["outcome"]}"; put explanations in summary, root_cause, action, or evidence.'
                    elif str(exc)=='tool':
                        message='Invalid tool call: call submit_report with the report fields.'
                    else:
                        message='Invalid report schema: provide summary, root_cause, action, outcome, and evidence using their specified types.'
                    conv.result(call,{'error':message})
                except Exception:
                    conv.result(call,{'error':'Invalid report schema: provide summary, root_cause, action, outcome, and evidence using their specified types.'})
        raise AgentFailure('FAILED_LLM_SCHEMA')
    except Exception as exc:
        activity.emit('operation','compose_report','failed','Operation Agent report composition failed',operation_id=phase,details={'error_type':type(exc).__name__})
        raise
    finally:await conv.close()

async def propose_memory(ai,system,report,run_dir,*,mode,profile_override=None):
    activity=activity_for_episode(Path(run_dir),'operation',mode,secrets=ai.keys.values())
    phase=activity.emit('memory','draft','started','Operation Agent started a memory draft',details={'verified_report':report})
    if mode=='mock':
        draft={'purpose':'P-recur','payload':report}
        activity.emit('memory','draft','succeeded','Operation Agent prepared a memory write',operation_id=phase,details={'draft':draft})
        return draft
    schema=object_tool('propose_memory','Draft the approved verified incident summary and declare its retention purpose. D0 records it unchanged.',{'purpose':{'type':'string','enum':['P-recur','P-ctx','P-audit','P-know']},'payload':{'type':'object'}},['purpose','payload'])
    conv=Conversation(ai,'operation',prompt(system,'operation'),{'phase':'approved_memory_draft','report':report},run_dir,profile_override)
    try:
        for _ in range(ai.schema_retries+1):
            for call in await call_model(conv,[schema],ai.schema_retries):
                if call.name=='propose_memory' and call.arguments.get('purpose') in {'P-recur','P-ctx','P-audit','P-know'} and isinstance(call.arguments.get('payload'),dict):
                    activity.emit('memory','draft','succeeded','Operation Agent prepared a memory write',operation_id=phase,details={'draft':call.arguments})
                    return call.arguments
                conv.result(call,{'error':'Invalid memory draft'})
        raise AgentFailure('FAILED_LLM_SCHEMA')
    except Exception as exc:
        activity.emit('memory','draft','failed','Operation Agent memory draft failed',operation_id=phase,details={'error_type':type(exc).__name__})
        raise
    finally:await conv.close()
