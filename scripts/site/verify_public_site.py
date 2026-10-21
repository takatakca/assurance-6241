"""Verify the authorized public Pages site against the built local snapshot."""
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote
from urllib.error import HTTPError, URLError
from datetime import datetime, timezone
import hashlib, json

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'dist-site'
BASE='https://takatakca.github.io/assurance-6241/'
manifest=json.loads((OUT/'.site-build.json').read_text(encoding='utf-8'))
paths=['index.html','6241 Léger/00_Lire_en_premier/index.html',
       '6280 Somerled NDG/index.html','HARMONY MOVERS/index.html']
fieldy='HARMONY MOVERS/11_Fieldy/2026-10-05-Fieldy-interrogatoire-Quadro-Harmony.pdf'
pdf=fieldy if fieldy in manifest['output_files'] else min(
    (p for p in manifest['output_files'] if p.lower().endswith('.pdf')),key=lambda p:(OUT/p).stat().st_size)
paths.append(pdf)
eml=min((p for p in manifest['output_files'] if p.lower().endswith('.eml')),
        key=lambda p:(OUT/p).stat().st_size)
paths.append(eml)
for path in ['HARMONY MOVERS/11_Fieldy/README.md.html',
             'HARMONY MOVERS/11_Fieldy/ANALYSE-FIELDY-POUR-CABINET.md.html',
             'HARMONY MOVERS/11_Fieldy/texte-natif-pages.json']:
    if path in manifest['output_files']:paths.append(path)
checks=[]
for path in paths:
    url=BASE+quote(path,safe='/')
    try:
        with urlopen(Request(url,headers={'User-Agent':'assurance-6241-verification'}),timeout=25) as response:
            data=response.read()
            matches=hashlib.sha256(data).hexdigest()==manifest['output_hashes'][path]
            mime=response.headers.get_content_type()
            expected='application/pdf' if path.endswith('.pdf') else ('message/rfc822' if path.endswith('.eml') else ('application/json' if path.endswith('.json') else 'text/html'))
            checks.append({'path':path,'url':url,'status':response.status,'mime':mime,
                           'sha256_matches':matches,'ok':response.status==200 and matches and (mime==expected or path.endswith('.eml'))})
    except HTTPError as exc:checks.append({'path':path,'url':url,'status':exc.code,'ok':False})
    except (URLError,TimeoutError):checks.append({'path':path,'url':url,'status':0,'ok':False})
receipt={'as_of':datetime.now(timezone.utc).isoformat(),'ok':all(c['ok'] for c in checks),
         'base_url':BASE,'checks':checks}
dest=ROOT/'scripts/.build-livrables/public-site-verification.json'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
raise SystemExit(0 if receipt['ok'] else 1)
