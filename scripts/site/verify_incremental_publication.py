"""Exercise incremental copies and preservation of remote edits with local fixtures.

Git is mocked: this verification does not access credentials, commit, or publish.
"""
from pathlib import Path
import hashlib, importlib.util, json, subprocess, uuid

ROOT=Path(__file__).resolve().parents[2]
work=ROOT/'scripts/.build-livrables'/('incremental-fixture-'+uuid.uuid4().hex)
work.mkdir(parents=True)
assert work.resolve().is_relative_to((ROOT/'scripts/.build-livrables').resolve())

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

builder=load('incremental_builder',ROOT/'scripts/build_remote_site.py')
builder.ROOT=work/'builder';builder.ROOT.mkdir()
builder.OUT=builder.ROOT/'dist-site'
source=builder.ROOT/'source.txt';source.write_bytes(b'Original\r\n')
builder.files={'document.txt':source};builder.hashes={'document.txt':sha(source)}
builder.generated={'index.html':b'<p>Lecture</p>'}
first={};builder.write_site(first)
target=builder.OUT/'document.txt';original_time=target.stat().st_mtime_ns
second={};builder.write_site(second)
assert second['incremental']['copied_source_files']==0 and second['incremental']['written_generated_files']==0
assert target.stat().st_mtime_ns==original_time
target.write_bytes(b'Changed generated copy')
repair={};builder.write_site(repair)
assert repair['incremental']['copied_source_files']==1 and target.read_bytes()==source.read_bytes()
source.write_bytes(b'Changed source\r\n');builder.hashes={'document.txt':sha(source)}
changed={};builder.write_site(changed)
assert changed['incremental']['copied_source_files']==1 and changed['incremental']['unchanged_files']==1
checks=['Unchanged build outputs keep their timestamps and bytes',
        'A tampered managed output is repaired from the source',
        'Only changed source bytes are recopied']

publisher=load('incremental_publisher',ROOT/'scripts/site/publish_remote_site.py')
publisher.ROOT=work/'publisher';publisher.ROOT.mkdir()
publisher.REPO=publisher.ROOT/'.publish-repo';publisher.REPO.mkdir()
publisher.SOURCE=publisher.ROOT/'dist-site';publisher.SOURCE.mkdir()
publisher.DOCS=publisher.REPO/'docs';publisher.DOCS.mkdir()
for name,value in [('stable.eml',b'From: test@example.org\r\n\r\nOriginal\r\n'),('updated.txt',b'old')]:
    (publisher.DOCS/name).write_bytes(value)
old_hashes={p.name:sha(p) for p in publisher.DOCS.iterdir()}
old={'output_files':list(old_hashes),'output_hashes':old_hashes}
(publisher.DOCS/'.site-build.json').write_text(json.dumps(old),encoding='utf-8')
stable_time=(publisher.DOCS/'stable.eml').stat().st_mtime_ns
(publisher.SOURCE/'stable.eml').write_bytes((publisher.DOCS/'stable.eml').read_bytes())
(publisher.SOURCE/'updated.txt').write_bytes(b'new')
new_hashes={p.name:sha(p) for p in publisher.SOURCE.iterdir()}
new={'mode':'build','output_files':list(new_hashes),'output_hashes':new_hashes}
(publisher.SOURCE/'.site-build.json').write_text(json.dumps(new),encoding='utf-8')
git_calls=[]
def fake_git(*args,allowed=(0,)):
    git_calls.append(args);out=b''
    if args[:2]==('remote','get-url'):out=b'https://github.com/takatakca/assurance-6241.git'
    elif args[:2]==('symbolic-ref','--short'):out=b'main'
    elif args[0]=='rev-parse':out=b'fixture-commit'
    elif args[0]=='ls-remote':out=b'fixture-commit\trefs/heads/main'
    return subprocess.CompletedProcess(args,0,out,b'')
publisher.git=fake_git
publisher.main()
assert (publisher.DOCS/'stable.eml').stat().st_mtime_ns==stable_time
assert (publisher.DOCS/'stable.eml').read_bytes()==(publisher.SOURCE/'stable.eml').read_bytes()
assert (publisher.DOCS/'updated.txt').read_bytes()==b'new'
result=json.loads((publisher.ROOT/'scripts/.build-livrables/publication-result.json').read_text())
assert result['incremental']['copied_files']==2 and result['incremental']['unchanged_files']==1
checks.append('Publication skips unchanged original EML bytes and only copies the changed file and manifest')
for mode in ['edit','delete']:
    doc=publisher.DOCS/'updated.txt'
    if mode=='edit':doc.write_bytes(b'Remote collaborator edit')
    else:doc.unlink()
    git_calls.clear()
    try:publisher.main();raise AssertionError('Expected remote change rejection')
    except RuntimeError as exc:assert 'edited since the last build' in str(exc),str(exc)
    assert not any(call[0] in {'add','commit','push'} for call in git_calls)
checks.append('Remote edits and deletions are rejected before staging or publishing')
long_doc=publisher.DOCS/('directory-'+'x'*80)/('document-'+'y'*80+'.txt')
Path(publisher.native(long_doc.parent)).mkdir(parents=True)
Path(publisher.native(long_doc)).write_bytes(b'Long path original\r\n')
assert len(str(long_doc))>260
assert long_doc.relative_to(publisher.DOCS).as_posix() in publisher.file_tree(publisher.DOCS)
assert publisher.sha(long_doc)==hashlib.sha256(b'Long path original\r\n').hexdigest()
checks.append('Files beyond the Windows 260-character boundary remain visible and hashable')
receipt={'passed':len(checks),'scope':'Synthetic filesystem fixtures; Git mocked; no network publication','checks':checks}
(ROOT/'scripts/.build-livrables/incremental-publication-validation.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt,indent=2))
