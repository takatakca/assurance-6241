"""Check real generated readers/anchors and execute hub navigation; no site copy."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import importlib.util,json,posixpath,re,subprocess

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('reader_navigation_actual',ROOT/'scripts/build_remote_site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
site.collect();site.build_generated();audit=site.audit()
assert not audit['broken_generated_links']

class Document(HTMLParser):
    def __init__(self,text):super().__init__();self.ids=set();self.links=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if a.get('id'):self.ids.add(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a)

documents={r:Document(data.decode('utf-8')) for r,data in site.generated.items() if r.endswith('.html')}
anchors=0;broken_anchors=[];raw_reading_links=[]
for rel,doc in documents.items():
    for a in doc.links:
        value=urlsplit(a['href'])
        if value.scheme or value.netloc:continue
        target=posixpath.normpath(posixpath.join(posixpath.dirname(rel),unquote(value.path))) if value.path else rel
        if target in site.routes and 'download' not in a and a.get('data-raw')!='true':raw_reading_links.append({'page':rel,'target':target})
        if value.fragment and target in documents:
            anchors+=1
            if unquote(value.fragment) not in documents[target].ids:broken_anchors.append({'page':rel,'target':target,'fragment':unquote(value.fragment)})
assert not raw_reading_links,raw_reading_links[:5]
assert not broken_anchors,broken_anchors[:5]

node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def execute(code):
    done=subprocess.run([str(node),'-'],input=code,capture_output=True,text=True,encoding='utf-8',check=True)
    return json.loads(done.stdout)

hub=site.generated['OUVRIR-LES-DOSSIERS.html'].decode('utf-8')
paths=[];launcher_mode='historical hub'
if site.is_master_launcher(hub):
    launcher_mode='master launcher'
    assert site.generated['index.html']==site.generated['OUVRIR-LES-DOSSIERS.html']
    assert site.MASTER_HOME in documents
    assert site.generated['OUVRIR-LES-DOSSIERS.html']==site.files['OUVRIR-LES-DOSSIERS.html'].read_bytes()
else:
    code=re.search(r'const readingRoutes=.*?const href=.*?;',hub)[0]
    paths=list(site.routes)
    actual=execute(code+'process.stdout.write(JSON.stringify('+json.dumps(paths)+'.map(href)));')
    assert all(unquote(result)==site.routes[path] for path,result in zip(paths,actual))

portal=site.generated['6241 Léger/00_Lire_en_premier/index.html'].decode('utf-8')
data=json.loads(re.search(r'const DATA=([\s\S]*?);\s*const \$=',portal)[1])
code=re.search(r'const readingRoutes=.*?const availablePaths=.*?const localHref=.*?;',portal,re.S)[0]
case_paths=[p for p in data['resource_paths'] if '6241 Léger/'+p in site.routes]
actual=execute('const DATA='+json.dumps({'resource_paths':data['resource_paths']})+';'+code+'process.stdout.write(JSON.stringify('+json.dumps(case_paths)+'.map(localHref)));')
assert all(unquote(result)=='../'+site.routes['6241 Léger/'+path][len('6241 Léger/'):] for path,result in zip(case_paths,actual))

receipt={'mode':'Génération en mémoire seulement; aucune écriture dist-site et aucune publication','launcher_mode':launcher_mode,'generated_pages':len(documents),'static_links_checked':audit['static_links_checked'],'html_anchors_checked':anchors,'broken_anchors':broken_anchors,'raw_reading_links':raw_reading_links,'hub_markdown_routes_executed':len(paths),'leger_markdown_routes_executed':len(case_paths),'original_source_hashes_checked':len(site.hashes)}
changed=[r for r,p in site.files.items() if site.digest(p.read_bytes())!=site.hashes[r]]
assert not changed,changed[:3]
out=ROOT/'scripts/.build-livrables/reader-navigation-validation.json'
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
