"""Read/configure only the authorized repository's GitHub Pages endpoint.

Credentials come from the official Git helper, remain in memory, and are never
printed or written to disk. No sign-in or permission expansion is attempted.
"""
from pathlib import Path
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError, URLError
import argparse, json, os, subprocess

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'.publish-repo'
ENDPOINT='https://api.github.com/repos/takatakca/assurance-6241/pages'
class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):return None

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--configure',action='store_true');args=parser.parse_args()
    env=os.environ.copy();env.update({'GCM_INTERACTIVE':'never','GIT_TERMINAL_PROMPT':'0'})
    result=subprocess.run(['git','-C',str(REPO),'credential','fill'],
        input='protocol=https\nhost=github.com\nusername=takatakca\n\n',capture_output=True,text=True,env=env,timeout=45)
    if result.returncode:
        print(json.dumps({'ok':False,'stage':'credential_helper','exit_code':result.returncode}));return 1
    credentials=dict(line.split('=',1) for line in result.stdout.splitlines() if '=' in line)
    secret=credentials.get('password')
    if not secret:
        print(json.dumps({'ok':False,'stage':'credential_helper','reason':'No credential returned'}));return 1
    opener=build_opener(NoRedirect)
    def request(method,payload=None):
        data=json.dumps(payload).encode() if payload is not None else None
        req=Request(ENDPOINT,data=data,method=method,headers={
            'Authorization':'Bearer '+secret,'Accept':'application/vnd.github+json',
            'X-GitHub-Api-Version':'2022-11-28','User-Agent':'assurance-6241-publisher',
            'Content-Type':'application/json'})
        try:
            with opener.open(req,timeout=45) as response:
                body=response.read();return response.status,json.loads(body) if body else {}
        except HTTPError as exc:return exc.code,{}
        except URLError:return 0,{}
    status,body=request('GET');actions=[{'method':'GET','status':status}]
    if args.configure:
        payload={'build_type':'legacy','source':{'branch':'main','path':'/docs'}}
        if status==404:
            status,body=request('POST',payload);actions.append({'method':'POST','status':status})
        elif status==200 and (body.get('source')!={'branch':'main','path':'/docs'} or body.get('build_type','legacy')!='legacy'):
            status,body=request('PUT',payload);actions.append({'method':'PUT','status':status})
        if status in (200,201,204):
            status,body=request('GET');actions.append({'method':'GET','status':status})
    output={'ok':status==200,'actions':actions,'pages':{k:body.get(k) for k in ['html_url','status','source','build_type','public','https_enforced'] if k in body}}
    print(json.dumps(output,ensure_ascii=False))
    return 0 if status==200 else 1

if __name__=='__main__':
    try:raise SystemExit(main())
    except (subprocess.SubprocessError,OSError,ValueError) as exc:
        print(json.dumps({'ok':False,'error_type':type(exc).__name__,'detail':'Operation failed; no credential output retained'}));raise SystemExit(1)
