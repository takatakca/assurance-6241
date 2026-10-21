"""Publish the prepared static tree to docs/ in the authorized existing clone.

Uses normal Git/GCM authentication with interaction disabled; no force push,
no credential inspection, edits limited to docs/ and its .gitattributes rule,
and no source deletion.
"""
from pathlib import Path, PurePosixPath
import hashlib, json, os, shutil, subprocess

ROOT=Path(__file__).resolve().parents[2]
REPO=ROOT/'.publish-repo';SOURCE=ROOT/'dist-site';DOCS=REPO/'docs'
ALLOWED_REMOTES={'https://github.com/takatakca/assurance-6241','https://github.com/takatakca/assurance-6241.git'}
ENV=os.environ.copy();ENV.update({'GCM_INTERACTIVE':'never','GIT_TERMINAL_PROMPT':'0'})
def git(*args,allowed=(0,)):
    result=subprocess.run(['git','-C',str(REPO),*args],capture_output=True,env=ENV)
    if result.returncode not in allowed:
        # Never relay helper or transport output that could contain credentials.
        raise RuntimeError('Git operation failed: '+args[0]+'; exit='+str(result.returncode))
    return result
def text(*args):return git(*args).stdout.decode('utf-8').strip()
def sha(path):return hashlib.sha256(Path(native(path)).read_bytes()).hexdigest()
def native(path):
    value=str(path.resolve())
    return '\\\\?\\'+value if os.name=='nt' and not value.startswith('\\\\?\\') else value

def file_tree(base):
    tree=Path(native(base))
    return {p.relative_to(tree).as_posix() for p in tree.rglob('*') if p.is_file()}
def main():
    if REPO.is_symlink() or REPO.resolve()!=ROOT.resolve()/'.publish-repo':raise RuntimeError('Unexpected clone location')
    if DOCS.is_symlink() or not DOCS.resolve().is_relative_to(REPO.resolve()):raise RuntimeError('Unexpected docs location')
    if text('remote','get-url','origin') not in ALLOWED_REMOTES:raise RuntimeError('Unexpected Git remote')
    if text('symbolic-ref','--short','HEAD')!='main':raise RuntimeError('Expected main branch')
    marker=SOURCE/'.site-build.json'
    if not marker.is_file():raise RuntimeError('Build manifest absent')
    manifest=json.loads(marker.read_text(encoding='utf-8'))
    if manifest.get('mode')!='build' or manifest.get('source_changes_during_build'):
        raise RuntimeError('Build is incomplete or its sources changed during generation')
    expected=set(manifest['output_files'])|{'.site-build.json'}
    actual=file_tree(SOURCE)
    if actual!=expected:raise RuntimeError('Unexpected files or missing files in build output')
    for rel,value in manifest['output_hashes'].items():
        if sha(SOURCE/rel)!=value:raise RuntimeError('Build file changed after validation: '+rel)
    if any((SOURCE/r).stat().st_size>=100_000_000 for r in expected):raise RuntimeError('Individual file exceeds regular GitHub file limit')
    partial_copy=False
    if git('status','--porcelain').stdout:
        # Resume an interrupted first copy only if Git has no tracked docs and
        # every untracked file is an exact member of this validated snapshot.
        tracked=git('ls-tree','-r','--name-only','HEAD','--','docs').stdout
        modified=git('diff','--name-only','HEAD').stdout
        untracked=git('ls-files','--others','--exclude-standard','-z').stdout.decode('utf-8').split('\0')
        if tracked or modified or any(p and not p.startswith('docs/') for p in untracked):
            raise RuntimeError('Clone has unrelated changes; preserve them before publishing')
        for p in filter(None,untracked):
            rel=p[len('docs/'):]
            if rel not in expected or sha(REPO/p)!=sha(SOURCE/rel):
                raise RuntimeError('Partial copy differs from the validated snapshot: '+p)
        partial_copy=True
    print('Validated static output; synchronizing the existing main branch.',flush=True)
    git('pull','--ff-only','origin','main')
    git('config','core.longpaths','true')
    git('config','core.autocrlf','false')
    existing_hashes={}
    if DOCS.exists():
        existing=file_tree(DOCS)
        old=DOCS/'.site-build.json'
        if existing and not old.is_file():raise RuntimeError('Existing docs have no generation manifest; no overwrite performed')
        old_manifest=json.loads(old.read_text(encoding='utf-8')) if old.exists() else {}
        previous=set(old_manifest.get('output_files',[]))|({'.site-build.json'} if old.exists() else set())
        if existing-previous:raise RuntimeError('Existing docs contain unmanaged files')
        existing_hashes={r:sha(DOCS/r) for r in existing}
        changed=[r for r,value in old_manifest.get('output_hashes',{}).items()
                 if (r not in existing_hashes and not partial_copy) or (r in existing_hashes and existing_hashes[r]!=value)]
        if changed:raise RuntimeError('Published documents have been edited since the last build; reconcile before overwriting: '+', '.join(changed[:5]))
        for rel in previous-expected:
            target=DOCS/rel
            if '..' in PurePosixPath(rel).parts or not target.resolve().is_relative_to(DOCS.resolve()):raise RuntimeError('Unexpected prior output path')
            native_target=Path(native(target))
            if native_target.is_file():native_target.unlink()
    DOCS.mkdir(exist_ok=True)
    expected_hashes=dict(manifest['output_hashes']);expected_hashes['.site-build.json']=sha(marker)
    incremental={'copied_files':0,'unchanged_files':0,'copied_bytes':0,'unchanged_bytes':0}
    for rel in sorted(expected):
        target=DOCS/rel
        if existing_hashes.get(rel)==expected_hashes[rel]:
            incremental['unchanged_files']+=1;incremental['unchanged_bytes']+=(SOURCE/rel).stat().st_size;continue
        Path(native(target.parent)).mkdir(parents=True,exist_ok=True)
        try:shutil.copy2(native(SOURCE/rel),native(target))
        except OSError as exc:raise RuntimeError('Copy failed: '+rel+'; '+type(exc).__name__)
        incremental['copied_files']+=1;incremental['copied_bytes']+=(SOURCE/rel).stat().st_size
    for rel,value in expected_hashes.items():
        if sha(DOCS/rel)!=value:raise RuntimeError('Copied publication file differs from the validated snapshot: '+rel)
    print(json.dumps({'incremental_copy':incremental}),flush=True)
    attrs=REPO/'.gitattributes'
    rule='docs/** -text'
    previous=attrs.read_text(encoding='utf-8') if attrs.exists() else ''
    if rule not in previous.splitlines():attrs.write_text(previous.rstrip()+'\n'+rule+'\n',encoding='utf-8')
    git('add','--','docs','.gitattributes')
    staged=git('diff','--cached','--name-only','-z').stdout.decode('utf-8').split('\0')
    if any(p and not p.startswith('docs/') and p!='.gitattributes' for p in staged):raise RuntimeError('Unexpected staged paths outside docs')
    if any(staged):
        name=git('config','user.name',allowed=(0,1)).stdout.decode().strip()
        email=git('config','user.email',allowed=(0,1)).stdout.decode().strip()
        config=[]
        if not name:config+=['-c','user.name=Dossier 6241 automation']
        if not email:config+=['-c','user.email=noreply@github.com']
        git(*config,'commit','-m','Publier les trois dossiers documentaires sur GitHub Pages')
    commit=text('rev-parse','HEAD')
    print('Static dossier committed; pushing main without force.',flush=True)
    git('push','origin','main')
    remote=text('ls-remote','origin','refs/heads/main').split()[0]
    if remote!=commit:raise RuntimeError('Remote main does not match the published commit')
    result={'ok':True,'commit':commit,'commit_url':'https://github.com/takatakca/assurance-6241/commit/'+commit,
        'repository':'https://github.com/takatakca/assurance-6241','docs_files':len(expected),
        'bytes':sum((SOURCE/r).stat().st_size for r in expected),'branch':'main','path':'/docs','incremental':incremental}
    dest=ROOT/'scripts/.build-livrables/publication-result.json';dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (OSError,ValueError,KeyError,RuntimeError,subprocess.SubprocessError) as exc:
        print(json.dumps({'ok':False,'error':str(exc),'credential_output':'not retained'}));raise SystemExit(1)
