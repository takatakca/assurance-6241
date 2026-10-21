"""Audit generated pages in memory and test the renderer without a browser."""
from pathlib import Path
import base64, hashlib, importlib.util, json, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('remote_site',ROOT/'scripts/build_remote_site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
site.collect();site.build_generated();report=site.audit()
assert not report['broken_generated_links']
checks=['Generated internal links all resolve in the selected publication tree']
for rel,data in site.generated.items():
    if not rel.endswith('.html'):continue
    text=data.decode('utf-8')
    assert site.RULE in text,rel
    assert 'Content-Security-Policy' in text,rel
    assert 'connect-src &#x27;none&#x27;' in text,rel
    for script in re.findall(r'<script>([\s\S]*?)</script>',text):
        token=base64.b64encode(hashlib.sha256(script.encode()).digest()).decode()
        assert 'sha256-'+token in text,rel
checks+=['All rendered pages include the exact common rule','CSP permits exact generated script hashes and blocks network fetches']
source=next(iter(site.routes))+'.html'
result=site.inline('<script>alert(1)</script> [bad](javascript:alert(1)) [bad](data:text/html,test)',source)
assert '<script>' not in result
assert 'href="javascript:' not in result and 'href="data:' not in result
assert '&lt;script&gt;' in result
checks.append('Markdown raw HTML and active URL schemes are not executed')
reader=site.ArchiveReader(source)
reader.feed('<script>alert(1)</script><p onclick="evil()">Bonjour</p><iframe src="https://evil.test">x</iframe>')
sanitized=''.join(reader.out)
assert sanitized=='<p>Bonjour</p>',sanitized
checks.append('Archived HTML loses scripts, event handlers and frames while retaining text')
code=site.markdown('# Exemple\n\n| Un | Deux |\n|---|---|\n| **Texte** | `code` |\n\n- Entrée\n\n```\n<script>x</script>\n```',source)
assert all(v in code for v in ['<h1','<table>','<strong>Texte</strong>','<code>code</code>','<ul>','&lt;script&gt;x&lt;/script&gt;'])
checks.append('Headings, tables, lists, emphasis and literal code remain readable')
assert site.resolve_link('javascript:alert(1)',source) is None
assert site.resolve_link('file:///C:/secret',source) is None
assert site.resolve_link('https://example.org/source',source)=='https://example.org/source'
checks.append('External citations remain hyperlinks; local machine and active schemes are blocked')
work=ROOT/'scripts/.build-livrables/remote-site-tests';work.mkdir(parents=True,exist_ok=True)
node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
if not node.is_file():node='node'
count=0
for rel,data in site.generated.items():
    scripts=re.findall(r'<script>([\s\S]*?)</script>',data.decode('utf-8')) if rel.endswith('.html') else []
    if rel=='assets/site-viewer.js':scripts=[data.decode('utf-8')]
    for script in scripts:
        dest=work/f'script-{count}.js';dest.write_text(script,encoding='utf-8');count+=1
        result=subprocess.run([str(node),'--check',str(dest)],capture_output=True,text=True)
        assert result.returncode==0,result.stderr[-1500:]
checks.append(f'JavaScript syntax validated by Node for {count} generated scripts')
receipt={'checks':checks,'passed':len(checks),'mode':'in-memory generation + filesystem + Node syntax; no publication',
    'published_files':report['published_files'],'megabytes_decimal':report['megabytes_decimal'],
    'static_links_checked':report['static_links_checked'],'markdown_readers':report['markdown_readers']}
(ROOT/'scripts/.build-livrables/remote-site-validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
