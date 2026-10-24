"""Check actual master output: local links/anchors, unchanged bundle, and content search."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import hashlib,json,subprocess,posixpath
ROOT=Path(__file__).resolve().parents[2]
MASTER=ROOT/'00_DOSSIER_MAITRE'
class Audit(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=set();self.handlers=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        for key in ('href','src'):
            if key in a:self.links.append((tag,key,a[key],'download' in a))
        self.handlers += [k for k in a if k.lower().startswith('on')]
def main():
    manifest=json.loads((MASTER/'07_Controle_des_sources/CONTROLE-DU-MAITRE.json').read_text(encoding='utf-8'))
    pages={};errors=[];links=0;raw_md=[];anchors=0
    for rel in manifest['files']:
        if not rel.endswith('.html'):continue
        parser=Audit();parser.feed((ROOT/rel).read_text(encoding='utf-8'));pages[rel]=parser
        if parser.handlers:errors.append({'page':rel,'inline_handlers':parser.handlers})
    for rel,parser in pages.items():
        for tag,key,url,download in parser.links:
            parts=urlsplit(url)
            if parts.scheme or parts.netloc:continue
            target=posixpath.normpath(posixpath.join(posixpath.dirname(rel),unquote(parts.path))) if parts.path else rel
            links+=1
            if not (ROOT/target).is_file():errors.append({'source':rel,'missing':target})
            if target.endswith('.md') and not download:raw_md.append({'source':rel,'raw_markdown':target})
            fragment=unquote(parts.fragment)
            if fragment and target in pages:
                anchors+=1
                if fragment not in pages[target].ids:errors.append({'source':rel,'missing_anchor':target+'#'+fragment})
    assert not raw_md,raw_md[:10]
    assert not errors,errors[:20]
    bundle=ROOT/'HARMONY MOVERS/12_Remise_Dufourd_2026-10-21'
    original={'REPONSES-AUX-25-DEMANDES.pdf':'bce7adaeeb235e48d57f32cfc85a34fee7336a60a818167195426b4ce9d6229b','DOSSIER-DUFOURD-2026-10-21.zip':'342809b5b41d43d7170d868e66d851c05905ca1d413869f638af9e493d95aacb'}
    for path,expected in original.items():assert hashlib.sha256((bundle/path).read_bytes()).hexdigest()==expected,path
    node=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    proc=subprocess.run([str(node),str(ROOT/'scripts/site/verify_master_search.cjs')],capture_output=True,text=True,encoding='utf-8')
    assert proc.returncode==0,proc.stderr
    search=json.loads(proc.stdout)
    report={'ok':True,'html_pages':len(pages),'links_checked':links,'anchors_checked':anchors,'raw_markdown_reading_links':len(raw_md),'bundle_pdf_zip_unchanged':True,'search':search}
    (ROOT/'scripts/.build-livrables/master-workspace-validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
if __name__=='__main__':main()
