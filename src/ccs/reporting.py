"""Aggregate reports exclude raw incident payloads and registry identifiers."""
from html import escape
import json
from pathlib import Path
import hashlib

def write_reports(run_dir,summary,manifest):
    title='CCS NetOps D0 execution report'
    successful=summary['successful_episodes']
    rows=[f"| {e['episode_id']} | {e['fault']} | {e['seed']} | {e['outcome']} | {e['utility'] if summary['integrity_valid'] else 'INVALID'} | {e['latency_seconds']:.2f} |" for e in manifest['episodes']]
    text=f"# {title}\n\nRun: `{summary['run_id']}`\n\nStatus: **{summary['status']}**; mode: **{summary['mode']}**.\n\n"
    text+=f"Episodes: {summary['episodes']}; successful: {successful}; artifact integrity: {summary['integrity_valid']}.\n\n"
    text+=f"API calls: {summary['api_calls']}; input/output tokens: {summary['input_tokens']}/{summary['output_tokens']}; estimated run cost: US${summary['estimated_cost_usd']}.\n\n"
    text+='| Episode | Fault | Seed | Outcome | Utility | Seconds |\n|---|---|---|---|---|---|\n'+'\n'.join(rows)+'\n\n'
    text+='Limitations:\n\n'+'\n'.join('- '+x for x in summary['limitations'])+'\n'
    (Path(run_dir)/'report.md').write_text(text,encoding='utf-8')
    table=''.join('<tr>'+''.join('<td>'+escape(str(value))+'</td>' for value in [e['episode_id'],e['fault'],e['seed'],e['outcome'],e['utility'] if summary['integrity_valid'] else 'INVALID',f"{e['latency_seconds']:.2f}"])+'</tr>' for e in manifest['episodes'])
    html='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+title+'</title>'
    html+='<style>body{font:16px system-ui;max-width:1100px;margin:3rem auto;padding:0 1rem;background:#f4f7fa;color:#132b3b}article{background:white;padding:2rem;border-radius:12px}h1{font-size:1.8rem}table{border-collapse:collapse;width:100%;margin:2rem 0}td,th{border-bottom:1px solid #dde5eb;padding:.6rem;text-align:left}code{overflow-wrap:anywhere}.metrics{display:flex;gap:2rem;flex-wrap:wrap}.metric{background:#edf4fa;padding:1rem;border-radius:8px}</style><article>'
    html+=f'<h1>{title}</h1><p><code>{escape(summary["run_id"])}</code></p><p>Status: <b>{escape(summary["status"])}</b> · Mode: {escape(summary["mode"])}</p>'
    html+='<div class="metrics">'+''.join(f'<div class="metric">{escape(label)}<br><b>{escape(str(value))}</b></div>' for label,value in [('Successful episodes',f'{successful}/{summary["episodes"]}'),('API calls',summary['api_calls']),('Estimated USD',summary['estimated_cost_usd']),('Integrity',summary['integrity_valid'])])+'</div>'
    html+='<table><thead><tr><th>Episode</th><th>Fault</th><th>Seed</th><th>Outcome</th><th>Utility</th><th>Seconds</th></tr></thead><tbody>'+table+'</tbody></table><h2>Scope and limits</h2><ul>'+''.join('<li>'+escape(x)+'</li>' for x in summary['limitations'])+'</ul></article></html>'
    (Path(run_dir)/'report.html').write_text(html,encoding='utf-8')

def verify_seal(run_dir:Path):
    manifest=json.loads((run_dir/'manifest.json').read_text(encoding='utf-8'))
    errors=[];hashes=manifest.get('artifact_hashes',{})
    if not hashes:errors.append('Run has no sealed artifact hashes')
    for relative,digest in hashes.items():
        path=(run_dir/relative).resolve()
        if not path.is_relative_to(run_dir.resolve()):errors.append('Invalid artifact path');continue
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:errors.append('Artifact mismatch: '+relative)
    from ccs.core.integrity import validate_events
    integrity=validate_events(run_dir)
    errors.extend(integrity.get('errors',[]))
    if manifest.get('manifest_schema')!='netops-run@1':errors.append('Unknown manifest schema')
    return {'valid':not errors,'errors':errors,'event_count':integrity.get('event_count')}

def compare_runs(paths):
    results=[];basis=None;comparable=True
    for path in paths:
        path=Path(path);check=verify_seal(path)
        if not check['valid']:raise ValueError('Cannot compare an invalid run')
        manifest=json.loads((path/'manifest.json').read_text(encoding='utf-8'))
        summary=json.loads((path/'summary.json').read_text(encoding='utf-8'))
        identity=comparison_identity(path,manifest)
        if basis is None:basis=identity
        elif basis!=identity:comparable=False
        results.append({k:summary[k] for k in ['run_id','mode','models','successful_episodes','episodes','api_calls','input_tokens','output_tokens','estimated_cost_usd']})
    return {'same_code_scenarios_backend':comparable,'runs':results,'note':'This flag also requires matching runtime/generation settings and actual scenario artifacts. Provider/model and token prices may differ intentionally. Token-price comparison does not establish equivalent model quality.'}

def comparison_identity(run_dir,manifest):
    """Compare executed scenarios and non-model conditions, not just fault labels."""
    config=json.loads((Path(run_dir)/'effective-config.json').read_text(encoding='utf-8'))
    system={k:v for k,v in config['system'].items() if k not in {'project_root','output_root','runbooks','prompts'}}
    ai=config['ai'];profiles=ai['profiles'];generation={}
    for role in ['operation','diagnosis']:
        selected=config.get('profile_override') or ai['agent_profiles'].get(role) or ai['active_profile']
        profile=profiles[selected]
        generation[role]={k:profile[k] for k in ['reasoning_effort','max_output_tokens']}
    scenarios=[]
    for episode in manifest.get('episodes',[]):
        name=f"episodes/{episode['episode_id']}/scenario.restricted.json"
        digest=manifest.get('artifact_hashes',{}).get(name)
        if digest is None:raise ValueError('Scenario artifacts are not sealed for comparison')
        scenarios.append(digest)
    return {**{key:manifest.get(key) for key in ['source_hashes','seeds','faults','repeat','network_backend']},
        'scenarios':scenarios,'system':system,'generation':generation,
        'input_conditions':config.get('input_conditions'),
        'pacing_conditions':pacing_identity(manifest.get('timing',{})),
        'request_limits':{k:ai[k] for k in ['timeout','schema_retries','max_input_bytes']}}


def pacing_identity(timing):
    """Compare selected delay levels without treating clock timestamps as inputs."""
    levels=[]
    for change in timing.get('delay_change_history',[]):
        if isinstance(change,dict) and 'seconds' in change:
            seconds=change['seconds']
            if not levels or levels[-1]!=seconds:levels.append(seconds)
    return {'initial':timing.get('initial_delay_seconds',0),
        'final':timing.get('final_delay_seconds',0),'delay_levels':levels}
