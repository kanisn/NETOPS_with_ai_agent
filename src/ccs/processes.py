"""Bounded local service startup and reliable cleanup on Windows and POSIX."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from ccs.paths import working_root

def choose_port(host,configured):
    if configured:return configured
    with socket.socket() as sock:
        sock.bind((host,0));return sock.getsockname()[1]

class Services:
    def __init__(self,system,run_dir,episode_dir,contexts,tokens):
        self.system=system;self.run_dir=run_dir;self.episode_dir=episode_dir
        self.contexts=contexts;self.tokens=tokens;self.children=[];self.files=[]

    async def __aenter__(self):
        try:
            for kind,context in self.contexts.items():
                config_path=self.episode_dir/f'{kind}-process.json'
                config_path.write_text(json.dumps(context,indent=2),encoding='utf-8')
                output=(self.episode_dir/f'{kind}-process.log').open('w',encoding='utf-8');self.files.append(output)
                env=os.environ.copy();env.update(self.tokens)
                env['PYTHONDONTWRITEBYTECODE']='1';env['PYTHONPATH']=str(self.system.project_root/'src')
                # Run artifacts may be on OneDrive; child scratch must stay separate.
                scratch_root=working_root()
                working_dir=scratch_root/self.run_dir.name
                working_dir.mkdir(parents=True,exist_ok=True)
                work=str(working_dir.resolve())
                env['TEMP']=work;env['TMP']=work;env['TMPDIR']=work
                child=subprocess.Popen([sys.executable,'-m','ccs.services',kind,'--context',str(config_path)],
                    cwd=self.episode_dir,env=env,stdout=output,stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0)
                self.children.append(child)
                deadline=time.monotonic()+self.system.startup_timeout
                while time.monotonic()<deadline:
                    if child.poll() is not None:raise RuntimeError(f'{kind} process exited during startup; inspect its process log')
                    try:
                        with socket.create_connection((context['host'],context['port']),timeout=.2):break
                    except OSError:await asyncio.sleep(.15)
                else:raise RuntimeError(f'{kind} process startup timed out')
            return self
        except BaseException:
            await self.__aexit__(None,None,None);raise

    async def __aexit__(self,*_):
        for child in reversed(self.children):
            if child.poll() is None:
                child.terminate()
                try:await asyncio.to_thread(child.wait,5)
                except subprocess.TimeoutExpired:
                    child.kill();await asyncio.to_thread(child.wait,5)
        for handle in self.files:handle.close()
