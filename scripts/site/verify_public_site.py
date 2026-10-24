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
             'HARMONY MOVERS/11_Fieldy/texte-natif-pages.json',
             'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md.html',
             'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_Ooeuf/PROVENANCE-OOEUF.json',
             'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_Ooeuf/Scan2026-04-03_120155.pdf',
             'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_Ooeuf/Declaration-TPS-TVQ-2024-09-30.pdf',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/BILAN-DE-LA-RECHERCHE.md.html',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/ChatGPT/BILAN-REPRISE-CHATGPT.md.html',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/ChatGPT/COUVERTURE-REPRISE-CHATGPT-2026-10-24.json',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Ooeuf/Polices/10043375-Renouvellement-2024-2025.pdf',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Ooeuf/Polices/10043375-Nouveau-contrat-2023-2024.pdf',
             'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Autorisation_SPVM/AUTORISATION-SPVM-MTLEV2500487177-A-SIGNER.pdf']:
    if path in manifest['output_files']:paths.append(path)
remise='HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/'
if remise+'LIRE-EN-PREMIER.md.html' in manifest['output_files']:paths.append(remise+'LIRE-EN-PREMIER.md.html')
for extension in ['.pdf','.zip']:
    candidates=[p for p in manifest['output_files'] if p.startswith(remise) and p.lower().endswith(extension)]
    if candidates:paths.append(min(candidates,key=lambda p:('/' in p[len(remise):],(OUT/p).stat().st_size)))
master='00_DOSSIER_MAITRE/'
paths += [p for p in [master+'00-OUVRIR-LE-DOSSIER.html',master+'01_6241_Leger/index.html',master+'02_6280_Somerled_NDG/index.html',master+'03_Harmony_Movers/index.html',master+'04_Remise_et_suivis/index.html',master+'05_Table_des_matieres/index.html',master+'07_Controle_des_sources/index.html',master+'assets/master.css',master+'assets/app.js',master+'assets/search-core.js',master+'06_Index_recherche/metadata.js'] if p in manifest['output_files']]
paths += sorted(p for p in manifest['output_files'] if p.startswith(master+'06_Index_recherche/recherche-') and p.endswith('.js'))
draft=OUT/master/'04_Remise_et_suivis/COURRIEL-DE-REMISE.md'
if draft.is_file():
    reader=master+'08_Lectures/'+hashlib.sha256(draft.read_bytes()).hexdigest()+'.html'
    if reader in manifest['output_files']:paths.append(reader)
for source in ['6241 Léger/10_Archive_avocat_2026-10-05/comptabilite-ventes2024/final.xls',
               'HARMONY MOVERS/04_Factures_et_comptabilite/Collecte_Gmail_2026-10-21/19cb1ecd4a7964a1__quadro excel sort.xls',
               'HARMONY MOVERS/04_Factures_et_comptabilite/Collecte_Gmail_2026-10-21/19cb13a2879f146c__quadro excel sort.xls',
               'HARMONY MOVERS/15_Suivi_extractions_2026-10-24/BILAN-DU-LOT.md']:
    if (OUT/source).is_file():
        reader=master+'08_Lectures/'+hashlib.sha256((OUT/source).read_bytes()).hexdigest()+'.html'
        if reader in manifest['output_files']:paths.append(reader)
        if source+'.html' in manifest['output_files']:paths.append(source+'.html')
checks=[]
for path in paths:
    url=BASE+quote(path,safe='/')
    try:
        with urlopen(Request(url,headers={'User-Agent':'assurance-6241-verification'}),timeout=25) as response:
            data=response.read()
            matches=hashlib.sha256(data).hexdigest()==manifest['output_hashes'][path]
            mime=response.headers.get_content_type()
            expected='application/pdf' if path.endswith('.pdf') else ('message/rfc822' if path.endswith('.eml') else ('application/json' if path.endswith('.json') else ('application/zip' if path.endswith('.zip') else 'text/html')))
            if path.endswith('.js'):expected='application/javascript'
            if path.endswith('.css'):expected='text/css'
            mime_ok=(mime==expected or path.endswith('.eml') or (path.endswith('.zip') and mime=='application/x-zip-compressed'))
            if path.endswith('.js') and mime=='text/javascript':mime_ok=True
            checks.append({'path':path,'url':url,'status':response.status,'mime':mime,
                           'sha256_matches':matches,'ok':response.status==200 and matches and mime_ok})
    except HTTPError as exc:checks.append({'path':path,'url':url,'status':exc.code,'ok':False})
    except (URLError,TimeoutError):checks.append({'path':path,'url':url,'status':0,'ok':False})
receipt={'as_of':datetime.now(timezone.utc).isoformat(),'ok':all(c['ok'] for c in checks),
         'base_url':BASE,'checks':checks}
dest=ROOT/'scripts/.build-livrables/public-site-verification.json'
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
raise SystemExit(0 if receipt['ok'] else 1)
