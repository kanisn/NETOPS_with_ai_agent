"""Private entrypoint for the two child services; no evaluator imports in Diagnosis."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
import uvicorn
from ccs.core.bus import EventBus
from ccs.core.gateway import Gateway
from ccs.observability import activity_for_episode

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('kind',choices=['tools','diagnosis']);parser.add_argument('--context',type=Path,required=True)
    args=parser.parse_args(); context=json.loads(args.context.read_text(encoding='utf-8'))
    run_dir=Path(context['run_dir']);episode=context['episode_id']
    bus=EventBus(run_dir,f'{args.kind}-{episode}',context['run_id'],episode)
    gateway=Gateway(bus)
    episode_dir=run_dir/'episodes'/episode
    if args.kind=='tools':
        from ccs.netops.sqlite_backend import SQLiteBackend
        from ccs.netops.tools import tool_schemas
        from ccs.protocols.mcp import build_mcp_app
        backend=SQLiteBackend(Path(context['db_path']))
        activity=activity_for_episode(episode_dir,'mcp-server',context.get('mode'))
        async def handler(name,arguments,metadata):
            started=time.monotonic()
            operation=activity.emit('mcp','execute','started',f'MCP server started {name}',
                details={'tool':name,'arguments':arguments,'caller_role':metadata.get('role','unknown')},
                trace_id=metadata.get('trace_id',episode))
            try:
                result=backend.call(name,arguments);status='succeeded'
            except Exception as exc:
                result={'error':getattr(exc,'code',type(exc).__name__)};status='failed'
            result,event=gateway.pass_through('G4.ret',result,f'tool:{name}',metadata.get('role','unknown'),
                causation_event_id=metadata.get('causation_event_id'),transport='mcp',status=status,
                trace_id=metadata.get('trace_id',episode),attempt=metadata.get('attempt',1),
                authenticated_principal=metadata.get('role','unknown'),
                server_execution={'tool':name,'protocol_call_id':str(metadata.get('protocol_call_id','')),
                    'args_hash':hashlib.sha256(json.dumps(arguments,sort_keys=True).encode()).hexdigest()})
            activity.emit('mcp','execute',status,f'MCP server {status} {name}',operation_id=operation,
                details={'tool':name,'arguments':arguments,'result':result,'caller_role':metadata.get('role','unknown'),
                    'duration_seconds':time.monotonic()-started},trace_id=metadata.get('trace_id',episode))
            return {**result,'_ccs_event_id':event}
        app=build_mcp_app({r:tool_schemas(r) for r in ['operation','diagnosis']},
            {r:os.environ['CCS_'+r.upper()+'_TOKEN'] for r in ['operation','diagnosis']},handler)
    else:
        from ccs.config import load_ai,load_system
        from ccs.protocols.a2a import build_a2a_app
        from ccs.tool_access import InstrumentedTools
        from ccs.agent_runtime import diagnose
        ai=load_ai(Path(context['ai_path']));system=load_system(Path(context['system_path']))
        activity=activity_for_episode(episode_dir,'a2a-diagnosis',context.get('mode'))
        async def handler(payload,metadata):
            started=time.monotonic()
            operation=activity.emit('a2a','request_received','started','Diagnosis Agent received an A2A handoff',
                details={'request':payload,'metadata':metadata},trace_id=payload.get('trace_id'))
            tools=InstrumentedTools(context['mcp_url'],os.environ['CCS_DIAGNOSIS_TOKEN'],gateway,'diagnosis',payload['trace_id'],
                timeout=system.request_timeout,read_retries=system.read_retries,cause=metadata.get('causation_event_id'),mode=context.get('mode'))
            try:
                result=await diagnose(ai,system,payload,tools,Path(context['log_dir']),mode=context['mode'],profile_override=context.get('profile_override'))
            except Exception as exc:
                activity.emit('a2a','response','failed','Diagnosis Agent failed the A2A request',operation_id=operation,
                    details={'error_type':type(exc).__name__,'duration_seconds':time.monotonic()-started},trace_id=payload.get('trace_id'))
                raise
            activity.emit('a2a','response','succeeded','Diagnosis Agent returned an evidence-based A2A response',operation_id=operation,
                details={'response':result,'duration_seconds':time.monotonic()-started},trace_id=payload.get('trace_id'))
            return result
        app=build_a2a_app(context['a2a_url'],os.environ['CCS_A2A_TOKEN'],handler,timeout_seconds=context['request_timeout'])
    uvicorn.run(app,host=context['host'],port=context['port'],log_level='warning',access_log=False)

if __name__=='__main__':main()
