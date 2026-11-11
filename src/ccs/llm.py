"""Native OpenAI Responses and Anthropic Messages tool-use adapters."""
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
import hashlib
import json
import re
import time
from typing import Any
from ccs.budget import BudgetLedger, token_cost
from ccs.config import AIConfig, ConfigurationError
from ccs.observability import ActivityLog, activity_for_episode

class ProviderError(RuntimeError):
    pass

class ProviderSchemaError(ProviderError):
    pass

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]

_DECISION_KEYS={"rationale","reason","evidence","conclusion","root_cause","confidence","notes"}

def _decision_fields(value):
    if isinstance(value,dict):
        selected={}
        for key,item in value.items():
            if key in _DECISION_KEYS:selected[key]=item
            else:
                nested=_decision_fields(item)
                if nested not in ({},[]):selected[key]=nested
        return selected
    if isinstance(value,list):
        nested=[_decision_fields(item) for item in value]
        return [item for item in nested if item not in ({},[])]
    return {}

class Conversation:
    def __init__(self,config: AIConfig,role: str,system: str,user: dict | str,log_dir: Path,profile_override: str | None=None,*,activity: ActivityLog | None=None):
        self.config=config; self.role=role; self.profile=config.profile(role,profile_override)
        key=config.keys.get(self.profile.provider,"")
        if not key: raise ConfigurationError("The selected provider has no API key configured")
        self.system=system; self.initial_request=user
        self.history=[{"role":"user","content":json.dumps(user,ensure_ascii=False) if isinstance(user,dict) else user}]
        self.log_path=Path(log_dir)/f"llm_{role}.jsonl"
        self.log_path.parent.mkdir(parents=True,exist_ok=True)
        self.activity=activity or activity_for_episode(Path(log_dir),f'model-{role}',mode='live',secrets=config.keys.values())
        self.ledger=BudgetLedger(config.ledger_path,config.budget_usd)
        if self.profile.provider=="openai":
            from openai import AsyncOpenAI
            self.client=AsyncOpenAI(api_key=key,base_url='https://api.openai.com/v1',timeout=config.timeout,max_retries=0)
        else:
            from anthropic import AsyncAnthropic
            self.client=AsyncAnthropic(api_key=key,base_url='https://api.anthropic.com',timeout=config.timeout,max_retries=0)

    async def close(self):
        await self.client.close()

    def feedback(self,text: str):
        self.history.append({"role":"user","content":text})
        self.activity.emit('model','schema_feedback','info',f'{self.role} model received schema feedback',details={'feedback':text})

    def result(self,call: ToolCall,result: dict | list):
        text=json.dumps(result,ensure_ascii=False,default=str)
        if self.profile.provider=="openai":
            self.history.append({"type":"function_call_output","call_id":call.id,"output":text})
        else:
            block={"type":"tool_result","tool_use_id":call.id,"content":text}
            if self.history[-1].get("role")=="user" and isinstance(self.history[-1].get("content"),list):
                self.history[-1]["content"].append(block)
            else:
                self.history.append({"role":"user","content":[block]})
        self.activity.emit('model','tool_result','info',f'{self.role} model received result for {call.name}',
            details={'tool':call.name,'result':result})

    def _log(self,record):
        with self.log_path.open('a',encoding='utf-8') as f:
            f.write(json.dumps(record,ensure_ascii=False,default=str)+'\n')

    async def next(self,schemas: list[dict],*,attempt: int=1) -> list[ToolCall]:
        serialized=json.dumps({"system":self.system,"input":self.history,"tools":schemas},ensure_ascii=False,default=str)
        input_bytes=len(serialized.encode('utf-8'))
        if input_bytes>self.config.max_input_bytes:
            raise ProviderError("Configured input size limit reached before API request")
        # UTF-8 bytes bound ordinary tokenized text; added allowance covers tool framing.
        # Input is capped below long-context pricing thresholds and no hosted tools are used.
        input_bound=input_bytes+8192
        # Cache writes can cost more than ordinary input; reserve the higher rate.
        write_bound=input_bound if self.profile.cache_write_rate>self.profile.input_rate else 0
        reservation=self.ledger.reserve(token_cost(self.profile,input_bound,self.profile.max_output_tokens,cache_write_tokens=write_bound),self.profile.model,self.role)
        started=time.monotonic()
        operation_id=self.activity.emit('model','request','started',f'{self.role} model request started',details={
            'role':self.role,'provider':self.profile.provider,'model':self.profile.model,'attempt':attempt,
            'offered_tools':[schema.get('name','unknown') for schema in schemas],'request':self.initial_request})
        try:
            if self.profile.provider=="openai":
                response=await self.client.responses.create(model=self.profile.model,instructions=self.system,input=self.history,
                    tools=[{"type":"function","name":s['name'],"description":s['description'],"parameters":s['parameters'],"strict":False} for s in schemas],
                    tool_choice="required",parallel_tool_calls=False,store=False,include=["reasoning.encrypted_content"],
                    reasoning={"effort":self.profile.reasoning_effort},max_output_tokens=self.profile.max_output_tokens)
                raw=response.model_dump(mode='json')
                input_tokens=response.usage.input_tokens; output_tokens=response.usage.output_tokens
                cached=getattr(response.usage.input_tokens_details,'cached_tokens',0) or 0
                created=getattr(response.usage.input_tokens_details,'cache_write_tokens',0) or 0
                try:
                    calls=[ToolCall(o.call_id,o.name,json.loads(o.arguments)) for o in response.output if o.type=='function_call']
                except (ValueError,TypeError):
                    calls=[]
                finish=response.status
                if finish!='completed': calls=[]
                if calls and all(isinstance(c.arguments,dict) for c in calls):
                    # SDK attribute names (e.g. async_) and absent output-only fields
                    # are not valid wire input. Preserve reasoning using API aliases.
                    self.history.extend(item.model_dump(mode='json',by_alias=True,exclude_none=True) for item in response.output)
            else:
                options={"thinking":{"type":"disabled"}}
                if self.profile.reasoning_effort!='none':
                    options={"thinking":{"type":"adaptive"},"output_config":{"effort":self.profile.reasoning_effort}}
                response=await self.client.messages.create(model=self.profile.model,system=self.system,messages=self.history,
                    tools=[{"name":s['name'],"description":s['description'],"input_schema":s['parameters']} for s in schemas],
                    tool_choice={'type':'auto','disable_parallel_tool_use':True},max_tokens=self.profile.max_output_tokens,**options)
                raw=response.model_dump(mode='json'); usage=response.usage
                cached=getattr(usage,'cache_read_input_tokens',0) or 0
                created=getattr(usage,'cache_creation_input_tokens',0) or 0
                input_tokens=usage.input_tokens+cached+created; output_tokens=usage.output_tokens
                calls=[ToolCall(o.id,o.name,o.input) for o in response.content if o.type=='tool_use']
                finish=response.stop_reason
                if finish not in {'tool_use','end_turn'}: calls=[]
                if calls and all(isinstance(c.arguments,dict) for c in calls):
                    self.history.append({"role":"assistant","content":[item.model_dump(mode='json',by_alias=True,exclude_none=True) for item in response.content]})
            cost=token_cost(self.profile,input_tokens,output_tokens,cached,created)
            self.ledger.settle(reservation,cost)
            self._log({"reservation_id":reservation,"role":self.role,"provider":self.profile.provider,
                "requested_model":self.profile.model,"resolved_model":raw.get('model'),"request_id":getattr(response,'_request_id',None),
                "prompt_hash":hashlib.sha256(serialized.encode()).hexdigest(),"input_tokens":input_tokens,"cached_input_tokens":cached,
                "cache_write_input_tokens":created,
                "output_tokens":output_tokens,"cost_usd":str(cost),"latency_seconds":time.monotonic()-started,"finish_reason":finish,"attempt":attempt,"raw_response":raw})
        except Exception as exc:
            # Preserve actionable API fields only after scrubbing configured credentials.
            status=getattr(exc,'status_code',None)
            body=getattr(exc,'body',None)
            error=body.get('error',body) if isinstance(body,dict) else {}
            details={k:error.get(k) for k in ['type','code','param']} if isinstance(error,dict) else {}
            safe_details=json.dumps(details,default=str)
            for secret in self.config.keys.values():
                if secret:safe_details=safe_details.replace(secret,'[REDACTED]')
            safe_details=re.sub(r'sk-[A-Za-z0-9_-]{12,}','[REDACTED]',safe_details)
            try:
                self.ledger.settle(reservation,Decimal(0) if status in {400,401,403,404,422,429} else None,'failed')
            except ValueError:
                pass  # A successful API response was already accounted before a local logging error.
            self._log({"reservation_id":reservation,"role":self.role,"model":self.profile.model,"error_type":type(exc).__name__,"http_status":status,"provider_error":json.loads(safe_details),"attempt":attempt,"latency_seconds":time.monotonic()-started})
            self.activity.emit('model','request','failed',f'{self.role} model request failed',operation_id=operation_id,
                details={'role':self.role,'provider':self.profile.provider,'model':self.profile.model,
                    'attempt':attempt,'error_type':type(exc).__name__,'http_status':status,
                    'latency_seconds':time.monotonic()-started})
            raise ProviderError(f"Provider request failed ({type(exc).__name__}, HTTP {status}); see safe usage log") from None
        if not calls or any(not isinstance(c.arguments,dict) for c in calls):
            self.activity.emit('model','request','failed',f'{self.role} model returned no valid tool call',operation_id=operation_id,
                details={'role':self.role,'provider':self.profile.provider,'model':self.profile.model,
                    'attempt':attempt,'finish_reason':finish,'latency_seconds':time.monotonic()-started})
            raise ProviderSchemaError("Provider did not return a complete function call")
        self.activity.emit('model','request','succeeded',f'{self.role} model selected {calls[0].name}',operation_id=operation_id,
            details={'role':self.role,'provider':self.profile.provider,'model':self.profile.model,'attempt':attempt,
                'selected_tools':[{'name':call.name,'arguments':call.arguments,'decision':_decision_fields(call.arguments)} for call in calls],
                'input_tokens':input_tokens,'output_tokens':output_tokens,'cost_usd':str(cost),
                'latency_seconds':time.monotonic()-started,'finish_reason':finish})
        return calls

def object_tool(name: str,description: str,properties: dict,required: list[str] | None=None) -> dict:
    return {"name":name,"description":description,"parameters":{"type":"object","properties":properties,"required":required or [],"additionalProperties":False}}

def model_tool(name: str,description: str,model) -> dict:
    return {"name":name,"description":description,"parameters":model.model_json_schema()}
