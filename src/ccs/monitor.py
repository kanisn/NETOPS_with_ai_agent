"""Safe, local-only live monitor for curated CCS activity events.

The monitor deliberately reads only ``activity/*.jsonl`` plus an allow-list of
fields from ``manifest.json`` and ``summary.json``.  Restricted event blobs,
model transcripts, configuration files, and episode payloads are outside its
read boundary.
"""

from __future__ import annotations

import base64
from datetime import datetime, timezone
from functools import partial
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import hmac
import json
from pathlib import Path
import secrets
import threading
from typing import Any
from urllib.parse import parse_qs, quote, urlsplit

from ccs.event_presentation import presentation_for_event


_COMPONENTS = {"operation", "diagnosis", "runbook", "memory", "mcp", "a2a", "model", "runner"}
_STATUSES = {"started", "succeeded", "failed", "waiting", "skipped", "info"}
_TERMINAL_RUN_STATUSES = {"COMPLETED", "FAILED", "ABORTED", "INVALID_ARTIFACT"}
_BLOCKED_DETAIL_KEYS = {
    "authorization",
    "credential",
    "credentials",
    "api_key",
    "apikey",
    "password",
    "secret",
    "token",
    "raw_response",
    "thinking",
    "encrypted_content",
    "encrypted_reasoning",
    "reasoning_content",
}


def _json_safe(value: Any, *, depth: int = 0) -> Any:
    """Copy JSON-like detail data while suppressing credential/reasoning fields."""
    if depth > 12:
        return "[detail depth limit]"
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            text_key = str(key)
            lowered = text_key.casefold()
            if lowered in _BLOCKED_DETAIL_KEYS or any(
                marker in lowered
                for marker in (
                    "authorization",
                    "credential",
                    "password",
                    "api_key",
                    "secret",
                    "encrypted_content",
                    "encrypted_reasoning",
                    "raw_response",
                )
            ) or lowered.endswith("_token"):
                result[text_key] = "[redacted by monitor]"
            else:
                result[text_key] = _json_safe(item, depth=depth + 1)
        return result
    if isinstance(value, (list, tuple)):
        return [_json_safe(item, depth=depth + 1) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def _text(value: Any, default: str = "") -> str:
    return value if isinstance(value, str) else default


def _integer(value: Any, default: int = 0) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else default


def _normalize_event(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    event_id = _text(value.get("event_id"))
    if not event_id:
        return None
    component = _text(value.get("component")).casefold()
    status = _text(value.get("status")).casefold()
    normalized = {
        "event_id": event_id,
        "ts_utc": _text(value.get("ts_utc")),
        "run_id": _text(value.get("run_id")),
        "episode_id": _text(value.get("episode_id")),
        "writer_id": _text(value.get("writer_id")),
        "local_seq": _integer(value.get("local_seq")),
        "component": component if component in _COMPONENTS else "runner",
        "action": _text(value.get("action"), "activity"),
        "status": status if status in _STATUSES else "info",
        "summary": _text(value.get("summary")),
        "details": _json_safe(value.get("details", {})),
        "operation_id": _text(value.get("operation_id")),
        "mode": _text(value.get("mode")),
    }
    normalized["presentation"] = presentation_for_event(normalized)
    return normalized


def _timestamp_key(value: str) -> tuple[int, str]:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return (int(parsed.timestamp() * 1_000_000), value)
    except (ValueError, OverflowError):
        return (0, value)


def _event_sort_key(event: dict[str, Any]) -> tuple[Any, ...]:
    # This is a display order only.  The UI explicitly avoids calling it causal order.
    return (*_timestamp_key(event["ts_utc"]), event["writer_id"], event["local_seq"], event["event_id"])


def _activity_files(run_dir: Path) -> list[Path]:
    activity_dir = run_dir / "activity"
    if not activity_dir.is_dir():
        return []
    resolved_dir = activity_dir.resolve()
    files: list[Path] = []
    for path in activity_dir.iterdir():
        try:
            if path.suffix.casefold() == ".jsonl" and path.is_file() and path.resolve().is_relative_to(resolved_dir):
                files.append(path)
        except (OSError, RuntimeError):
            continue
    return sorted(files, key=lambda item: item.name.casefold())


def _read_incremental(run_dir: Path, offsets: dict[str, int] | None = None) -> tuple[list[dict[str, Any]], dict[str, int]]:
    offsets = offsets or {}
    events: list[dict[str, Any]] = []
    next_offsets: dict[str, int] = {}
    for path in _activity_files(run_dir):
        try:
            size = path.stat().st_size
            start = offsets.get(path.name, 0)
            if not isinstance(start, int) or start < 0 or start > size:
                start = 0
            with path.open("rb") as stream:
                stream.seek(start)
                chunk = stream.read()
        except OSError:
            continue
        newline = chunk.rfind(b"\n")
        if newline < 0:
            next_offsets[path.name] = start
            continue
        complete = chunk[: newline + 1]
        next_offsets[path.name] = start + newline + 1
        for raw_line in complete.splitlines():
            if not raw_line.strip():
                continue
            try:
                normalized = _normalize_event(json.loads(raw_line.decode("utf-8")))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if normalized is not None:
                events.append(normalized)
    events.sort(key=_event_sort_key)
    return events, next_offsets


def read_activity(run_dir: str | Path) -> list[dict[str, Any]]:
    """Return a normalized display-order snapshot of all complete activity lines.

    A trailing line without a newline is treated as an in-progress append.  Wall
    clock order is useful for display but does not prove total causality.
    """
    root = Path(run_dir).resolve()
    events, _ = _read_incremental(root)
    return events


def _safe_json_object(run_dir: Path, name: str) -> dict[str, Any]:
    path = run_dir / name
    try:
        if not path.is_file() or not path.resolve().is_relative_to(run_dir.resolve()):
            return {}
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RuntimeError):
        return {}
    return value if isinstance(value, dict) else {}


def _metadata(run_dir: Path) -> dict[str, Any]:
    manifest = _safe_json_object(run_dir, "manifest.json")
    summary = _safe_json_object(run_dir, "summary.json")
    episodes = []
    for episode in manifest.get("episodes", []):
        if not isinstance(episode, dict):
            continue
        episodes.append(
            {
                key: _json_safe(episode.get(key))
                for key in (
                    "episode_id",
                    "seed",
                    "repetition",
                    "fault",
                    "status",
                    "outcome",
                    "utility",
                    "memory_written",
                    "diagnosis_correct",
                    "latency_seconds",
                )
                if key in episode
            }
        )
    manifest_public = {
        key: _json_safe(manifest.get(key))
        for key in (
            "manifest_schema",
            "run_id",
            "condition",
            "status",
            "mode",
            "started_at_utc",
            "finished_at_utc",
            "network_backend",
            "seeds",
            "faults",
            "repeat",
            "models",
        )
        if key in manifest
    }
    manifest_public["episodes"] = episodes
    summary_public = {
        key: _json_safe(summary.get(key))
        for key in (
            "run_id",
            "status",
            "episodes",
            "completed_episodes",
            "successful_episodes",
            "diagnoses_correct",
            "api_calls",
            "input_tokens",
            "output_tokens",
            "estimated_cost_usd",
            "integrity_valid",
            "mode",
            "models",
            "limitations",
        )
        if key in summary
    }
    status = str(manifest_public.get("status", summary_public.get("status", "UNKNOWN"))).upper()
    activity_present = bool(_activity_files(run_dir))
    return {
        "manifest": manifest_public,
        "summary": summary_public,
        "activity_present": activity_present,
        "run_phase": "finished" if status in _TERMINAL_RUN_STATUSES else "live" if status == "RUNNING" else "unknown",
        "read_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def _encode_cursor(offsets: dict[str, int]) -> str:
    payload = json.dumps(offsets, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_cursor(value: str) -> dict[str, int]:
    if not value or len(value) > 16_384:
        return {}
    try:
        raw = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
        decoded = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return {}
    if not isinstance(decoded, dict):
        return {}
    return {str(key): item for key, item in decoded.items() if isinstance(item, int) and 0 <= item <= 2**63 - 1}


_STYLE = r"""
:root{color-scheme:dark;--bg:#07111f;--panel:#0c1a2b;--panel2:#102339;--line:#24425e;--text:#e8f2fa;--muted:#91a9bc;--cyan:#4ed8e8;--blue:#6ea8ff;--violet:#ad8cff;--green:#54d69b;--amber:#ffc96b;--red:#ff7f82;font-family:Inter,ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 15% -10%,#163e58 0,transparent 34%),var(--bg);color:var(--text);min-height:100vh}.shell{max-width:1680px;margin:auto;padding:22px}.top{display:flex;align-items:flex-start;justify-content:space-between;gap:16px;margin-bottom:18px}.eyebrow{color:var(--cyan);font-weight:800;letter-spacing:.14em;font-size:11px;text-transform:uppercase}.title{font-size:clamp(24px,3vw,42px);margin:5px 0 4px;letter-spacing:-.04em}.subtitle{color:var(--muted);margin:0}.live-chip{display:flex;align-items:center;gap:8px;border:1px solid var(--line);background:#0b1b2c;padding:9px 13px;border-radius:99px;font-weight:750;white-space:nowrap}.dot{width:9px;height:9px;border-radius:50%;background:var(--muted)}.live .dot{background:var(--green);box-shadow:0 0 0 5px #54d69b20}.disconnected .dot,.failed .dot{background:var(--red)}.finished .dot{background:var(--blue)}
.summary{display:grid;grid-template-columns:repeat(6,minmax(120px,1fr));gap:10px;margin-bottom:12px}.metric,.card,.panel{background:linear-gradient(145deg,#0f2236,#0a1727);border:1px solid var(--line);border-radius:14px;box-shadow:0 12px 35px #0003}.metric{padding:13px 15px}.metric span{display:block;color:var(--muted);font-size:11px;text-transform:uppercase;letter-spacing:.08em}.metric strong{display:block;font-size:18px;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.flow{display:grid;grid-template-columns:minmax(120px,.85fr) 28px minmax(190px,1.25fr) 28px minmax(190px,1.15fr) 28px minmax(190px,1.25fr);align-items:stretch;margin:12px 0}.node{border:1px solid var(--line);border-radius:14px;padding:14px;background:#0b1929;min-height:95px}.node b{display:block;margin-bottom:5px}.node small{color:var(--muted);line-height:1.45}.node.operation{border-color:#397e99}.node.diagnosis{border-color:#6656a2}.node.tools{border-color:#487e6c}.arrow{display:grid;place-items:center;color:var(--muted);font-size:20px}.subnodes{display:flex;gap:6px;flex-wrap:wrap;margin-top:9px}.subnodes em{font-style:normal;color:#b8d0df;font-size:10px;border:1px solid var(--line);border-radius:20px;padding:4px 7px}.legend{font-size:11px;color:var(--muted);margin:-3px 0 14px}
.components{display:grid;grid-template-columns:repeat(8,minmax(138px,1fr));gap:8px;margin-bottom:12px}.card{padding:11px;min-height:112px;position:relative;overflow:hidden}.card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:var(--blue)}.card.active:before{background:var(--amber);box-shadow:0 0 16px var(--amber)}.card.done:before{background:var(--green)}.card.failed:before{background:var(--red)}.card h3{font-size:13px;margin:0 0 7px}.card .work{font-size:12px;line-height:1.35;min-height:34px}.card .elapsed{font:11px ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--muted);margin-top:8px}
.filters{display:grid;grid-template-columns:1fr 1fr 1fr 2fr auto auto;gap:8px;padding:11px;margin-bottom:12px}.filters select,.filters input,.filters button{appearance:none;color:var(--text);background:#081523;border:1px solid var(--line);border-radius:9px;padding:9px 11px;font:inherit}.filters button{cursor:pointer}.filters button.on{border-color:var(--cyan);color:var(--cyan)}
.workspace{display:grid;grid-template-columns:minmax(440px,1.35fr) minmax(340px,.85fr);gap:12px}.panel{overflow:hidden}.panel-head{display:flex;justify-content:space-between;align-items:center;padding:12px 15px;border-bottom:1px solid var(--line)}.panel-head h2{font-size:14px;margin:0}.count{font:12px ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--muted)}.log{height:550px;overflow:auto}.row{display:grid;grid-template-columns:90px 94px 90px 1fr;gap:8px;align-items:start;padding:10px 13px;border-bottom:1px solid #183149;cursor:pointer}.row:hover,.row.selected{background:#14304a}.time,.mono{font:11px ui-monospace,SFMono-Regular,Consolas,monospace;color:var(--muted)}.badge{font-size:10px;font-weight:800;letter-spacing:.04em;text-transform:uppercase;border-radius:20px;padding:4px 7px;display:inline-block;border:1px solid var(--line)}.badge.started,.badge.waiting{color:var(--amber)}.badge.succeeded{color:var(--green)}.badge.failed{color:var(--red)}.event-summary{font-size:12px;line-height:1.4}.event-summary b{font-size:11px;color:var(--blue);margin-right:6px}.event-summary small{display:block;color:var(--muted);margin-top:3px}.detail{padding:14px;height:550px;overflow:auto}.empty{color:var(--muted);padding:28px;text-align:center}.detail h3{font-size:17px;margin:0 0 6px}.detail-grid{display:grid;grid-template-columns:110px 1fr;gap:7px;font-size:12px;margin:14px 0}.detail-grid dt{color:var(--muted)}.detail-grid dd{margin:0;overflow-wrap:anywhere}.detail h4{font-size:12px;color:var(--cyan);letter-spacing:.07em;text-transform:uppercase;margin:18px 0 7px}.json{white-space:pre-wrap;overflow-wrap:anywhere;background:#06111d;border:1px solid #1f3c55;border-radius:10px;padding:11px;font:11px/1.5 ui-monospace,SFMono-Regular,Consolas,monospace;color:#cfe5f1}.results{margin-top:12px}.result-item{border-left:3px solid var(--violet);padding:9px 11px;margin:8px 0;background:#111f34;border-radius:0 8px 8px 0}.result-item b{font-size:12px}.result-item p{font-size:12px;color:#c7d8e4;margin:5px 0}.warning{background:#422e14;border:1px solid #8c6630;color:#ffd99a;padding:10px 13px;border-radius:10px;margin-bottom:12px;font-size:12px}
@media(max-width:1200px){.components{grid-template-columns:repeat(4,1fr)}.summary{grid-template-columns:repeat(3,1fr)}}@media(max-width:850px){.shell{padding:12px}.top{flex-direction:column}.flow{grid-template-columns:1fr}.arrow{height:25px;transform:rotate(90deg)}.workspace{grid-template-columns:1fr}.filters{grid-template-columns:1fr 1fr}.log,.detail{height:460px}.components{grid-template-columns:repeat(2,1fr)}}
"""


_SCRIPT = r"""
const INITIAL=window.__CCS_SNAPSHOT__;
const COMPONENTS=['operation','diagnosis','runbook','memory','a2a','mcp','model','runner'];
const LABELS={operation:'Operation Agent',diagnosis:'Diagnosis Agent',runbook:'Runbooks Search',memory:'Incident Memory',a2a:'A2A',mcp:'MCP / Network Tools',model:'Model',runner:'Runner'};
const state={events:[],ids:new Set(),cursor:'',meta:{},selected:null,paused:false,auto:true,connected:true,snapshot:!!INITIAL,inFlight:false};
const $=id=>document.getElementById(id);
const asText=v=>v===null||v===undefined?'—':String(v);
const escapeSearch=v=>asText(v).toLocaleLowerCase();
function addEvents(items){for(const e of items||[]){if(e&&e.event_id&&!state.ids.has(e.event_id)){state.ids.add(e.event_id);state.events.push(e)}}state.events.sort((a,b)=>(a.ts_utc||'').localeCompare(b.ts_utc||'')||(a.writer_id||'').localeCompare(b.writer_id||'')||(a.local_seq||0)-(b.local_seq||0)||(a.event_id||'').localeCompare(b.event_id||''));if(!state.selected&&state.events.length){const first=state.events.find(e=>e.action==='request_received')||state.events.find(e=>e.status==='started')||state.events[0];state.selected=first.event_id}}
function time(v){if(!v)return '—';const d=new Date(v);return Number.isNaN(d.valueOf())?v:d.toLocaleTimeString('ko-KR',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'});}
function elapsed(start,end){const a=new Date(start).valueOf(),b=end?new Date(end).valueOf():Date.now();if(!Number.isFinite(a)||!Number.isFinite(b))return '시간 정보 없음';const s=Math.max(0,Math.floor((b-a)/1000));return s<60?`${s}초`:s<3600?`${Math.floor(s/60)}분 ${s%60}초`:`${Math.floor(s/3600)}시간 ${Math.floor(s%3600/60)}분`;}
function terminal(status){return ['succeeded','failed','skipped'].includes(status)}
function filtered(){const ep=$('episode').value,comp=$('component').value,st=$('statusFilter').value,q=escapeSearch($('search').value);return state.events.filter(e=>(!ep||e.episode_id===ep)&&(!comp||e.component===comp)&&(!st||e.status===st)&&(!q||escapeSearch(`${e.action} ${e.summary} ${JSON.stringify(e.details)}`).includes(q)));}
function renderHeader(){const m=state.meta.manifest||{},s=state.meta.summary||{};const phase=!state.connected?'disconnected':state.snapshot?'finished':state.meta.run_phase||'unknown';const chip=$('liveChip');chip.className='live-chip '+phase;const labels={live:'LIVE · 실행 중',finished:state.snapshot?'OFFLINE SNAPSHOT':'FINISHED · 실행 종료',disconnected:'DISCONNECTED · 연결 끊김',unknown:'상태 확인 중'};chip.querySelector('span:last-child').textContent=labels[phase]||labels.unknown;$('runId').textContent=asText(m.run_id||s.run_id);$('mode').textContent=(m.mode||s.mode||'unknown').toUpperCase();$('mode').style.color=(m.mode||s.mode)==='live'?'var(--amber)':'var(--cyan)';$('runStatus').textContent=asText(m.status||s.status);$('episodesMetric').textContent=`${asText(s.completed_episodes??(m.episodes||[]).length)} / ${asText(s.episodes??((m.seeds||[]).length*(m.faults||[]).length*(m.repeat||1)))}`;$('successMetric').textContent=s.successful_episodes===undefined?'진행 중':asText(s.successful_episodes);$('callsMetric').textContent=asText(s.api_calls??(m.mode==='mock'?0:'진행 중'));const has=state.meta.activity_present||state.events.length;if(!has){$('oldWarning').hidden=false;$('oldWarning').textContent='이 run에는 activity event가 없습니다. 이전 형식의 run이거나 계측 시작 전 상태일 수 있습니다.'}else $('oldWarning').hidden=true;}
function populateEpisodes(){const select=$('episode'),current=select.value;const values=[...new Set(state.events.map(e=>e.episode_id).filter(Boolean))].sort();const existing=[...select.options].slice(1).map(o=>o.value);if(JSON.stringify(values)!==JSON.stringify(existing)){while(select.options.length>1)select.remove(1);for(const v of values){const o=document.createElement('option');o.value=v;o.textContent=v;select.append(o)}select.value=values.includes(current)?current:''}}
function renderCards(){const now=new Date().toISOString(),episode=$('episode').value,runEnded=state.snapshot||state.meta.run_phase==='finished',mode=(state.meta.manifest?.mode||state.meta.summary?.mode||'').toLowerCase();for(const component of COMPONENTS){const events=state.events.filter(e=>e.component===component&&(!episode||e.episode_id===episode));const latest=events.at(-1);const starts=new Map();for(const e of events){if(e.operation_id){if(e.status==='started'||e.status==='waiting')starts.set(e.operation_id,e);if(terminal(e.status))starts.delete(e.operation_id)}}const open=[...starts.values()].at(-1),incomplete=!!open&&runEnded,active=incomplete?null:open,mockModel=component==='model'&&!events.length&&mode==='mock';const card=$('card-'+component);card.className='card '+(mockModel?'done':incomplete?'failed':active?'active':latest?.status==='failed'?'failed':latest&&terminal(latest.status)?'done':'');card.querySelector('.work').textContent=mockModel?'Mock · 모델 호출 없음':incomplete?`${open.summary||open.action} · 종료 시 미완료`:active?.summary||latest?.summary||'대기 중';card.querySelector('.elapsed').textContent=mockModel?'API call 0':incomplete?`${time(open.ts_utc)} · terminal run`:active?`진행 ${elapsed(active.ts_utc,now)}`:latest?`${time(latest.ts_utc)} · ${latest.status}`:'event 없음';}}
function renderLog(){const items=filtered(),log=$('log'),wasBottom=log.scrollHeight-log.scrollTop-log.clientHeight<35;const frag=document.createDocumentFragment();for(const e of items){const row=document.createElement('div');row.className='row'+(state.selected===e.event_id?' selected':'');row.dataset.id=e.event_id;const t=document.createElement('div');t.className='time';t.textContent=time(e.ts_utc);const c=document.createElement('div');c.className='mono';c.textContent=LABELS[e.component]||e.component;const sw=document.createElement('div');const badge=document.createElement('span');badge.className='badge '+e.status;badge.textContent=e.status;sw.append(badge);const body=document.createElement('div');body.className='event-summary';const action=document.createElement('b');action.textContent=e.action;const summary=document.createTextNode(e.summary||'요약 없음');const small=document.createElement('small');small.textContent=`${e.episode_id||'run'} · ${e.operation_id||e.event_id}`;body.append(action,summary,small);row.append(t,c,sw,body);row.addEventListener('click',()=>{state.selected=e.event_id;renderLog();renderDetail()});frag.append(row)}log.replaceChildren(frag);$('visibleCount').textContent=`${items.length} / ${state.events.length}`;if(state.auto&&(wasBottom||!state.selected))log.scrollTop=log.scrollHeight;}
function renderDetail(){const e=state.events.find(x=>x.event_id===state.selected),box=$('detail');box.replaceChildren();if(!e){const p=document.createElement('div');p.className='empty';p.textContent='Activity를 선택하면 curated input/output detail과 operation 관계를 확인할 수 있습니다.';box.append(p);return}const h=document.createElement('h3');h.textContent=e.summary||e.action;box.append(h);const dl=document.createElement('dl');dl.className='detail-grid';for(const [k,v] of [['Component',LABELS[e.component]||e.component],['Action',e.action],['Status',e.status],['Episode',e.episode_id],['Operation ID',e.operation_id],['Writer / sequence',`${e.writer_id} / ${e.local_seq}`],['UTC',e.ts_utc],['Mode',e.mode]]){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=k;dd.textContent=asText(v);dl.append(dt,dd)}box.append(dl);const hh=document.createElement('h4');hh.textContent='Curated input / output detail';const pre=document.createElement('pre');pre.className='json';pre.textContent=JSON.stringify(e.details,null,2);box.append(hh,pre);}
function renderResults(){const box=$('results');box.replaceChildren();const candidates=filtered().filter(e=>{const d=e.details||{};return e.status==='failed'||['verify','report','conclusion','evidence','result','return_results','write'].some(x=>(e.action||'').toLowerCase().includes(x))||['evidence','conclusion','rationale','result','outcome','passed'].some(k=>Object.prototype.hasOwnProperty.call(d,k))}).slice(-8).reverse();if(!candidates.length){const p=document.createElement('div');p.className='empty';p.textContent='현재 필터에 맞는 structured evidence/conclusion 결과가 없습니다.';box.append(p);return}for(const e of candidates){const item=document.createElement('div');item.className='result-item';const b=document.createElement('b');b.textContent=`${LABELS[e.component]||e.component} · ${e.action} · ${e.status}`;const p=document.createElement('p');p.textContent=e.summary||'요약 없음';const code=document.createElement('div');code.className='mono';const d=e.details||{};const chosen={};for(const k of ['evidence','conclusion','rationale','result','outcome','passed'])if(Object.prototype.hasOwnProperty.call(d,k))chosen[k]=d[k];code.textContent=Object.keys(chosen).length?JSON.stringify(chosen):e.episode_id;item.append(b,p,code);item.addEventListener('click',()=>{state.selected=e.event_id;renderLog();renderDetail()});box.append(item)}}
function render(){populateEpisodes();renderHeader();renderCards();renderLog();renderDetail();renderResults();}
async function poll(){if(state.snapshot||state.paused||state.inFlight)return;state.inFlight=true;try{const params=new URLSearchParams(location.search);if(state.cursor)params.set('cursor',state.cursor);const response=await fetch('/api/state?'+params.toString(),{cache:'no-store',credentials:'omit'});if(!response.ok)throw new Error(`HTTP ${response.status}`);const data=await response.json();state.connected=true;state.cursor=data.cursor||state.cursor;state.meta=data.meta||{};addEvents(data.events);render()}catch(error){state.connected=false;renderHeader()}finally{state.inFlight=false}}
for(const id of ['episode','component','statusFilter','search'])$(id).addEventListener(id==='search'?'input':'change',()=>{if(id==='episode')state.selected=filtered()[0]?.event_id||null;renderCards();renderLog();renderDetail();renderResults()});$('pause').addEventListener('click',()=>{state.paused=!state.paused;$('pause').classList.toggle('on',state.paused);$('pause').textContent=state.paused?'새 event 다시 받기':'새 event 일시정지';if(!state.paused)poll()});$('auto').addEventListener('click',()=>{state.auto=!state.auto;$('auto').classList.toggle('on',state.auto);$('auto').textContent=`Auto-scroll ${state.auto?'ON':'OFF'}`});
if(INITIAL){state.meta=INITIAL.meta||{};addEvents(INITIAL.events);render()}else{poll();setInterval(poll,900);setInterval(()=>{renderCards();},1000)}
"""


def _legacy_document(snapshot_payload: dict[str, Any] | None = None) -> str:
    from ccs.monitor_i18n import SCRIPT as language_script
    embedded = "null"
    if snapshot_payload is not None:
        embedded = json.dumps(snapshot_payload, ensure_ascii=False, separators=(",", ":"))
        embedded = embedded.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
        embedded = embedded.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark"><title>CCS NetOps Activity Monitor</title><style>{_STYLE}</style></head>
<body><main class="shell">
<header class="top"><div><div class="eyebrow">CCS · D0 observability</div><h1 class="title">NetOps Agent Activity Monitor</h1><p class="subtitle">요청부터 진단·조치·검증까지 실시간으로 확인합니다.</p></div><div id="liveChip" class="live-chip"><span class="dot"></span><span>상태 확인 중</span></div></header>
<div id="oldWarning" class="warning" hidden></div>
<section class="summary"><div class="metric"><span>Run ID</span><strong id="runId">—</strong></div><div class="metric"><span>Mode</span><strong id="mode">—</strong></div><div class="metric"><span>Run status</span><strong id="runStatus">—</strong></div><div class="metric"><span>Episodes</span><strong id="episodesMetric">—</strong></div><div class="metric"><span>Successful</span><strong id="successMetric">—</strong></div><div class="metric"><span>API calls</span><strong id="callsMetric">—</strong></div></section>
<section class="flow" aria-label="NetOps workflow"><div class="node"><b>Human Operator</b><small>장애 요청을 보내고 최종 evidence와 conclusion을 받습니다.</small></div><div class="arrow">→</div><div class="node operation"><b>Operation Agent</b><small>Workflow &amp; Action · 변경과 검증을 소유합니다.</small><div class="subnodes"><em>Runbooks Search</em><em>Incident Memory R/W</em></div></div><div class="arrow">⇄</div><div class="node diagnosis"><b>Diagnosis Agent</b><small>A2A Delegate / Return Results · Cause &amp; Remedy · read-only MCP</small></div><div class="arrow">→</div><div class="node tools"><b>Network Tools</b><small>MCP · Operation: read/change/verify · Diagnosis: read only</small></div></section>
<p class="legend">표시 순서: 관측된 UTC timestamp + writer/local sequence. 분산 component 사이의 완전한 인과관계를 보장하지 않습니다.</p>
<section id="components" class="components">{''.join(f'<article id="card-{c}" class="card"><h3>{label}</h3><div class="work">대기 중</div><div class="elapsed">event 없음</div></article>' for c,label in ((c, {"operation":"Operation Agent","diagnosis":"Diagnosis Agent","runbook":"Runbooks Search","memory":"Incident Memory","a2a":"A2A","mcp":"MCP / Network Tools","model":"Model","runner":"Runner"}[c]) for c in ("operation","diagnosis","runbook","memory","a2a","mcp","model","runner")))}</section>
<section class="panel filters"><select id="episode"><option value="">모든 episode</option></select><select id="component"><option value="">모든 component</option>{''.join(f'<option value="{c}">{c}</option>' for c in ("operation","diagnosis","runbook","memory","a2a","mcp","model","runner"))}</select><select id="statusFilter"><option value="">모든 status</option>{''.join(f'<option value="{s}">{s}</option>' for s in ("started","succeeded","failed","waiting","skipped","info"))}</select><input id="search" type="search" placeholder="action, summary, detail 검색"><button id="pause">새 event 일시정지</button><button id="auto" class="on">Auto-scroll ON</button></section>
<section class="workspace"><article class="panel"><div class="panel-head"><h2>Ordered activity log</h2><span id="visibleCount" class="count">0 / 0</span></div><div id="log" class="log"></div></article><aside><article class="panel"><div class="panel-head"><h2>선택한 활동 · 입력과 결과</h2></div><div id="detail" class="detail"><div class="empty">활동을 선택하세요.</div></div></article><article class="panel results"><div class="panel-head"><h2>Results · Evidence · Rationale</h2></div><div id="results"></div></article></aside></section>
</main><script>window.__CCS_SNAPSHOT__={embedded};{_SCRIPT}\n{language_script}</script></body></html>"""


_STUDIO_STYLE = r"""
:root{color-scheme:light;--bg:#f5f5f7;--surface:#fff;--surface-soft:#fafafa;--ink:#1d1d1f;--muted:#6e6e73;--hair:#d9d9de;--blue:#0071e3;--green:#248a3d;--red:#d92d20;--shadow:0 18px 50px rgba(0,0,0,.07);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Segoe UI",sans-serif}
*{box-sizing:border-box}html{background:var(--bg);scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--ink);min-height:100vh}.shell{width:min(1500px,100%);margin:0 auto;padding:32px 28px 56px}.top{display:flex;align-items:flex-start;justify-content:space-between;gap:28px;margin-bottom:22px}.eyebrow{color:var(--blue);font-size:11px;font-weight:750;letter-spacing:.12em;text-transform:uppercase}.title{font-size:clamp(30px,4vw,52px);line-height:1.02;letter-spacing:-.045em;margin:8px 0 10px}.subtitle{color:var(--muted);font-size:16px;line-height:1.5;margin:0}.header-actions{display:flex;align-items:center;gap:10px}.language{border:1px solid var(--hair);border-radius:980px;background:#fff;padding:9px 30px 9px 13px;color:var(--ink);font:inherit}.live-chip{display:flex;align-items:center;gap:8px;border:1px solid var(--hair);background:#fff;padding:10px 14px;border-radius:980px;font-size:13px;font-weight:650;white-space:nowrap;box-shadow:0 4px 16px rgba(0,0,0,.04)}.dot{width:8px;height:8px;border-radius:50%;background:#8e8e93}.live .dot{background:#34c759;box-shadow:0 0 0 5px rgba(52,199,89,.14)}.finished .dot{background:var(--blue)}.disconnected .dot{background:var(--red)}
.summary{display:grid;grid-template-columns:1.65fr repeat(5,minmax(105px,1fr));gap:10px;margin-bottom:16px}.metric{min-width:0;background:rgba(255,255,255,.82);border:1px solid rgba(0,0,0,.07);border-radius:16px;padding:13px 15px}.metric span{display:block;color:var(--muted);font-size:11px;font-weight:650;letter-spacing:.05em;text-transform:uppercase}.metric strong{display:block;margin-top:5px;font-size:17px;line-height:1.25;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.warning{background:#fff8e6;border:1px solid #f2d285;color:#6f4e00;border-radius:14px;padding:12px 14px;margin-bottom:14px;font-size:13px}
.panel{background:var(--surface);border:1px solid rgba(0,0,0,.07);border-radius:22px;box-shadow:var(--shadow)}.topology-panel{padding:22px 22px 14px;margin-bottom:14px;overflow:hidden}.section-head{display:flex;align-items:flex-end;justify-content:space-between;gap:18px;margin-bottom:8px}.section-head h2{font-size:19px;letter-spacing:-.02em;margin:0}.section-head p{color:var(--muted);font-size:12px;margin:0;text-align:right}.topology{display:block;width:100%;height:auto;min-height:430px}.node{cursor:pointer;outline:none}.node .node-surface{fill:#fff;stroke:#d4d4d9;stroke-width:1.5;transition:stroke .2s,filter .2s}.node:hover .node-surface,.node.selected .node-surface{stroke:var(--activity,var(--blue));stroke-width:2.5;filter:drop-shadow(0 8px 16px rgba(0,0,0,.1))}.node-title{fill:var(--ink);font-size:19px;font-weight:720;letter-spacing:-.02em}.node-caption{fill:var(--muted);font-size:12px}.icon-stroke{fill:none;stroke:#515154;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}.sub-chip rect{fill:#f5f5f7;stroke:#e2e2e7;stroke-width:1;transition:all .22s}.sub-chip text{fill:#515154;font-size:10.5px;font-weight:650;text-anchor:middle}.sub-chip.active rect{fill:#fff;stroke:var(--activity,var(--blue));stroke-width:2;filter:drop-shadow(0 0 9px var(--activity,var(--blue)))}.sub-chip.selected rect{stroke:var(--activity,var(--blue));stroke-width:2}.route{cursor:pointer;outline:none;--route:#6e6e73}.route-line{fill:none;stroke:var(--route);stroke-width:2.6;opacity:.22;transition:opacity .22s,stroke-width .22s}.route-hit{fill:none;stroke:transparent;stroke-width:22}.route text{fill:var(--route);font-size:11px;font-weight:720;opacity:.7;text-anchor:middle;paint-order:stroke;stroke:#fff;stroke-width:5px;stroke-linejoin:round}.route:hover .route-line,.route.selected .route-line{opacity:1;stroke-width:4}.route.active .route-line{opacity:1;stroke-width:4.5;stroke-dasharray:8 7;animation:route-flow 1.1s linear infinite}.route.active text,.route.selected text{opacity:1}.route.internal{pointer-events:none}.route.internal .route-line{stroke-dasharray:4 6;opacity:.12}@keyframes route-flow{to{stroke-dashoffset:-30}}
.topology-legend{display:flex;align-items:center;justify-content:space-between;gap:16px;color:var(--muted);font-size:11px;border-top:1px solid #ededf0;padding-top:12px}.legend-routes{display:flex;gap:12px;flex-wrap:wrap}.legend-routes span{display:inline-flex;align-items:center;gap:5px}.legend-routes i{display:block;width:16px;height:3px;border-radius:4px;background:var(--swatch)}
.filters{display:grid;grid-template-columns:minmax(155px,.8fr) minmax(150px,.8fr) minmax(135px,.7fr) minmax(230px,1.6fr) auto auto;gap:8px;padding:11px;margin-bottom:14px;box-shadow:none}.filters select,.filters input,.filters button{min-width:0;border:1px solid var(--hair);border-radius:11px;background:#fff;color:var(--ink);padding:10px 12px;font:inherit;font-size:13px}.filters button{cursor:pointer;font-weight:650}.filters button.on{background:#eaf3ff;border-color:#8bbef0;color:#0059b3}
.workspace{display:grid;grid-template-columns:minmax(520px,1.35fr) minmax(360px,.85fr);gap:14px;align-items:start}.timeline-panel,.detail-panel{overflow:hidden}.panel-head{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid #ededf0;padding:15px 18px}.panel-head h2{font-size:15px;margin:0}.count{color:var(--muted);font:12px ui-monospace,SFMono-Regular,Consolas,monospace}.log{height:620px;overflow:auto;overscroll-behavior:contain}.row{--route:#6e6e73;display:grid;grid-template-columns:82px minmax(0,1fr) auto;gap:12px;align-items:start;border-left:4px solid var(--route);border-bottom:1px solid #ededf0;padding:13px 14px 13px 12px;cursor:pointer;background:#fff}.row:hover{background:#fafafa}.row.selected{background:#f2f7fd;box-shadow:inset 0 0 0 1px rgba(0,113,227,.12)}.time{color:var(--muted);font:11px/1.45 ui-monospace,SFMono-Regular,Consolas,monospace}.event-headline{font-size:13px;font-weight:720;line-height:1.35;margin-bottom:4px}.event-detail{color:#515154;font-size:12px;line-height:1.45}.event-meta{color:#8e8e93;font:10.5px/1.4 ui-monospace,SFMono-Regular,Consolas,monospace;margin-top:5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.badge{display:inline-flex;border-radius:980px;padding:4px 8px;font-size:10px;font-weight:760;letter-spacing:.02em;background:#f1f1f3;color:#515154}.badge.started,.badge.waiting{background:#fff4d6;color:#805b00}.badge.succeeded{background:#eaf7ed;color:#176b2d}.badge.failed{background:#fff0ee;color:var(--red)}.badge.skipped{background:#f1f1f3;color:#6e6e73}.empty{color:var(--muted);font-size:13px;line-height:1.55;padding:42px 24px;text-align:center}
.detail{min-height:620px;max-height:760px;overflow:auto;padding:20px}.detail h3{font-size:22px;letter-spacing:-.025em;line-height:1.2;margin:0 0 8px}.detail-lead{color:#515154;font-size:13px;line-height:1.55;margin:0 0 16px}.detail-grid{display:grid;grid-template-columns:120px minmax(0,1fr);gap:9px 14px;border-top:1px solid #ededf0;border-bottom:1px solid #ededf0;padding:16px 0;margin:0}.detail-grid dt{color:var(--muted);font-size:11px}.detail-grid dd{font-size:12px;margin:0;overflow-wrap:anywhere}.raw{margin-top:16px;border:1px solid #e1e1e6;border-radius:14px;overflow:hidden}.raw summary{cursor:pointer;padding:12px 14px;font-size:12px;font-weight:700;background:#fafafa}.raw-hint{color:var(--muted);font-size:11px;padding:0 14px;margin:10px 0 0}.json{white-space:pre-wrap;overflow-wrap:anywhere;margin:10px 12px 12px;padding:12px;border-radius:10px;background:#f5f5f7;color:#333336;font:10.5px/1.55 ui-monospace,SFMono-Regular,Consolas,monospace}.technical{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.generic-note{display:inline-block;margin-bottom:12px;background:#f1f1f3;color:#515154;border-radius:980px;padding:5px 9px;font-size:10px;font-weight:700}
.embedded .top,.embedded .summary{display:none}.embedded .shell{padding-top:12px;padding-left:12px;padding-right:12px}
@media(max-width:1100px){.summary{grid-template-columns:repeat(3,1fr)}.workspace{grid-template-columns:1fr}.log{height:520px}.detail{min-height:0;max-height:none}.filters{grid-template-columns:repeat(3,1fr)}.topology{min-height:360px}.section-head{align-items:flex-start;flex-direction:column}.section-head p{text-align:left}}
@media(max-width:720px){.shell{padding:18px 10px 36px}.top{flex-direction:column}.header-actions{width:100%;justify-content:space-between}.summary{grid-template-columns:repeat(2,1fr)}.topology-panel{padding:14px 8px 10px;overflow:auto}.topology{width:1080px;min-height:auto}.topology-legend{align-items:flex-start;flex-direction:column}.filters{grid-template-columns:1fr 1fr}.workspace{grid-template-columns:minmax(0,1fr)}.row{grid-template-columns:70px minmax(0,1fr)}.row .badge{grid-column:2;justify-self:start}.log{height:480px}}
.topology{height:clamp(430px,38vw,520px);min-height:0}.route{pointer-events:bounding-box}.route-hit{pointer-events:stroke}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.route.active .route-line{animation:none}}
"""


_STUDIO_STYLE += r"""
.workflow-board{display:grid;grid-template-columns:minmax(0,2.2fr) minmax(350px,1fr);gap:16px;align-items:stretch;height:680px;margin-bottom:16px}
.workflow-board .topology-panel{margin:0;min-width:0;display:flex;flex-direction:column;padding:22px 20px 16px}
.workflow-board .section-head{align-items:flex-start;flex-direction:column;gap:7px;margin-bottom:10px}
.workflow-board .section-head h2{font-size:18px}.workflow-board .section-head p{text-align:left;font-size:11px;line-height:1.5}
.workflow-board .topology{width:100%;height:auto;min-height:0;flex:1 1 0}
.workflow-board .topology-legend{flex-direction:column;align-items:flex-start;gap:9px;padding-top:12px;font-size:10px;line-height:1.5}
.workflow-board .legend-routes{gap:11px;font-size:10px}
.timeline-panel{min-width:0;display:flex;flex-direction:column;overflow:hidden}
.timeline-panel .panel-head{padding:18px 17px 13px;border-bottom:0;gap:10px}.timeline-heading{display:flex;align-items:center;gap:9px}.timeline-panel .panel-head h2{font-size:16px}.order-badge{font-size:10px;font-weight:600;padding:4px 7px;border-radius:6px;background:#f2f6fb;color:#617184}.timeline-panel .count{font-size:10px;white-space:nowrap}
.timeline-controls.filters{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;padding:0 14px 13px;margin:0;border:0;border-radius:0;box-shadow:none;background:none}
.timeline-controls input{grid-column:1/-1;grid-row:1;min-width:0}.timeline-controls select,.timeline-controls input,.timeline-controls button{font-size:11px;padding:8px;border-radius:9px;min-width:0;background:#fafafb;border:1px solid #e5e5ea;color:#515154}.timeline-controls select{appearance:auto;overflow:hidden;text-overflow:ellipsis}.timeline-controls input{background:#fff}
.timeline-actions{grid-column:1/-1;display:flex;gap:8px}.timeline-actions button{flex:1;cursor:pointer}.timeline-actions button.on{background:#eff6ff;border-color:#bfd9f5;color:#0071e3}
.timeline-panel .log{position:relative;height:0;min-height:0;flex:1;overflow:auto;overflow-anchor:none;border-top:1px solid #ededf0;scrollbar-gutter:stable}
.timeline-panel .row{grid-template-columns:minmax(0,1fr) auto;gap:6px 10px;padding:12px 13px 12px 12px}
.timeline-panel .row .time{grid-column:1;grid-row:1;font-size:10px;align-self:center}.timeline-panel .row .badge{grid-column:2;grid-row:1;justify-self:end;align-self:center;font-size:9px;padding:3px 7px}.timeline-panel .event-body{grid-column:1/-1;grid-row:2;min-width:0}.timeline-panel .event-headline{font-size:12.5px;font-weight:650}.timeline-panel .event-detail{font-size:11.5px}.timeline-panel .event-meta{font-size:9.5px}.row:focus-visible{outline:2px solid var(--blue);outline-offset:-3px}
.detail-panel{margin-top:0;overflow:hidden}.detail-panel>summary{cursor:pointer;list-style:none;display:flex;align-items:center;padding:17px 21px;gap:16px;border-bottom:0}.detail-panel>summary::-webkit-details-marker{display:none}.detail-panel>summary h2{font-size:14px;margin:0;white-space:nowrap}.detail-preview{font-size:12px;color:var(--muted);overflow:hidden;white-space:nowrap;text-overflow:ellipsis;flex:1}.detail-chevron{font-size:17px;color:#8e8e93;transition:transform .15s}.detail-panel[open] .detail-chevron{transform:rotate(90deg)}.detail-panel[open]>summary{border-bottom:1px solid #ededf0}
.detail-panel .detail{min-height:0;max-height:420px;padding:20px 22px}.detail-panel .detail h3{font-size:19px}.detail-panel .detail-grid{grid-template-columns:105px minmax(0,1fr) 105px minmax(0,1fr);gap:10px 16px}.detail-panel .raw{margin-top:15px}.detail-panel .json{max-height:260px;overflow:auto}
@media(max-width:1100px){.workflow-board{grid-template-columns:1fr;height:auto}.workflow-board .topology-panel{min-height:570px}.workflow-board .topology{height:450px;flex:none}.timeline-panel{height:620px}.detail-panel .detail-grid{grid-template-columns:105px minmax(0,1fr)}.detail-panel .detail{max-height:520px}.timeline-controls.filters{grid-template-columns:repeat(3,minmax(0,1fr))}}
@media(max-width:720px){.workflow-board{gap:12px}.workflow-board .topology-panel{min-height:0;padding:17px 12px 12px;overflow:auto}.workflow-board .topology{width:1080px;height:540px;flex:none}.timeline-panel{height:600px}.timeline-panel .row{grid-template-columns:minmax(0,1fr) auto}.timeline-panel .row .badge{grid-column:2;grid-row:1}.detail-panel>summary{padding:15px;gap:10px}.detail-panel .detail{padding:15px}.detail-preview{font-size:11px}.timeline-controls select{font-size:10px}}
"""


_STUDIO_STYLE += r"""
.event-direction{font-size:10px;font-weight:600;color:var(--route);margin-bottom:5px;line-height:1.55}.event-fields{font-size:10px;color:var(--muted);margin-top:7px;line-height:1.65}
.communication-banner{padding:12px 15px;border:1px solid #e2eaf5;background:#f5f9ff;border-radius:10px;font-size:12px;font-weight:600;margin:14px 0;color:#245583}.message-payloads{display:grid;gap:8px;margin:12px 0 20px}.message-section{border:1px solid #e5e5ea;border-radius:10px;overflow:hidden}.message-section>summary{padding:11px 13px;font-size:12px;cursor:pointer;background:#fafafb}.message-section pre{padding:13px;margin:0;font:11px/1.7 ui-monospace,Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;max-height:300px;overflow:auto;color:#343438}
"""


_STUDIO_SCRIPT = r"""
const INITIAL=window.__CCS_SNAPSHOT__;
const ROUTE_COLORS={request:'#0071e3',rag:'#af52de',memory:'#00897b',delegate:'#5856d6',return:'#6e5ce6',op_mcp:'#c77800',diag_mcp:'#008db3',report:'#248a3d',internal:'#6e6e73'};
const ROUTE_LABEL_KEYS={request:'routeRequest',rag:'routeRag',memory:'routeMemory',delegate:'routeDelegate',return:'routeReturn',op_mcp:'routeOpMcp',diag_mcp:'routeDiagMcp',report:'routeReport',internal:'routeInternal'};
const NODE_LABEL_KEYS={human:'human',operation:'operation',diagnosis:'diagnosis',runbook:'runbook',memory:'memory',tools:'tools'};
const state={events:[],ids:new Set(),cursor:'',meta:{},selected:null,paused:false,auto:true,connected:true,snapshot:!!INITIAL,inFlight:false};
const $=id=>document.getElementById(id);
const asText=v=>v===null||v===undefined||v===''?'—':String(v);
const terminal=s=>['succeeded','failed','skipped'].includes(s);
const searchText=v=>String(v??'').toLocaleLowerCase();
const eventEpoch=v=>{const value=Date.parse(v||'');return Number.isFinite(value)?value:0};
const communicationOf=e=>e?.presentation?.communication||{};
const endpoint=(id,c)=>id==='model'&&c.model?c.model:t('endpoint_'+(id||'unknown'));
const messageKind=c=>t(({request:'requestMessage',response:'responseMessage',request_failed:'failedRequest',internal:'internalMessage'})[c.kind]||'internalMessage');
function communicationText(e){const c=communicationOf(e);return c.kind==='internal'?`${endpoint(c.source,c)} · ${t('internalMessage')}`:`${endpoint(c.source,c)} → ${endpoint(c.destination,c)} · ${messageKind(c)}`}

function postMonitorHeight(){
  if(window.self===window.top)return;
  // Measure content, not the iframe viewport: body min-height is viewport-sized.
  // Using scrollHeight here feeds the parent's height back into the next update.
  const shell=document.querySelector('main.shell');
  if(!shell)return;
  const height=Math.ceil(shell.getBoundingClientRect().height);
  if(height<=0)return;
  try{window.parent.postMessage({type:'ccs-monitor-height',height},location.origin)}catch{}
}
function addEvents(items){
  let added=false;
  for(const event of items||[])if(event?.event_id&&!state.ids.has(event.event_id)){state.ids.add(event.event_id);state.events.push(event);added=true}
  if(added)state.events.sort((a,b)=>eventEpoch(a.ts_utc)-eventEpoch(b.ts_utc)||(a.ts_utc||'').localeCompare(b.ts_utc||'')||(a.writer_id||'').localeCompare(b.writer_id||'')||(a.local_seq||0)-(b.local_seq||0)||(a.event_id||'').localeCompare(b.event_id||''));
  if(!state.selected&&state.events.length)state.selected=(state.events.find(e=>e.action==='request_received')||state.events.find(e=>e.status==='started')||state.events[0]).event_id;
  return added;
}
function time(value){
  if(!value)return '—';const date=new Date(value);
  return Number.isNaN(date.valueOf())?value:date.toLocaleTimeString(monitorLanguage==='ko'?'ko-KR':'en-GB',{hour12:false,hour:'2-digit',minute:'2-digit',second:'2-digit'});
}
function filtered(){
  const episode=$('episode').value,route=$('routeFilter').value,status=$('statusFilter').value,q=searchText($('search').value);
  return state.events.filter(event=>(!episode||event.episode_id===episode)&&(!route||event.presentation?.route===route)&&(!status||event.status===status)&&(!q||searchText([
    event.action,event.summary,eventText(event,'headline'),eventText(event,'detail'),communicationText(event),event.presentation?.tool,event.presentation?.target,JSON.stringify(event.details)
  ].join(' ')).includes(q)));
}
function runFinished(){return state.meta.run_phase==='finished'}
function routeStages(event){
  const route=event?.presentation?.route,primary={node:event?.presentation?.node,submodule:event?.presentation?.submodule};
  const stages={
    request:[{node:'human',submodule:'request'},{node:'operation',submodule:'context'}],
    report:[{node:'operation',submodule:'report'},{node:'human',submodule:'report'}],
    delegate:[{node:'operation',submodule:'context'},{node:'diagnosis',submodule:'inspect'}],
    return:[{node:'diagnosis',submodule:'conclusion'},{node:'operation',submodule:'context'}],
    rag:[{node:'operation',submodule:'context'},{node:'runbook',submodule:event?.presentation?.submodule||'search'}],
    memory:[{node:'operation',submodule:event?.presentation?.submodule==='write'?'report':'context'},{node:'memory',submodule:event?.presentation?.submodule||'read'}],
    op_mcp:[{node:'operation',submodule:'action'},{node:'tools',submodule:event?.presentation?.submodule||'read'}],
    diag_mcp:[{node:'diagnosis',submodule:'evidence'},{node:'tools',submodule:event?.presentation?.submodule||'read'}]
  };
  const result=stages[route]||[primary];
  if(primary.node&&!result.some(stage=>stage.node===primary.node&&stage.submodule===primary.submodule))result.push(primary);
  return result;
}
function openOperations(){
  if(runFinished())return [];
  const episode=$('episode').value,open=new Map();
  for(const event of state.events){
    if(episode&&event.episode_id!==episode)continue;
    if(event.presentation?.track_active===false)continue;
    if(!event.operation_id)continue;
    if(event.status==='started'||event.status==='waiting')open.set(event.operation_id,event);
    else if(terminal(event.status))open.delete(event.operation_id);
  }
  return [...open.values()];
}
function staleOperationIds(){
  if(!runFinished())return new Set();
  const open=new Set();
  for(const event of state.events){
    if(!event.operation_id)continue;
    if(event.status==='started'||event.status==='waiting')open.add(event.operation_id);
    else if(terminal(event.status))open.delete(event.operation_id);
  }
  return open;
}
function renderHeader(){
  const manifest=state.meta.manifest||{},summary=state.meta.summary||{};
  const phase=!state.connected?'disconnected':state.snapshot?'finished':state.meta.run_phase||'unknown';
  const chip=$('liveChip');chip.className='live-chip '+phase;
  chip.querySelector('span:last-child').textContent=phase==='live'?t('live'):phase==='finished'?(state.snapshot?t('snapshot'):t('finished')):phase==='disconnected'?t('disconnected'):t('unknown');
  $('runId').textContent=asText(manifest.run_id||summary.run_id);
  $('mode').textContent=(manifest.mode||summary.mode||'unknown').toUpperCase();
  $('runStatus').textContent=asText(manifest.status||summary.status);
  const total=summary.episodes??((manifest.seeds||[]).length*(manifest.faults||[]).length*(manifest.repeat||1));
  $('episodesMetric').textContent=`${asText(summary.completed_episodes??(manifest.episodes||[]).length)} / ${asText(total)}`;
  $('successMetric').textContent=summary.successful_episodes===undefined?t('inProgress'):asText(summary.successful_episodes);
  $('callsMetric').textContent=asText(summary.api_calls??(manifest.mode==='mock'?0:t('inProgress')));
  const has=state.meta.activity_present||state.events.length;
  $('oldWarning').hidden=!!has;$('oldWarning').textContent=t('oldRun');
  $('pause').textContent=state.paused?t('resume'):t('pause');
  $('auto').textContent=state.auto?t('autoOn'):t('autoOff');
}
function populateEpisodes(){
  const select=$('episode'),current=select.value,values=[...new Set(state.events.map(e=>e.episode_id).filter(Boolean))].sort();
  const currentValues=[...select.options].slice(1).map(o=>o.value);
  if(JSON.stringify(values)===JSON.stringify(currentValues))return;
  const all=new Option(t('allEpisodes'),'');all.dataset.i18n='allEpisodes';select.replaceChildren(all);
  for(const value of values)select.append(new Option(value,value));
  select.value=values.includes(current)?current:'';
}
function renderTopology(){
  const active=openOperations(),activeRoutes=new Set(active.map(e=>e.presentation?.route)),selected=state.events.find(e=>e.event_id===state.selected);
  const selectedRoute=selected?.presentation?.route,selectedStages=routeStages(selected);
  for(const group of document.querySelectorAll('.route[data-route]')){
    const route=group.dataset.route;group.classList.toggle('active',activeRoutes.has(route));group.classList.toggle('selected',route===selectedRoute);
  }
  for(const group of document.querySelectorAll('.node[data-node]')){
    const node=group.dataset.node,matching=active.filter(e=>routeStages(e).some(stage=>stage.node===node)),color=ROUTE_COLORS[matching.at(-1)?.presentation?.route||selectedRoute||'internal'];
    group.style.setProperty('--activity',color);group.classList.toggle('selected',selectedStages.some(stage=>stage.node===node));
  }
  for(const chip of document.querySelectorAll('.sub-chip[data-node][data-submodule]')){
    const activeEvent=active.find(e=>routeStages(e).some(stage=>stage.node===chip.dataset.node&&stage.submodule===chip.dataset.submodule));
    const chosen=selectedStages.some(stage=>stage.node===chip.dataset.node&&stage.submodule===chip.dataset.submodule);
    chip.classList.toggle('active',!!activeEvent);chip.classList.toggle('selected',chosen);
    chip.style.setProperty('--activity',ROUTE_COLORS[activeEvent?.presentation?.route||selectedRoute||'internal']);
  }
}
function selectLatest(predicate){
  const candidates=state.events.filter(predicate);const event=candidates.at(-1);if(!event)return;
  chooseEvent(event);
  requestAnimationFrame(()=>{
    const log=$('log'),row=[...log.children].find(item=>item.dataset.id===event.event_id);if(!row)return;
    if(row.offsetTop<log.scrollTop)log.scrollTop=row.offsetTop;
    else if(row.offsetTop+row.offsetHeight>log.scrollTop+log.clientHeight)log.scrollTop=row.offsetTop+row.offsetHeight-log.clientHeight;
  });
}
function chooseEvent(event){
  state.selected=event.event_id;$('activityInspector').open=true;
  renderTopology();renderTimeline();renderDetail();postMonitorHeight();
}
function renderTimeline(){
  // Keep state.events chronological for operation tracking; only the view is reversed.
  const items=filtered().slice().reverse(),log=$('log'),oldScroll=log.scrollTop,wasTop=oldScroll<40,stale=staleOperationIds(),fragment=document.createDocumentFragment();
  const logTop=log.getBoundingClientRect().top;
  const anchor=[...log.children].find(row=>row.dataset.id&&row.getBoundingClientRect().bottom>logTop+1);
  const anchorId=anchor?.dataset.id,anchorOffset=anchor?anchor.getBoundingClientRect().top-logTop:0;
  if(!items.length){const empty=document.createElement('div');empty.className='empty';empty.textContent=t('emptyTimeline');fragment.append(empty)}
  for(const event of items){
    const route=event.presentation?.route||'internal',row=document.createElement('div');row.className='row'+(event.event_id===state.selected?' selected':'');row.dataset.id=event.event_id;row.style.setProperty('--route',ROUTE_COLORS[route]||ROUTE_COLORS.internal);
    const stamp=document.createElement('div');stamp.className='time';stamp.textContent=time(event.ts_utc);
    const body=document.createElement('div'),headline=document.createElement('div'),detail=document.createElement('div'),meta=document.createElement('div'),direction=document.createElement('div');body.className='event-body';
    direction.className='event-direction';direction.textContent=communicationText(event);
    headline.className='event-headline';headline.textContent=eventText(event,'headline')||t('generic');
    detail.className='event-detail';detail.textContent=stale.has(event.operation_id)&&!terminal(event.status)?t('stale'):(eventText(event,'detail')||t('generic'));
    meta.className='event-meta';meta.textContent=`${t(ROUTE_LABEL_KEYS[route]||'generic')} · ${event.presentation?.tool||event.presentation?.target||event.episode_id||'run'}`;
    body.append(direction,headline,detail);
    if(event.component==='a2a'&&communicationOf(event).sections?.length){const fields=document.createElement('div');fields.className='event-fields';fields.textContent=communicationOf(event).sections.map(s=>s.label?.[monitorLanguage]||s.key).join(' · ');body.append(fields)}
    body.append(meta);
    const badge=document.createElement('span');badge.className='badge '+event.status;badge.textContent=statusText(event.status);
    row.append(stamp,body,badge);row.tabIndex=0;row.setAttribute('role','button');row.setAttribute('aria-pressed',String(event.event_id===state.selected));
    row.addEventListener('click',()=>chooseEvent(event));row.addEventListener('keydown',key=>{if(key.key==='Enter'||key.key===' '){key.preventDefault();chooseEvent(event)}});fragment.append(row);
  }
  log.replaceChildren(fragment);$('visibleCount').textContent=`${items.length} / ${state.events.length}`;
  if(state.auto&&wasTop)log.scrollTop=0;
  else{
    const nextAnchor=[...log.children].find(row=>row.dataset.id===anchorId);
    log.scrollTop=nextAnchor?Math.max(0,log.scrollTop+nextAnchor.getBoundingClientRect().top-log.getBoundingClientRect().top-anchorOffset):oldScroll;
  }
}
function renderDetail(){
  const event=state.events.find(e=>e.event_id===state.selected),box=$('detail'),oldScroll=box.scrollTop;box.replaceChildren();
  $('detailPreview').textContent=event?(eventText(event,'headline')||t('generic')):t('selectActivity');
  if(!event){const empty=document.createElement('div');empty.className='empty';empty.textContent=t('selectActivity');box.append(empty);postMonitorHeight();return}
  if(event.presentation?.generic){const generic=document.createElement('span');generic.className='generic-note';generic.textContent=t('generic');box.append(generic)}
  const heading=document.createElement('h3');heading.textContent=eventText(event,'headline')||t('generic');
  const lead=document.createElement('p');lead.className='detail-lead';lead.textContent=eventText(event,'detail')||t('generic');box.append(heading,lead);
  const comm=communicationOf(event),banner=document.createElement('div');banner.className='communication-banner';banner.textContent=communicationText(event)+(comm.kind!=='internal'?` · ${comm.protocol||''}`:'');box.append(banner);
  if(comm.sections?.length){
    const title=document.createElement('h4');title.textContent=t('messageContent');box.append(title);
    const payloads=document.createElement('div');payloads.className='message-payloads';
    for(const section of comm.sections){const panel=document.createElement('details'),label=document.createElement('summary'),value=document.createElement('pre');panel.className='message-section';panel.open=['incident','response','diagnosis','arguments','result','report'].includes(section.key);label.textContent=section.label?.[monitorLanguage]||section.label?.en||section.key;value.textContent=typeof section.value==='string'?section.value:JSON.stringify(section.value,null,2);panel.append(label,value);payloads.append(panel)}
    box.append(payloads);
  }
  const pairs=[
    [t('actor'),event.presentation?.actor],[t('channel'),t(ROUTE_LABEL_KEYS[event.presentation?.route]||'generic')],
    [t('nodeStage'),`${t(NODE_LABEL_KEYS[event.presentation?.node]||event.presentation?.node)} / ${t(event.presentation?.submodule||'generic')}`],
    [t('component'),event.component],[t('actionField'),event.action],[t('status'),statusText(event.status)],[t('episode'),event.episode_id],
    [t('operationId'),event.operation_id],[t('writerSequence'),`${event.writer_id} / ${event.local_seq}`],[t('utc'),event.ts_utc],[t('modeField'),event.mode]
  ];
  if(event.presentation?.tool)pairs.splice(3,0,['Tool',event.presentation.tool]);
  if(event.presentation?.target)pairs.splice(4,0,['Target',event.presentation.target]);
  const dl=document.createElement('dl');dl.className='detail-grid';
  for(const [key,value] of pairs){const dt=document.createElement('dt'),dd=document.createElement('dd');dt.textContent=key;dd.textContent=asText(value);if(['Tool','Target',t('operationId')].includes(key))dd.className='technical';dl.append(dt,dd)}box.append(dl);
  const raw=document.createElement('details');raw.className='raw';const summary=document.createElement('summary');summary.textContent=t('rawTitle');const hint=document.createElement('p');hint.className='raw-hint';hint.textContent=t('rawHint');const pre=document.createElement('pre');pre.className='json';
  const original={event_id:event.event_id,ts_utc:event.ts_utc,run_id:event.run_id,episode_id:event.episode_id,writer_id:event.writer_id,local_seq:event.local_seq,component:event.component,action:event.action,status:event.status,summary:event.summary,details:event.details,operation_id:event.operation_id,mode:event.mode};
  pre.textContent=JSON.stringify(original,null,2);raw.append(summary,hint,pre);box.append(raw);box.scrollTop=oldScroll;postMonitorHeight();
}
function render(){
  populateEpisodes();renderHeader();renderTopology();renderTimeline();renderDetail();applyMonitorLanguage();postMonitorHeight();
}
async function poll(){
  if(state.snapshot||state.paused||state.inFlight)return;state.inFlight=true;
  try{
    const params=new URLSearchParams(location.search);if(state.cursor)params.set('cursor',state.cursor);
    const response=await fetch('/api/state?'+params.toString(),{cache:'no-store',credentials:'omit'});if(!response.ok)throw new Error(`HTTP ${response.status}`);
    const data=await response.json(),previousPhase=state.meta.run_phase,added=addEvents(data.events);
    state.connected=true;state.cursor=data.cursor||state.cursor;state.meta=data.meta||{};
    renderHeader();renderTopology();
    if(added||previousPhase!==state.meta.run_phase){populateEpisodes();renderTimeline();renderDetail();applyMonitorLanguage();postMonitorHeight()}
  }catch{state.connected=false;renderHeader()}finally{state.inFlight=false}
}
for(const id of ['episode','routeFilter','statusFilter','search'])$(id).addEventListener(id==='search'?'input':'change',()=>{renderTopology();renderTimeline();renderDetail();postMonitorHeight()});
$('pause').addEventListener('click',()=>{state.paused=!state.paused;$('pause').classList.toggle('on',state.paused);$('pause').textContent=state.paused?t('resume'):t('pause');if(!state.paused)poll()});
$('auto').addEventListener('click',()=>{state.auto=!state.auto;$('auto').classList.toggle('on',state.auto);$('auto').textContent=state.auto?t('autoOn'):t('autoOff');if(state.auto)$('log').scrollTop=0});
$('activityInspector').addEventListener('toggle',()=>postMonitorHeight());
$('monitorLanguage').addEventListener('change',event=>setMonitorLanguage(event.target.value));
for(const group of document.querySelectorAll('.route[data-route]')){const pick=()=>selectLatest(e=>e.presentation?.route===group.dataset.route);group.addEventListener('click',pick);group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pick()}})}
for(const group of document.querySelectorAll('.node[data-node]')){const pick=()=>selectLatest(e=>routeStages(e).some(stage=>stage.node===group.dataset.node));group.addEventListener('click',pick);group.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();pick()}})}
window.addEventListener('message',event=>{
  if(event.origin!==location.origin||event.source!==window.parent)return;
  if(event.data?.type==='ccs-language')setMonitorLanguage(event.data.language);
  if(event.data?.type==='ccs-monitor-measure')postMonitorHeight();
});
window.addEventListener('storage',event=>{if(event.key==='ccs-ui-language'&&['ko','en'].includes(event.newValue))setMonitorLanguage(event.newValue)});
document.documentElement.classList.toggle('embedded',window.self!==window.top);
if(window.self!==window.top)$('monitorLanguage').hidden=true;
applyMonitorLanguage();
if(INITIAL){state.meta=INITIAL.meta||{};addEvents(INITIAL.events);render()}else{poll();setInterval(poll,900)}
if('ResizeObserver'in window)new ResizeObserver(()=>postMonitorHeight()).observe(document.querySelector('main.shell'));
window.addEventListener('load',postMonitorHeight);
"""


_TOPOLOGY = r"""
<svg id="topology" class="topology" viewBox="0 0 1300 650" role="img" aria-label="NetOps multi-agent topology">
<defs>
  <marker id="arrow-request" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8z" fill="#0071e3"/></marker>
  <marker id="arrow-report" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8z" fill="#248a3d"/></marker>
  <marker id="arrow-delegate" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8z" fill="#5856d6"/></marker>
  <marker id="arrow-return" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 8 4 0 8z" fill="#6e5ce6"/></marker>
  <marker id="arrow-rag" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 8 4 0 8z" fill="#af52de"/></marker>
  <marker id="arrow-memory" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 8 4 0 8z" fill="#00897b"/></marker>
  <marker id="arrow-opmcp" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 8 4 0 8z" fill="#c77800"/></marker>
  <marker id="arrow-diagmcp" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto-start-reverse"><path d="M0 0 8 4 0 8z" fill="#008db3"/></marker>
</defs>
<g class="route" data-route="request" tabindex="0" role="button" style="--route:#0071e3"><path class="route-hit" d="M285 315H430"/><path class="route-line" d="M285 315H430" marker-end="url(#arrow-request)"/><text x="358" y="300" data-i18n="routeRequest">Request</text></g>
<g class="route" data-route="report" tabindex="0" role="button" style="--route:#248a3d"><path class="route-hit" d="M430 405H285"/><path class="route-line" d="M430 405H285" marker-end="url(#arrow-report)"/><text x="358" y="428" data-i18n="routeReport">Report</text></g>
<g class="route" data-route="delegate" tabindex="0" role="button" style="--route:#5856d6"><path class="route-hit" d="M730 315H930"/><path class="route-line" d="M730 315H930" marker-end="url(#arrow-delegate)"/><text x="830" y="300" data-i18n="routeDelegate">Delegate</text></g>
<g class="route" data-route="return" tabindex="0" role="button" style="--route:#6e5ce6"><path class="route-hit" d="M930 405H730"/><path class="route-line" d="M930 405H730" marker-end="url(#arrow-return)"/><text x="830" y="428" data-i18n="routeReturn">Return</text></g>
<g class="route" data-route="rag" tabindex="0" role="button" style="--route:#af52de"><path class="route-hit" d="M515 235C500 200 485 188 470 180"/><path class="route-line" d="M515 235C500 200 485 188 470 180" marker-start="url(#arrow-rag)" marker-end="url(#arrow-rag)"/><text x="520" y="202" data-i18n="routeRag">Retrieval</text></g>
<g class="route" data-route="memory" tabindex="0" role="button" style="--route:#00897b"><path class="route-hit" d="M645 235C665 202 710 190 770 180"/><path class="route-line" d="M645 235C665 202 710 190 770 180" marker-start="url(#arrow-memory)" marker-end="url(#arrow-memory)"/><text x="675" y="196" data-i18n="routeMemory">Read / Write</text></g>
<g class="route" data-route="op_mcp" tabindex="0" role="button" style="--route:#c77800"><path class="route-hit" d="M650 475C700 535 805 550 900 555"/><path class="route-line" d="M650 475C700 535 805 550 900 555" marker-start="url(#arrow-opmcp)" marker-end="url(#arrow-opmcp)"/><text x="750" y="532" data-i18n="routeOpMcp">MCP · change</text></g>
<g class="route" data-route="diag_mcp" tabindex="0" role="button" style="--route:#008db3"><path class="route-hit" d="M1050 450C1055 475 1050 495 1045 515"/><path class="route-line" d="M1050 450C1055 475 1050 495 1045 515" marker-start="url(#arrow-diagmcp)" marker-end="url(#arrow-diagmcp)"/><text x="1135" y="490" data-i18n="routeDiagMcp">MCP · read-only</text></g>
<g class="node" data-node="human" tabindex="0" role="button"><rect class="node-surface" x="55" y="260" width="230" height="190" rx="24"/><g transform="translate(78 284)"><circle class="icon-stroke" cx="17" cy="12" r="8"/><path class="icon-stroke" d="M4 36c2-10 24-10 26 0"/></g><text class="node-title" x="126" y="311" data-i18n="human">Human Operator</text><text class="node-caption" x="78" y="338" data-i18n="humanCaption">Intent &amp; oversight</text>
  <g class="sub-chip" data-node="human" data-submodule="request"><rect x="78" y="360" width="82" height="30" rx="15"/><text x="119" y="379" data-i18n="request">Request</text></g><g class="sub-chip" data-node="human" data-submodule="report"><rect x="168" y="360" width="82" height="30" rx="15"/><text x="209" y="379" data-i18n="report">Report</text></g></g>
<g class="node" data-node="operation" tabindex="0" role="button"><rect class="node-surface" x="430" y="235" width="300" height="240" rx="26"/><g transform="translate(454 260)"><circle class="icon-stroke" cx="17" cy="17" r="11"/><path class="icon-stroke" d="M17 0v6m0 22v6M0 17h6m22 0h6M5 5l5 5m14 14 5 5M29 5l-5 5M10 24l-5 5"/><circle class="icon-stroke" cx="17" cy="17" r="4"/></g><text class="node-title" x="504" y="288" data-i18n="operation">Operation Agent</text><text class="node-caption" x="454" y="318" data-i18n="operationCaption">Workflow · change owner</text>
  <g class="sub-chip" data-node="operation" data-submodule="context"><rect x="454" y="342" width="112" height="32" rx="16"/><text x="510" y="362" data-i18n="context">Context</text></g><g class="sub-chip" data-node="operation" data-submodule="action"><rect x="574" y="342" width="92" height="32" rx="16"/><text x="620" y="362" data-i18n="action">Action</text></g><g class="sub-chip" data-node="operation" data-submodule="approval"><rect x="454" y="383" width="112" height="32" rx="16"/><text x="510" y="403" data-i18n="approval">Approval</text></g><g class="sub-chip" data-node="operation" data-submodule="report"><rect x="574" y="383" width="92" height="32" rx="16"/><text x="620" y="403" data-i18n="report">Report</text></g></g>
<g class="node" data-node="diagnosis" tabindex="0" role="button"><rect class="node-surface" x="930" y="260" width="270" height="190" rx="24"/><g transform="translate(954 284)"><circle class="icon-stroke" cx="14" cy="14" r="11"/><path class="icon-stroke" d="M22 22l10 10M10 14h8M14 10v8"/></g><text class="node-title" x="1003" y="311" data-i18n="diagnosis">Diagnosis Agent</text><text class="node-caption" x="954" y="338" data-i18n="diagnosisCaption">Evidence · read-only tools</text>
  <g class="sub-chip" data-node="diagnosis" data-submodule="inspect"><rect x="954" y="360" width="70" height="30" rx="15"/><text x="989" y="379" data-i18n="inspect">Inspect</text></g><g class="sub-chip" data-node="diagnosis" data-submodule="evidence"><rect x="1030" y="360" width="74" height="30" rx="15"/><text x="1067" y="379" data-i18n="evidence">Evidence</text></g><g class="sub-chip" data-node="diagnosis" data-submodule="conclusion"><rect x="1110" y="360" width="70" height="30" rx="15"/><text x="1145" y="379" data-i18n="conclusion">Conclusion</text></g></g>
<g class="node" data-node="runbook" tabindex="0" role="button"><rect class="node-surface" x="300" y="35" width="260" height="145" rx="22"/><g transform="translate(324 60)"><path class="icon-stroke" d="M2 2h14c5 0 8 3 8 8v24c0-5-3-8-8-8H2zM46 2H32c-5 0-8 3-8 8v24c0-5 3-8 8-8h14z"/></g><text class="node-title" x="382" y="84" data-i18n="runbook">Runbooks Search</text><text class="node-caption" x="324" y="110" data-i18n="runbookCaption">BM25 retrieval</text><g class="sub-chip" data-node="runbook" data-submodule="search"><rect x="324" y="126" width="92" height="30" rx="15"/><text x="370" y="145" data-i18n="search">Search</text></g><g class="sub-chip" data-node="runbook" data-submodule="result"><rect x="424" y="126" width="92" height="30" rx="15"/><text x="470" y="145" data-i18n="result">Result</text></g></g>
<g class="node" data-node="memory" tabindex="0" role="button"><rect class="node-surface" x="690" y="35" width="260" height="145" rx="22"/><g transform="translate(714 57)"><ellipse class="icon-stroke" cx="20" cy="8" rx="18" ry="6"/><path class="icon-stroke" d="M2 8v22c0 4 36 4 36 0V8M2 19c0 4 36 4 36 0"/></g><text class="node-title" x="768" y="84" data-i18n="memory">Incident Memory</text><text class="node-caption" x="714" y="110" data-i18n="memoryCaption">Approved incident records</text><g class="sub-chip" data-node="memory" data-submodule="read"><rect x="714" y="126" width="64" height="30" rx="15"/><text x="746" y="145" data-i18n="read">Read</text></g><g class="sub-chip" data-node="memory" data-submodule="draft"><rect x="784" y="126" width="64" height="30" rx="15"/><text x="816" y="145" data-i18n="draft">Draft</text></g><g class="sub-chip" data-node="memory" data-submodule="write"><rect x="854" y="126" width="64" height="30" rx="15"/><text x="886" y="145" data-i18n="write">Write</text></g></g>
<g class="node" data-node="tools" tabindex="0" role="button"><rect class="node-surface" x="900" y="515" width="310" height="115" rx="22"/><g transform="translate(924 538)"><path class="icon-stroke" d="M25 4a10 10 0 0 0-13 13L2 27l7 7 10-10A10 10 0 0 0 32 11l-7 7-7-7z"/></g><text class="node-title" x="975" y="563" data-i18n="tools">Network Tools</text><text class="node-caption" x="924" y="586" data-i18n="toolsCaption">MCP · role-bound access</text><g class="sub-chip" data-node="tools" data-submodule="read"><rect x="924" y="594" width="48" height="25" rx="12"/><text x="948" y="611" data-i18n="read">Read</text></g><g class="sub-chip" data-node="tools" data-submodule="preview"><rect x="978" y="594" width="52" height="25" rx="12"/><text x="1004" y="611" data-i18n="preview">Preview</text></g><g class="sub-chip" data-node="tools" data-submodule="apply"><rect x="1036" y="594" width="48" height="25" rx="12"/><text x="1060" y="611" data-i18n="apply">Apply</text></g><g class="sub-chip" data-node="tools" data-submodule="verify"><rect x="1090" y="594" width="48" height="25" rx="12"/><text x="1114" y="611" data-i18n="verify">Verify</text></g><g class="sub-chip" data-node="tools" data-submodule="rollback"><rect x="1144" y="594" width="52" height="25" rx="12"/><text x="1170" y="611" data-i18n="rollback">Rollback</text></g></g>
</svg>
"""


def _document(snapshot_payload: dict[str, Any] | None = None) -> str:
    from ccs.monitor_i18n import SCRIPT as language_script

    embedded = "null"
    if snapshot_payload is not None:
        embedded = json.dumps(snapshot_payload, ensure_ascii=False, separators=(",", ":"))
        embedded = embedded.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
        embedded = embedded.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    route_options = "".join(
        f'<option value="{route}" data-i18n="{key}">{route}</option>'
        for route, key in (
            ("request", "routeRequest"), ("rag", "routeRag"), ("memory", "routeMemory"),
            ("delegate", "routeDelegate"), ("return", "routeReturn"), ("op_mcp", "routeOpMcp"),
            ("diag_mcp", "routeDiagMcp"), ("report", "routeReport"), ("internal", "routeInternal"),
        )
    )
    status_options = "".join(
        f'<option value="{status}" data-i18n="{status}">{status}</option>'
        for status in ("started", "succeeded", "failed", "waiting", "skipped", "info")
    )
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><link rel="icon" href="data:,"><title>CCS NetOps Agent Activity Monitor</title><style>{_STUDIO_STYLE}</style></head>
<body><main class="shell">
<header class="top"><div><div class="eyebrow" data-i18n="eyebrow">CCS · D0 observability</div><h1 class="title" data-i18n="title">NetOps Agent Activity Monitor</h1><p class="subtitle" data-i18n="subtitle">Follow requests, diagnosis, action, and verification through recorded events.</p></div><div class="header-actions"><select id="monitorLanguage" class="language" aria-label="Language"><option value="ko">한국어</option><option value="en">English</option></select><div id="liveChip" class="live-chip"><span class="dot"></span><span>Checking status</span></div></div></header>
<div id="oldWarning" class="warning" hidden></div>
<section class="summary"><div class="metric"><span data-i18n="runId">Run ID</span><strong id="runId">—</strong></div><div class="metric"><span data-i18n="mode">Mode</span><strong id="mode">—</strong></div><div class="metric"><span data-i18n="runStatus">Run status</span><strong id="runStatus">—</strong></div><div class="metric"><span data-i18n="episodes">Episodes</span><strong id="episodesMetric">—</strong></div><div class="metric"><span data-i18n="successful">Successful</span><strong id="successMetric">—</strong></div><div class="metric"><span data-i18n="apiCalls">API calls</span><strong id="callsMetric">—</strong></div></section>
<section class="workflow-board">
<section class="panel topology-panel"><div class="section-head"><h2 data-i18n="diagramTitle">Live agent topology</h2><p data-i18n="diagramHint">Bright routes are executing now; the selected record highlights its matching route.</p></div>{_TOPOLOGY}<div class="topology-legend"><div class="legend-routes"><span><i style="--swatch:#0071e3"></i>Request</span><span><i style="--swatch:#5856d6"></i>A2A</span><span><i style="--swatch:#af52de"></i>RAG</span><span><i style="--swatch:#00897b"></i>Memory</span><span><i style="--swatch:#c77800"></i>MCP</span></div><span data-i18n="orderNote">Newest records appear first.</span></div></section>
<aside class="panel timeline-panel"><div class="panel-head"><div class="timeline-heading"><h2 data-i18n="timeline">Activity timeline</h2><span class="order-badge" data-i18n="newestFirst">Newest first</span></div><span id="visibleCount" class="count">0 / 0</span></div><div class="filters timeline-controls"><input id="search" type="search" placeholder="Search actions, tools, targets, and details"><select id="episode"><option value="" data-i18n="allEpisodes">All episodes</option></select><select id="routeFilter"><option value="" data-i18n="allChannels">All routes</option>{route_options}</select><select id="statusFilter"><option value="" data-i18n="allStatuses">All statuses</option>{status_options}</select><div class="timeline-actions"><button id="pause">Pause updates</button><button id="auto" class="on">Follow latest</button></div></div><div id="log" class="log"></div></aside>
</section>
<details id="activityInspector" class="panel detail-panel"><summary><h2 data-i18n="selectedActivity">Selected activity</h2><span id="detailPreview" class="detail-preview"></span><span class="detail-chevron" aria-hidden="true">›</span></summary><div id="detail" class="detail"><div class="empty" data-i18n="selectActivity">Select an activity.</div></div></details>
</main><script>window.__CCS_SNAPSHOT__={embedded};{language_script}\n{_STUDIO_SCRIPT}</script></body></html>"""


def write_snapshot(run_dir: str | Path) -> Path:
    """Write a standalone, offline ``monitor.html`` beside the run artifacts."""
    root = Path(run_dir).resolve()
    if not root.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {root}")
    payload = {"events": read_activity(root), "meta": _metadata(root), "snapshot_at_utc": datetime.now(timezone.utc).isoformat()}
    destination = root / "monitor.html"
    writing = root / "monitor.html.writing"
    writing.write_text(_document(payload), encoding="utf-8")
    writing.replace(destination)
    return destination


class _MonitorHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class DashboardServer:
    """Serve the activity monitor on loopback with an unguessable URL token."""

    def __init__(self, run_dir: str | Path, port: int = 0):
        self.run_dir = Path(run_dir).resolve()
        if not self.run_dir.is_dir():
            raise FileNotFoundError(f"Run directory does not exist: {self.run_dir}")
        if not isinstance(port, int) or isinstance(port, bool) or not 0 <= port <= 65535:
            raise ValueError("port must be an integer from 0 to 65535")
        self.port = port
        self._token = secrets.token_urlsafe(32)
        self._server: _MonitorHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.url: str | None = None

    def start(self) -> "DashboardServer":
        if self._server is not None:
            return self
        handler = partial(_DashboardHandler, dashboard=self)
        server = _MonitorHTTPServer(("127.0.0.1", self.port), handler)
        self._server = server
        actual_port = int(server.server_address[1])
        self.url = f"http://127.0.0.1:{actual_port}/?token={quote(self._token)}"
        self._thread = threading.Thread(target=server.serve_forever, name="ccs-dashboard", daemon=True)
        self._thread.start()
        return self

    def stop(self) -> None:
        server, thread = self._server, self._thread
        self._server = None
        self._thread = None
        if server is not None:
            server.shutdown()
            server.server_close()
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=3)

    def __enter__(self) -> "DashboardServer":
        return self.start()

    def __exit__(self, *_: object) -> None:
        self.stop()


class _DashboardHandler(BaseHTTPRequestHandler):
    server_version = "CCSMonitor/1"

    def __init__(self, *args: Any, dashboard: DashboardServer, **kwargs: Any):
        self.dashboard = dashboard
        super().__init__(*args, **kwargs)

    def log_message(self, _format: str, *args: Any) -> None:
        return

    def _headers(self, content_type: str, length: int) -> None:
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'none'; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'self'; img-src data:; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
        )

    def _send(self, status: HTTPStatus, body: bytes, content_type: str = "text/plain; charset=utf-8") -> None:
        self.send_response(status)
        self._headers(content_type, len(body))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlsplit(self.path)
        query = parse_qs(parsed.query, keep_blank_values=True)
        token = query.get("token", [""])[0]
        if not hmac.compare_digest(token, self.dashboard._token):
            self._send(HTTPStatus.FORBIDDEN, b"Forbidden")
            return
        if parsed.path == "/":
            self._send(HTTPStatus.OK, _document().encode("utf-8"), "text/html; charset=utf-8")
            return
        if parsed.path == "/api/state":
            offsets = _decode_cursor(query.get("cursor", [""])[0])
            events, next_offsets = _read_incremental(self.dashboard.run_dir, offsets)
            payload = {"events": events, "cursor": _encode_cursor(next_offsets), "meta": _metadata(self.dashboard.run_dir)}
            self._send(
                HTTPStatus.OK,
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"),
                "application/json; charset=utf-8",
            )
            return
        self._send(HTTPStatus.NOT_FOUND, b"Not found")
