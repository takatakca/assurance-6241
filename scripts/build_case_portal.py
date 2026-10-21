from pathlib import Path, PurePosixPath
import json, csv, hashlib, re
from collections import Counter
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
CASE=ROOT/'6241 Léger'
INDEX=CASE/'09_Index_et_tracabilite'
HOME=CASE/'00_Lire_en_premier'
INDEX.mkdir(parents=True,exist_ok=True);HOME.mkdir(parents=True,exist_ok=True)
(INDEX/'Texte_et_OCR').mkdir(parents=True,exist_ok=True)
warnings=[]
def read_json(p,default):
    try:return json.loads(p.read_text(encoding='utf-8-sig'))
    except (FileNotFoundError,json.JSONDecodeError) as exc:
        warnings.append(f'Source non chargée : {p.relative_to(CASE).as_posix()} ({type(exc).__name__}).')
        return default

def read_text(p):
    try:return p.read_text(encoding='utf-8-sig')
    except (OSError,UnicodeError) as exc:
        warnings.append(f'Texte non indexé : {p.name} ({type(exc).__name__}).')
        return ''

def source_reference(value):
    """Resolve source paths only inside this case; fragments are source locators."""
    raw=str(value)
    normalized=raw.replace('\\','/')
    if normalized.startswith(CASE.name+'/'):normalized=normalized[len(CASE.name)+1:]
    path,_,locator=normalized.partition('#')
    parts=PurePosixPath(path).parts
    valid=bool(path) and not path.startswith('/') and not any(p in ('..','.') for p in parts) and ':' not in path
    target=CASE/path if valid else None
    if valid:
        try:valid=target.resolve().is_relative_to(CASE.resolve())
        except OSError:valid=False
    exists=valid and target.is_file()
    if not exists:warnings.append(f'Référence locale indisponible : {raw}')
    return {'path':path if valid else None,'locator':locator,'original':raw,'exists':bool(exists)}

def mail_url(value):
    try:
        url=urlsplit(value or '')
        if url.scheme=='https' and url.netloc=='mail.google.com' and not url.username:return value
    except ValueError:pass
    return None

def csv_safe(value):
    text=str(value)
    # Formula triggers after whitespace/control characters must stay literal.
    return "'"+text if re.match(r'^[\s\x00-\x1f]*[=+@-]',text) or text.startswith(('\t','\r','\n')) else value
# Write generated documentation before inventory hashing.
(HOME/'LIRE-EN-PREMIER.md').write_text('''# 6241 boulevard Léger, Montréal

Dossier de travail pour l’avocat — consolidation du 21 octobre 2026.

## Commencer ici

Ouvrir **index.html** dans ce dossier : recherche dans les noms de fichiers, les textes PDF et l’OCR, filtres par catégorie, accès aux pièces originales et chronologie. Le tableau de bord fonctionne localement sans connexion et sans modifier les documents.

1. Portrait : `01_Synthese_et_chronologie/`.
2. Conversations extraites : `02_Conversations/` (rôles et provenance conservés).
3. Courriels : `03_Courriels/Analyse_consolidee/` puis les messages sources.
4. Documents et images : `04_Pieces_jointes/` et `05_Photos_et_captures/`.
5. Comptabilité : `07_Dommages_et_pertes/Comptabilite/`.
6. Présentation : `08_Correspondance_et_procedures/Presentations/`.
7. Inventaire, empreintes et textes : `09_Index_et_tracabilite/`.
8. Archive historique reçue : `10_Archive_avocat_2026-10-05/`.

## Règles de lecture

- Un devis, une facture, une allocation d’assurance et un paiement bancaire sont quatre objets différents.
- Les déclarations dans les chats et les positions des intervenants sont attribuées à leur auteur. Les réponses ChatGPT ne sont pas des preuves originales.
- La chronologie distingue la date de l’événement de celle du message qui le raconte. Les dates imprimées restent inchangées.
- Les versions annulées, les copies et les doublons restent traçables. Un fichier copié plusieurs fois n’est compté qu’une fois par empreinte de contenu.
- L’OCR automatique aide à chercher; vérifier les citations, montants et dates sur l’image ou le PDF. Le moteur disponible utilise en-US et peut mal reconnaître le français.
- Les documents du sinistre antérieur et ceux du transport Harmony doivent être rapprochés par bien et par dommage, sans addition automatique.

## Couverture et travail restant

Les états d’extraction détaillés figurent dans les index des conversations et des courriels. Ils distinguent les pièces obtenues, les pièces seulement mentionnées et les tentatives non abouties. L’archivage local ne prouve pas à lui seul la synchronisation OneDrive ni l’exhaustivité de tous les comptes.

La demande récente de rencontre sans avocat reste à rapprocher du courriel exact. Une citation retrouvée du 21 octobre 2025 dit que l’intervenant transigera avec le représentant si un avocat est mandaté; ce n’est pas une exigence de renoncer à un avocat.

## Travail partagé

Le dépôt GitHub créé est https://github.com/takatakca/assurance-6241. Son contenu publié doit être vérifié séparément de cette consolidation OneDrive. Les dossiers «6280 Somerled NDG» et «HARMONY MOVERS» sont classés à côté; les pièces communes sont référencées avec leur origine.
''',encoding='utf-8')
records=[]
for f in sorted(CASE.rglob('*')):
    if not f.is_file() or '99_Travail_et_collecte' in f.parts:continue
    rel=f.relative_to(CASE).as_posix()
    if rel.startswith('09_Index_et_tracabilite/') or rel in ['00_Lire_en_premier/index.html','00_Lire_en_premier/tableau-de-bord.json']:continue
    b=f.read_bytes();sha=hashlib.sha256(b).hexdigest()
    records.append({'id':'F-'+sha[:12].upper(),'path':rel,'name':f.name,'category':rel.split('/')[0],'bytes':len(b),'sha256':sha,'format':f.suffix[1:].upper(),'text':''})
extractions=read_json(INDEX/'Texte_et_OCR/manifest-extraction.json',[])
ocr_results=read_json(CASE/'99_Travail_et_collecte/ocr-images/ocr-resultats.json',[])
ocr_map={(r['id'],r['page']):r for r in ocr_results}
ocr_summary={'pages_requested':len(ocr_results),'pages_succeeded':sum(not r.get('error') for r in ocr_results),'nonempty':sum(r.get('characters',0)>0 for r in ocr_results),'language':'en-US','qualification':'Texte automatique à contrôler sur l’original, particulièrement accents, dates et chiffres.'}
for d in extractions:
    chunks=[]
    for p in d['pages']:
        if p.get('text_file'):
            chunks.append(f'\n[Page {p["page"]} — texte PDF]\n'+read_text(INDEX/'Texte_et_OCR'/p['text_file']))
        result=ocr_map.get((d['id'],p['page']))
        if result and not result.get('error'):
            # Prefer the colocated copy, so a cloned/moved OneDrive dossier works.
            original=Path(result['output'])
            filename=str(result['output']).replace('\\','/').rsplit('/',1)[-1]
            local=INDEX/'Texte_et_OCR'/filename
            dest=local if local.is_file() else original
            p['ocr_file']=filename;p['ocr_characters']=result.get('characters',0);p['ocr_language']='en-US'
            chunks.append(f'\n[Page {p["page"]} — OCR automatique à contrôler]\n'+read_text(dest))
    d['search_text']='\n'.join(chunks)
by_hash={d['sha256']:d for d in extractions}
hash_counts=Counter(r['sha256'] for r in records)
for r in records:
    d=by_hash.get(r['sha256'])
    if d:
        r['text']=d.get('search_text','');r['pages']=len(d['pages']);r['extraction']='Texte/OCR disponible'
    elif r['format'] in ['MD','TXT','CSV']:
        try:r['text']=(CASE/r['path']).read_text(encoding='utf-8-sig')
        except UnicodeError:pass
    r['duplicate_count']=hash_counts[r['sha256']]
events=read_json(CASE/'01_Synthese_et_chronologie/chronologie-chatgpt.json',{})
events=events.get('events',[]) if isinstance(events,dict) else events
email_index=read_json(CASE/'03_Courriels/Analyse_consolidee/emails-index.json',{})
mail_events=email_index.get('chronology',[]) if isinstance(email_index,dict) else []
timeline=[]
for e in events:
    timeline.append({'id':e.get('id'),'family':'chat','date':e.get('date'),
        'date_label':'Date retenue dans la source','title':e.get('title',e.get('event','')),
        'summary':e.get('summary',e.get('description','')),'status':e.get('status','À contrôler'),
        'source_kind':e.get('source_kind','Conversation ChatGPT'),
        'source_title':e.get('source_title','Conversation source'),'author':e.get('author',''),
        'message_date':e.get('date_message_locale'),'message_date_label':'Date du message dans ChatGPT',
        'message_id':e.get('source_turn_id'),'thread_id':e.get('source_thread_id'),
        'source_refs':[source_reference(e['source_text_file'])] if e.get('source_text_file') else [],
        'notes':[n for n in [e.get('current_scope_note'),*(e.get('exact_dates_conflicts') or [])] if n],
        'anchor':'','gmail_url':None})
mail_status={'citation_dans_transfert':'Texte cité dans un transfert',
    'declaration_client_dans_transfert':'Déclaration du client citée dans un transfert',
    'message_direct':'Message direct récupéré',
    'message_direct_aux_intermediaires':'Message direct aux intermédiaires'}
for e in mail_events:
    forwarded='transfert' in e.get('evidence_level','')
    timeline.append({'id':e.get('id'),'family':'mail','date':e.get('event_date'),
        'date_label':'Date du texte cité' if forwarded else 'Date du message',
        'title':e.get('title',''),'summary':e.get('description',''),
        'status':mail_status.get(e.get('evidence_level'),'Courriel à contrôler'),
        'source_kind':e.get('evidence_level'),'source_title':'Courriel source',
        'author':e.get('author',''),'message_date':e.get('envelope_date'),
        'message_date_label':'Date du message qui contient la citation' if forwarded else 'Date de l’enveloppe du message',
        'message_id':e.get('message_id'),'thread_id':e.get('thread_id'),
        'source_refs':[source_reference(p) for p in e.get('source_files',[])],
        'notes':[],'anchor':e.get('text_anchor',''),'gmail_url':mail_url(e.get('gmail_url'))})
timeline.sort(key=lambda e:(e.get('date') or '9999',e.get('family',''),e.get('id','')))
resource_paths={f.relative_to(CASE).as_posix() for f in CASE.rglob('*') if f.is_file() and '99_Travail_et_collecte' not in f.parts}
resource_paths.update(['09_Index_et_tracabilite/INVENTAIRE-FICHIERS.csv','09_Index_et_tracabilite/INVENTAIRE-FICHIERS.json'])
data={'as_of':'2026-10-21','files':records,'events':events,'mail_events':mail_events,'timeline':timeline,
    'resource_paths':sorted(resource_paths),'warnings':warnings,'ocr':ocr_summary,
    'counts':{'files':len(records),'distinct_contents':len(hash_counts),'pdf_images':len(extractions),
        'pages':sum(len(d['pages']) for d in extractions),'chat_events':len(events),'mail_events':len(mail_events)}}
with (INDEX/'INVENTAIRE-FICHIERS.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=['id','path','category','format','bytes','sha256','duplicate_count'],extrasaction='ignore');writer.writeheader();writer.writerows({k:csv_safe(v) for k,v in r.items() if k!='text'} for r in records)
(INDEX/'INVENTAIRE-FICHIERS.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='text'} for r in records],ensure_ascii=False,indent=2),encoding='utf-8')
(INDEX/'Texte_et_OCR/CONTROLE-OCR.json').write_text(json.dumps(ocr_summary,ensure_ascii=False,indent=2),encoding='utf-8')
(INDEX/'Texte_et_OCR/manifest-extraction.json').write_text(json.dumps([{k:v for k,v in r.items() if k!='search_text'} for r in extractions],ensure_ascii=False,indent=2),encoding='utf-8')
(HOME/'tableau-de-bord.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
template=(ROOT/'scripts/case_portal_template.html').read_text(encoding='utf-8')
(HOME/'index.html').write_text(template.replace('/*CASE_DATA*/',json.dumps(data,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')),encoding='utf-8')

print(json.dumps({'files':len(records),'distinct':data['counts']['distinct_contents'],'timeline':len(timeline),'warnings':warnings,'ocr':ocr_summary},ensure_ascii=False))

