"""Client-side tool gateway; all Agent network access uses MCP."""
import time
from ccs.observability import activity_for_episode
from ccs.protocols.mcp import MCPClient

class ToolFailure(RuntimeError): pass

class InstrumentedTools:
    def __init__(self,url,token,gateway,role,trace_id,*,timeout=120,read_retries=2,cause=None,mode=None):
        self.client=MCPClient(url,token,timeout_seconds=timeout)
        self.gateway=gateway; self.role=role; self.trace_id=trace_id
        self.read_retries=read_retries; self.cause=cause; self.calls=0
        episode_dir=gateway.bus.run_dir/'episodes'/gateway.bus.episode_id
        self.activity=activity_for_episode(episode_dir,f'mcp-{role}',mode)

    async def list_tools(self):
        started=time.monotonic()
        operation=self.activity.emit('mcp','list_tools','started',f'{self.role} requested available MCP tools',
            details={'role':self.role},trace_id=self.trace_id)
        try:
            result=await self.client.list_tools()
        except Exception as exc:
            self.activity.emit('mcp','list_tools','failed',f'{self.role} MCP tool discovery failed',operation_id=operation,
                details={'role':self.role,'error_type':type(exc).__name__,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
            raise
        self.activity.emit('mcp','list_tools','succeeded',f'{self.role} discovered {len(result)} MCP tools',operation_id=operation,
            details={'role':self.role,'tools':result,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
        return result

    async def call(self,name,arguments):
        retryable=name in {'list_alarms','get_kpi','get_logs','get_config','get_topology','lookup_flows','get_change_status','verify_service'}
        for attempt in range(1,(self.read_retries+1 if retryable else 1)+1):
            self.calls+=1
            started=time.monotonic()
            operation=self.activity.emit('mcp','call','started',f'{self.role} called {name}',
                details={'role':self.role,'tool':name,'arguments':arguments,'attempt':attempt,'retryable':retryable},trace_id=self.trace_id)
            _,event=self.gateway.pass_through('G4.call',{'tool':name,'arguments':arguments},self.role,f'tool:{name}',
                causation_event_id=self.cause,transport='mcp',trace_id=self.trace_id,attempt=attempt,principal_role='tools')
            try:
                result=await self.client.call(name,arguments,metadata={'trace_id':self.trace_id,'causation_event_id':event,'episode_id':self.gateway.bus.episode_id,'attempt':attempt})
            except Exception as exc:
                _,last=self.gateway.pass_through('G4.ret',{'error_type':type(exc).__name__},f'tool:{name}',self.role,
                    causation_event_id=event,transport='mcp',status='failed',trace_id=self.trace_id,attempt=attempt)
                self.cause=last
                self.activity.emit('mcp','call','failed',f'{name} transport attempt failed',operation_id=operation,
                    details={'role':self.role,'tool':name,'arguments':arguments,'attempt':attempt,
                        'error_type':type(exc).__name__,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
                if retryable and attempt<=self.read_retries:continue
                raise ToolFailure(f'Tool transport failed: {name}') from None
            event_id=result.pop('_ccs_event_id',None)
            if not event_id:
                # Missing audit metadata is an infrastructure failure, never a successful tool result.
                _,event_id=self.gateway.pass_through('G4.ret',{'error':'missing server audit event'},f'tool:{name}',self.role,causation_event_id=event,transport='mcp',status='failed',trace_id=self.trace_id)
                self.activity.emit('mcp','call','failed',f'{name} result lacked required audit metadata',operation_id=operation,
                    details={'role':self.role,'tool':name,'arguments':arguments,'attempt':attempt,
                        'result':result,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
                raise ToolFailure('ABORTED_OBSERVABILITY')
            self.cause=event_id
            if 'error' in result:
                self.activity.emit('mcp','call','failed',f'{name} returned an error',operation_id=operation,
                    details={'role':self.role,'tool':name,'arguments':arguments,'attempt':attempt,
                        'result':result,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
                raise ToolFailure(str(result['error']))
            self.activity.emit('mcp','call','succeeded',f'{name} returned a result',operation_id=operation,
                details={'role':self.role,'tool':name,'arguments':arguments,'attempt':attempt,
                    'result':result,'duration_seconds':time.monotonic()-started},trace_id=self.trace_id)
            return result
