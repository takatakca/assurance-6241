"""Test the built tree over HTTP beneath /dist-site/, as Pages uses a repo prefix."""
from pathlib import Path
from functools import partial
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.parse import quote
import hashlib, json, threading

ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'dist-site'
class Quiet(SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(ROOT)))
thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
try:
    manifest=json.loads((OUT/'.site-build.json').read_text(encoding='utf-8'))
    files=manifest['output_files'];base=f'http://127.0.0.1:{server.server_port}/dist-site/'
    selected=['index.html','assets/site-viewer.js','assets/site-reader.css',
        '6241 Léger/00_Lire_en_premier/index.html','6280 Somerled NDG/index.html',
        'HARMONY MOVERS/index.html','documentation/REGLES-COMMUNES.md.html']
    for suffix in ['.pdf','.xlsx','.pptx','.eml','.json','.csv','.jpg','.zip']:
        candidate=next((p for p in files if p.lower().endswith(suffix)),None)
        if candidate:selected.append(candidate)
    for rel in ['HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/LIRE-EN-PREMIER.md.html',
                'HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/REPONSES-AUX-25-DEMANDES.pdf',
                'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md.html',
                'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/BILAN-DE-LA-RECHERCHE.md.html',
                'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/ChatGPT/BILAN-REPRISE-CHATGPT.md.html',
                'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/ChatGPT/COUVERTURE-REPRISE-CHATGPT-2026-10-24.json']:
        if rel in files:selected.append(rel)
    results=[]
    for rel in selected:
        url=base+quote(rel,safe='/')
        method='GET' if rel.endswith(('.html','.js','.css')) else 'HEAD'
        with urlopen(Request(url,method=method),timeout=30) as response:
            assert response.status==200,rel
            assert int(response.headers['Content-Length'])==(OUT/rel).stat().st_size,rel
            if method=='GET':assert hashlib.sha256(response.read()).hexdigest()==hashlib.sha256((OUT/rel).read_bytes()).hexdigest(),rel
            if rel.endswith('.html'):assert response.headers.get_content_type()=='text/html',rel
            if rel.endswith('.pdf'):assert response.headers.get_content_type()=='application/pdf',rel
            if rel.endswith('.zip'):assert response.headers.get_content_type() in ('application/zip','application/x-zip-compressed'),rel
            results.append({'path':rel,'status':response.status,'mime':response.headers.get_content_type()})
    receipt={'passed':len(results),'scope':'Local HTTP beneath a repository-style path prefix; not proof of public deployment','checks':results}
    (ROOT/'scripts/.build-livrables/remote-site-transport.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=False,indent=2))
finally:server.shutdown();server.server_close()
