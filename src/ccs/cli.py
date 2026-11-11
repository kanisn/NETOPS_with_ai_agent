"""User-facing CLI. Mock is the default; live requests require --mode live."""
import argparse
import asyncio
from decimal import Decimal
import json
from pathlib import Path
import time
import webbrowser
from ccs.config import load_ai,load_system,ConfigurationError
from ccs.budget import BudgetLedger,token_cost
from ccs.paths import web_workspace

ROOT=Path(__file__).resolve().parents[2]

def parser():
    cli=argparse.ArgumentParser(description='Protection-free two-agent synthetic NetOps system')
    cli.add_argument('--system-config',type=Path,default=ROOT/'configs/system.xml')
    cli.add_argument('--ai-config',type=Path,default=ROOT/'configs/ai.local.xml')
    commands=cli.add_subparsers(dest='command',required=True)
    web=commands.add_parser('web',help='Open the web experiment console with run setup and monitoring tabs')
    web.add_argument('--workspace',type=Path,default=web_workspace(),help='Web library/control storage (CCS_WEB_WORKSPACE or local-data/web); run results follow system.xml output_root')
    web.add_argument('--port',type=int,default=0,help='Web port; zero chooses an available port')
    web.add_argument('--host',default='127.0.0.1',help='Specific local IPv4 address; default is loopback')
    web.add_argument('--allow-network',action='append',default=[],help='Allowed client CIDR for LAN mode, /24 or narrower; repeatable')
    web.add_argument('--no-browser',action='store_true',help='Print the URL without opening a browser')
    commands.add_parser('doctor',help='Validate local configuration without making API requests')
    cost=commands.add_parser('costs',help='Compare configured token prices without making API requests')
    cost.add_argument('--input-tokens',type=int,default=100000);cost.add_argument('--output-tokens',type=int,default=10000)
    commands.add_parser('budget',help='Show the cumulative API cost ledger')
    run=commands.add_parser('run',help='Execute incidents through real MCP and A2A services')
    run.add_argument('--mode',choices=['mock','live'],default='mock')
    run.add_argument('--profile',help='Override both Agent profiles for this run')
    run.add_argument('--faults',default='W4',help='Comma-separated W1-W5,N0; all uses system.xml list')
    run.add_argument('--seeds',default='1',help='Comma-separated integer seeds; all uses system.xml list')
    run.add_argument('--repeat',type=int,default=1,help='Repeat each incident in one memory chain')
    run.add_argument('--memory-off',action='store_true')
    run.add_argument('--output-root',type=Path)
    run.add_argument('--request',help='Custom English operator request against the selected synthetic incident')
    run.add_argument('--dashboard',action='store_true',help='Open a live local dashboard and keep it available until Ctrl+C')
    run.add_argument('--no-browser',action='store_true',help='Print the dashboard URL without opening a browser')
    run.add_argument('--progress',choices=['compact','detailed','off'],default='compact',help='Live console activity; detailed also prints safe activity payloads')
    monitor=commands.add_parser('monitor',help='View detailed activity for an existing or running execution')
    monitor.add_argument('run_dir',type=Path)
    monitor.add_argument('--open',action='store_true',help='Open the local dashboard in the default browser')
    monitor.add_argument('--port',type=int,default=0,help='Local port; zero selects an available port')
    report=commands.add_parser('report',help='Verify a sealed run and print its report locations')
    report.add_argument('run_dir',type=Path)
    compare=commands.add_parser('compare',help='Compare completed run usage, cost and success')
    compare.add_argument('run_dirs',type=Path,nargs='+')
    return cli

def main(argv=None):
    args=parser().parse_args(argv)
    try:
        if args.command=='web':
            from ccs.web_console import WebConsoleBindError, WebConsoleServer
            try:
                server=WebConsoleServer(args.system_config,args.ai_config,args.workspace,port=args.port,
                    host=args.host,allowed_networks=tuple(args.allow_network)).start()
            except WebConsoleBindError as exc:
                retry = "Retry with --port 0 or choose another free port." if args.port else "Choose another free port."
                code = exc.winerror if exc.winerror is not None else exc.errno
                detail = f' (socket error {code})' if isinstance(code, int) else ''
                print(f'Web console could not bind to {exc.host}:{exc.port}: {exc.reason}{detail}. {retry}')
                return 1
            try:
                print('Web console: '+server.url,flush=True)
                print('Run setup / Monitoring. Press Ctrl+C to close the console.',flush=True)
                if not args.no_browser:webbrowser.open(server.url)
                while True:time.sleep(.5)
            except KeyboardInterrupt:return 0
            finally:server.stop()
        if args.command=='monitor':
            from ccs.monitor import DashboardServer
            directory=args.run_dir.resolve()
            if not (directory/'manifest.json').is_file():raise ValueError('Run directory must contain manifest.json')
            server=DashboardServer(directory,port=args.port).start()
            try:
                print('Dashboard: '+server.url,flush=True)
                print('Read-only local monitor. Press Ctrl+C to close it.',flush=True)
                if args.open:webbrowser.open(server.url)
                while True:time.sleep(.5)
            except KeyboardInterrupt:return 0
            finally:server.stop()
        if args.command=='report':
            from ccs.reporting import verify_seal
            result=verify_seal(args.run_dir.resolve());print(json.dumps(result,indent=2))
            if result['valid']:print(str(args.run_dir.resolve()/'report.html'))
            return 0 if result['valid'] else 1
        if args.command=='compare':
            from ccs.reporting import compare_runs
            print(json.dumps(compare_runs(args.run_dirs),indent=2));return 0
        ai_path=args.ai_config
        if not ai_path.exists() and args.command in {'doctor','costs','budget'}:ai_path=ROOT/'configs/ai.example.xml'
        ai=load_ai(ai_path);system=load_system(args.system_config)
        if args.command=='doctor':
            import importlib.metadata
            print(json.dumps({'configuration':'valid','condition':'D0','models':{r:ai.profile(r).model for r in ['operation','diagnosis']},
                'key_present':{k:bool(v) for k,v in ai.keys.items()},'runbooks_present':system.runbooks.exists(),
                'packages':{n:importlib.metadata.version(n) for n in ['mcp','a2a-sdk','openai','anthropic']},'live_api_tested':False},indent=2))
        elif args.command=='costs':
            if min(args.input_tokens,args.output_tokens)<0:raise ValueError('Token counts must be nonnegative')
            print(json.dumps([{'profile':p.id,'provider':p.provider,'model':p.model,'input_usd_per_million':str(p.input_rate),'output_usd_per_million':str(p.output_rate),
                'estimated_usd':str(token_cost(p,args.input_tokens,args.output_tokens))} for p in ai.profiles.values()],indent=2))
        elif args.command=='budget':print(json.dumps(BudgetLedger(ai.ledger_path,ai.budget_usd).summary(),indent=2))
        elif args.command=='run':
            from ccs.runner import run
            from ccs.progress import ConsoleProgress
            from ccs.monitor import DashboardServer
            viewers={}
            def created(directory):
                print('Run directory: '+str(directory),flush=True)
                if args.progress!='off':viewers['console']=ConsoleProgress(directory,detailed=args.progress=='detailed').start()
                if args.dashboard:
                    viewers['server']=DashboardServer(directory).start()
                    print('Dashboard: '+viewers['server'].url,flush=True)
                    if not args.no_browser:webbrowser.open(viewers['server'].url)
            try:
                paths,summary=asyncio.run(run(args.system_config,ai_path,mode=args.mode,profile_override=args.profile,
                    faults=None if args.faults=='all' else args.faults.split(','),seeds=None if args.seeds=='all' else [int(s) for s in args.seeds.split(',')],
                    repeat=args.repeat,memory_off=args.memory_off,output_root=args.output_root,request_override=args.request,on_created=created))
                if viewers.get('console'):viewers.pop('console').stop()
                print(json.dumps(summary,indent=2));print('Run directory: '+str(paths))
                print('Activity snapshot: '+str(paths/'monitor.html'))
                if viewers.get('server'):
                    print('Execution finished. Dashboard remains available; press Ctrl+C to close it.',flush=True)
                    try:
                        while True:time.sleep(.5)
                    except KeyboardInterrupt:pass
                return 0 if summary['status']=='COMPLETED' else 1
            finally:
                if viewers.get('console'):viewers['console'].stop()
                if viewers.get('server'):viewers['server'].stop()
        return 0
    except (ConfigurationError,ValueError) as exc:
        print(f'Configuration/input error: {exc}');return 2
    except KeyboardInterrupt:
        print('Interrupted; partial run artifacts have been retained.');return 130
    except Exception as exc:
        print(f'Execution failed ({type(exc).__name__}); inspect the preserved run artifacts.');return 1

if __name__=='__main__':raise SystemExit(main())
