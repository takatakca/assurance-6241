"""Build the portable OneDrive master from the attributed, deduplicated corpus.

Originals and the lawyer's annex bundle are never moved or modified. The same
HTML/JS files work on file:// and beneath the GitHub Pages repository prefix.
"""
from pathlib import Path, PurePosixPath
from collections import defaultdict
from urllib.parse import quote, unquote, urlsplit
from datetime import datetime, timezone
import csv, hashlib, html, importlib.util, json, posixpath, re

ROOT = Path(__file__).resolve().parents[1]
MASTER = '00_DOSSIER_MAITRE'
HOME = MASTER + '/00-OUVRIR-LE-DOSSIER.html'
CORPUS = ROOT / MASTER / '06_Index_recherche/corpus.json'
CASES = ['6241 Léger', '6280 Somerled NDG', 'HARMONY MOVERS', 'Remise et suivis']
SECTIONS = ['01_6241_Leger', '02_6280_Somerled_NDG', '03_Harmony_Movers', '04_Remise_et_suivis']
REM = 'HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/'
SPVM = 'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Autorisation_SPVM/AUTORISATION-SPVM-MTLEV2500487177-A-SIGNER.pdf'
spec = importlib.util.spec_from_file_location('remote_renderer', ROOT / 'scripts/build_remote_site.py')
renderer = importlib.util.module_from_spec(spec); spec.loader.exec_module(renderer)
RULE = renderer.RULE
written = {}; readers = {}; selected = set(); reader_sources = {}; missing = []; previous = {}
PLANNED = {HOME, MASTER+'/05_Table_des_matieres/index.html', MASTER+'/07_Controle_des_sources/index.html', *[MASTER+'/'+d+'/index.html' for d in SECTIONS]}

def esc(s): return html.escape(str(s), quote=True)
def sha(b): return hashlib.sha256(b).hexdigest()
def href(target, source): return quote(posixpath.relpath(target, posixpath.dirname(source) or '.'), safe='/')
def write(path, text):
    data = text.encode('utf-8') if isinstance(text, str) else text
    target = ROOT / path; target.parent.mkdir(parents=True, exist_ok=True)
    current = target.read_bytes() if target.exists() else None
    if current != data:
        if current is not None and path in previous and sha(current) != previous[path]:
            raise RuntimeError('Un fichier généré a été modifié hors du générateur; modification conservée : '+path)
        target.write_bytes(data)
    written[path] = sha(data)
def link(label, target, source, cls='', raw=False):
    target = target if raw else readers.get(target, target)
    return f'<a href="{href(target, source)}"' + (f' class="{cls}"' if cls else '') + (' download' if raw else '') + f'>{esc(label)}</a>'
def layout(title, body, source, scripts=(), reader=False):
    csp = "default-src 'none'; script-src 'self'; style-src 'self'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    rootrel = posixpath.relpath('.', posixpath.dirname(source) or '.') + '/'
    return f'''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="referrer" content="no-referrer"><meta http-equiv="Content-Security-Policy" content="{esc(csp)}"><title>{esc(title)} · Dossier maître</title><link rel="stylesheet" href="{href(MASTER+'/assets/master.css',source)}"></head><body data-workspace-root="{rootrel}"><a class="skip" href="#contenu">Aller au contenu</a><header class="topbar"><a class="brand" href="{href(HOME,source)}">DOSSIER MAÎTRE · 6241</a><nav class="toplinks" aria-label="Navigation principale"><a href="{href(HOME,source)}#recherche">Rechercher</a><a href="{href(MASTER+'/05_Table_des_matieres/index.html',source)}">Table des matières</a><a href="{href(MASTER+'/04_Remise_et_suivis/index.html',source)}">Remise et suivis</a></nav></header><main id="contenu" class="{'reader' if reader else ''}">{body}</main><footer class="footer"><strong>Provenance et contrôle des pièces</strong><p>{RULE}</p><p>Les pièces d’origine restent dans leurs dossiers. L’index est une copie de travail datée; une recherche sans résultat ne démontre pas l’absence d’une pièce. Les synchronisations OneDrive et GitHub sont distinctes.</p></footer>{''.join('<script defer src="'+href(s,source)+'"></script>' for s in scripts)}</body></html>'''

def resolve(value, source, image=False, raw=False):
    value = html.unescape(value.strip()); parts = urlsplit(value.replace('\\', '/'))
    if not parts.path and parts.fragment: return '#' + quote(unquote(parts.fragment), safe='-_=')
    origin = reader_sources.get(source, source)
    target = None
    if parts.scheme in ('http', 'https'):
        if parts.netloc == 'takatakca.github.io' and parts.path.startswith('/assurance-6241/'):
            target = unquote(parts.path[len('/assurance-6241/'):])
        else: return esc(value) if not image else None
    elif parts.scheme == 'mailto': return esc(value) if not image else None
    elif parts.scheme == 'file' or re.match(r'^[A-Za-z]:[/\\]', value):
        local = unquote(parts.path) if parts.scheme == 'file' else value
        if re.match(r'^/[A-Za-z]:/', local): local = local[1:]
        try: target = Path(local).resolve().relative_to(ROOT.resolve()).as_posix()
        except (ValueError, OSError): target = None
    elif not parts.scheme and not parts.netloc:
        target = posixpath.normpath(posixpath.join(posixpath.dirname(origin), unquote(parts.path)))
    if target and target.endswith('.md.html') and target[:-5] in selected: target = target[:-5]
    if target and (ROOT / target).is_dir():
        case = target.split('/')[0]
        if case in CASES: target = MASTER + '/' + SECTIONS[CASES.index(case)] + '/index.html'
    if target and (target in selected or target in PLANNED or target in readers.values()):
        dest = target if raw else readers.get(target, target)
        return href(dest, source) + ('#' + quote(unquote(parts.fragment), safe='-_=') if parts.fragment else '')
    if target == 'index.html' or target == 'OUVRIR-LES-DOSSIERS.html': return href(HOME, source)
    missing.append({'source': origin, 'reference': value})
    return None

def title_for(path):
    return PurePosixPath(path).stem.replace('_', ' ').replace('-', ' ')
def nature(doc):
    path = doc['path'].lower()
    if 'ocr' in path: return 'Extraction OCR — contrôle sur l’original requis'
    if any(s in path for s in ('analyse','synthese','synthèse','reponses','réponses','bilan','remise_et_suivis')): return 'Document de travail / analyse attribuée'
    if 'declaration' in path or 'precisions-du-client' in path: return 'Déclaration attribuée au client'
    if 'chatgpt' in path or 'conversations' in path: return 'Conversation — rôles et déclarations à distinguer'
    if doc['format'] == 'eml' or 'courriel' in path: return 'Courriel ou copie de correspondance'
    return 'Pièce du dossier — provenance à consulter'

def friendly_status(value):
    return {'texte_natif_disponible':'Texte disponible','texte_disponible_ocr_a_controler':'OCR disponible — à contrôler sur l’original','partiel_pages_sans_texte':'Texte partiel — certaines pages restent à extraire','partiel_limite_explicite':'Extrait limité — consulter le document complet','non_indexe_aucun_texte_detecte':'Aucun texte exploitable extrait','non_indexe_erreur_ou_format':'Lecture textuelle indisponible pour ce format'}.get(value,str(value).replace('_',' '))
def friendly_method(value):
    value=str(value or '')
    if 'ocr' in value.lower():return 'OCR automatique — à contrôler'
    if 'pdf_' in value:return 'Texte natif du PDF'
    if 'xlsx' in value:return 'Cellules du classeur — valeurs non recalculées'
    if 'OOXML' in value:return 'Texte du document — unité logique'
    if 'EML' in value:return 'Corps du courriel et noms des pièces jointes'
    if 'json' in value.lower():return 'Texte du courriel exporté'
    if 'html' in value:return 'Texte visible de la page'
    if 'image_sans' in value:return 'Image sans texte extrait'
    return 'Texte du fichier'

def section_path(case_index): return MASTER + '/' + SECTIONS[case_index] + '/index.html'
def main():
    previous_manifest = ROOT/MASTER/'07_Controle_des_sources/CONTROLE-DU-MAITRE.json'
    if previous_manifest.is_file(): previous.update(json.loads(previous_manifest.read_text(encoding='utf-8'))['files'])
    corpus = json.loads(CORPUS.read_text(encoding='utf-8-sig'))
    documents = corpus['documents']
    # Select exactly the same documentary perimeter as the remote renderer.
    renderer.collect(); selected.update(r for r in renderer.files if not r.startswith(MASTER+'/'))
    selected.update(p.relative_to(ROOT).as_posix() for p in (ROOT/MASTER/'04_Remise_et_suivis').glob('*') if p.is_file() and p.suffix in {'.md','.txt'})
    doc_by_hash = {d['sha256']: d for d in documents}
    for doc in documents:
        doc['format'] = doc.get('format', PurePosixPath(doc['path']).suffix).lower().lstrip('.')
        doc['aliases'] = [a for a in doc.get('aliases', []) if isinstance(a, str) and a != doc['path'] and a in selected]
        doc['title'] = doc.get('title') or title_for(doc['path'])
        if doc['format']=='md':
            heading=re.search(r'^#\s+(.{1,180})$',(ROOT/doc['path']).read_text(encoding='utf-8-sig',errors='replace'),re.M)
            if heading:doc['title']=heading[1]
        doc['nature'] = doc.get('source_nature') or nature(doc)
        if not doc.get('pages') and doc.get('text'): doc['pages'] = [{'page':None,'text':doc['text'],'method':doc.get('extraction_status','Extraction textuelle')}]
        doc['extraction_status']=friendly_status(doc['extraction_status'])
        for pg in doc.get('pages',[]):pg['method']=friendly_method(pg.get('method'))
    text_formats = {'.md','.txt','.eml','.json','.csv','.docx','.xlsx','.xls','.html'}
    for path in sorted(selected):
        if PurePosixPath(path).suffix.lower() not in text_formats or path.startswith(MASTER+'/08_Lectures/'): continue
        digest = sha((ROOT/path).read_bytes())
        output = MASTER + '/08_Lectures/' + digest + '.html'
        readers[path] = output
        if output not in reader_sources: reader_sources[output] = doc_by_hash.get(digest, {}).get('path', path)
    for doc in documents:
        if doc['path'] in readers: doc['reader'] = readers[doc['path']]
    renderer.resolve_link = resolve
    groups = defaultdict(lambda: defaultdict(list))
    for doc in documents:
        case = doc.get('case') or doc['path'].split('/')[0]
        if case not in CASES: case = 'Remise et suivis' if doc['path'].startswith(MASTER) else 'HARMONY MOVERS'
        doc['case'] = case
        parts = doc['path'].split('/')
        folder = parts[1] if case != 'Remise et suivis' and len(parts)>2 else 'Préparation de la remise'
        groups[case][folder].append(doc)
    order = 0; section_lists = {}
    for ci, case in enumerate(CASES):
        sections = []
        for si, (folder, docs) in enumerate(sorted(groups[case].items()), 1):
            number = f'{ci+1}.{si}'
            label = re.sub(r'^\d+[_ -]*','',folder).replace('_',' ')
            for di, doc in enumerate(sorted(docs, key=lambda d:(d['title'].casefold(),d['path'])),1):
                order += 1; doc['number'] = f'{number}.{di}'; doc['sort'] = order
            sections.append((number,label,sorted(docs,key=lambda d:d['sort'])))
        section_lists[case] = sections
    for rel in ('master.css','search-core.js','app.js'):
        write(MASTER+'/assets/'+rel,(ROOT/'scripts/master'/rel).read_bytes())
    # Generate standalone reading views. Relative source references are resolved
    # against the original document, then routed to these portable HTML readers.
    for output, path in sorted(reader_sources.items()):
        p = ROOT/path; digest = sha(p.read_bytes()); doc = doc_by_hash.get(digest)
        title = doc['title'] if doc else title_for(path)
        if p.suffix.lower() == '.md':
            content = '<section id="page-1">'+renderer.markdown(p.read_text(encoding='utf-8-sig',errors='replace'),output)+'</section>'
        elif p.suffix.lower() == '.html':
            parser = renderer.ArchiveReader(output); parser.feed(p.read_text(encoding='utf-8-sig',errors='replace')); content = '<section id="page-1">'+''.join(parser.out)+'</section>'
        else:
            pages = doc.get('pages',[]) if doc else []
            if not pages and p.suffix.lower() in {'.txt','.csv','.json'}:
                pages = [{'page':None,'text':p.read_text(encoding='utf-8-sig',errors='replace'),'method':'Lecture du fichier texte'}]
            content = '<h1>'+esc(title)+'</h1>'
            if not pages: content += '<p>La lecture textuelle de ce format n’est pas disponible dans cet index. Télécharger la pièce source ci-dessus.</p>'
            for idx, item in enumerate(pages,1):
                n = item.get('page'); label = ('Feuille '+str(item.get('label') or n)) if p.suffix.lower()=='.xlsx' else ('Partie '+str(item.get('label') or n)) if p.suffix.lower() in {'.docx','.pptx'} else str(item.get('label') or f'Extrait {idx}')
                content += f'<section class="page" id="page-{n or idx}"><p class="eyebrow">{esc(label)} · {esc(item.get("method","Extraction"))}</p><pre>{esc(item.get("text",""))}</pre></section>'
        intro = '<p class="breadcrumb">'+link('Accueil',HOME,output)+' / '+esc(doc.get('number','Lecture') if doc else 'Lecture')+'</p>'
        intro += '<div class="actions back">'+link('Télécharger la source',path,output,'button secondary',True)+'</div>'
        intro += '<p class="note">Vue de lecture dérivée. La source est conservée sans modification. '+esc(doc.get('extraction_status','Lecture du fichier') if doc else 'Lecture du fichier')+'</p>'
        intro += '<details class="provenance"><summary>Emplacement et empreinte de la source</summary><p>'+esc(path)+'</p><p class="hash">SHA-256 : '+digest+'</p></details>'
        write(output,layout(title,intro+'<article>'+content+'</article>',output,reader=True))
    def toc_sections(case, source):
        result = ''
        for number,label,docs in section_lists[case]:
            result += f'<details id="section-{number}"><summary>{number} · {esc(label)} <span class="muted">({len(docs)})</span></summary><ul>'
            for doc in docs:
                result += '<li><span class="section-number">'+doc['number']+'</span>'+link(doc['title'],doc['reader'] if doc.get('reader') else doc['path'],source)+'<small>'+esc(doc['format'].upper()+' · '+doc['nature'])+'</small></li>'
            result += '</ul></details>'
        common = [d for d in documents if d['case']!=case and case in (d.get('cases') or [d['case']])]
        if common:
            number = f'{CASES.index(case)+1}.{len(section_lists[case])+1}'
            result += f'<details id="section-{number}"><summary>{number} · Pièces communes aux dossiers <span class="muted">({len(common)})</span></summary><p class="muted">Renvois vers les documents déjà classés dans un autre dossier; aucune copie ni montant supplémentaire.</p><ul>'
            for idx,doc in enumerate(sorted(common,key=lambda d:d['title'].casefold()),1):
                result += '<li><span class="section-number">'+number+'.'+str(idx)+'</span>'+link(doc['title'],doc.get('reader') or doc['path'],source)+'<small>Renvoi vers '+esc(doc['number']+' · '+doc['case'])+'</small></li>'
            result += '</ul></details>'
        return result
    for ci, case in enumerate(CASES):
        source = section_path(ci)
        body = f'<p class="eyebrow">{ci+1} · Dossier de travail</p><h1>{esc(case)}</h1><p class="intro">Table des matières des documents distincts. Les numéros organisent la lecture; les cotes d’annexes A001 à A312 restent inchangées dans la remise.</p>'
        body += '<div class="actions">'+f'<a class="button" href="{href(HOME,source)}?dossier={quote(case)}#recherche">Rechercher dans ce dossier</a>'+'</div>'
        if ci == 3:
            body += '<section class="panel accent"><h2>À remettre au cabinet</h2><div class="actions">'+link('Courriel prêt à compléter',MASTER+'/04_Remise_et_suivis/COURRIEL-DE-REMISE.md',source,'button')+link('Autorisation SPVM à signer',SPVM,source,'button secondary')+link('Demandes Abdel, huissier et Élite',MASTER+'/04_Remise_et_suivis/SUIVIS-ABDEL-HUISSIER-ELITE.md',source,'button secondary')+'</div><p>Préparé, non envoyé. Le nom et la qualité du signataire du courriel restent à compléter.</p></section>'
        if ci in (2,3): body += request_panel(source)
        body += '<section class="toc">'+toc_sections(case,source)+'</section>'
        write(source,layout(case,body,source))
    source = MASTER+'/05_Table_des_matieres/index.html'
    body = '<p class="eyebrow">Plan général</p><h1>Table des matières</h1><p class="intro">Dossier → rubrique → document. La numérotation sert de repère de navigation et ne remplace pas les cotes des pièces.</p><section class="toc">'
    for ci, case in enumerate(CASES): body += '<h2>'+link(f'{ci+1}. {case}',section_path(ci),source)+'</h2>'+toc_sections(case,source)
    body += '</section>'
    write(source,layout('Table des matières',body,source))
    # A separate compact data script avoids fetch/CORS failures when opened from OneDrive.
    out_docs = []
    for d in sorted(documents,key=lambda d:d['sort']):
        item = {k:d.get(k) for k in ('id','sha256','case','cases','title','path','aliases','format','pages','extraction_status','reader','number','sort','nature')}
        item['pages'] = [{k:p.get(k) for k in ('page','label','text','method')} for p in d.get('pages',[])]
        out_docs.append(item)
    scripts = []; chunk = []; size = 0
    def dump_chunk():
        path = MASTER+f'/06_Index_recherche/recherche-{len(scripts):03d}.js'
        prefix = 'window.MASTER_CHUNKS=window.MASTER_CHUNKS||[];window.MASTER_CHUNKS.push('
        write(path,prefix+json.dumps(chunk,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')+');')
        scripts.append(path)
    for d in out_docs:
        n = len(json.dumps(d,ensure_ascii=False).encode('utf-8'))
        if chunk and size+n>4_000_000: dump_chunk(); chunk=[]; size=0
        chunk.append(d); size+=n
    if chunk: dump_chunk()
    metadata = {'generated_at':corpus.get('generated_at',datetime.now(timezone.utc).isoformat()),'cases':CASES,'stats':corpus.get('stats',{})}
    meta_path = MASTER+'/06_Index_recherche/metadata.js'; write(meta_path,'window.MASTER_META='+json.dumps(metadata,ensure_ascii=False).replace('<','\\u003c')+';')
    body = home_body(documents,corpus)
    write(HOME,layout('Les trois dossiers et la remise',body,HOME,[meta_path,*scripts,MASTER+'/assets/search-core.js',MASTER+'/assets/app.js']))
    guide = MASTER+'/07_Controle_des_sources/index.html'
    coverage_md = MASTER+'/07_Controle_des_sources/COUVERTURE-EXTRACTION.md'
    coverage = (ROOT/coverage_md).read_text(encoding='utf-8-sig') if (ROOT/coverage_md).exists() else 'Le rapport de couverture est en cours de génération.'
    body = '<p class="eyebrow">Méthode et utilisation</p><h1>Travailler avec le dossier maître</h1><div class="flow"><section class="card"><h2>1. Ouvrir</h2><p>Commencer par OUVRIR-LES-DOSSIERS.html dans OneDrive, ou par la page d’accueil du site.</p></section><section class="card"><h2>2. Trouver</h2><p>Rechercher un nom, une facture ou une expression. Tous les mots sont recherchés; les guillemets conservent une expression. Les accents et la casse sont ignorés.</p></section><section class="card"><h2>3. Vérifier</h2><p>Lire l’extrait, ouvrir la pièce et vérifier la page. Les copies exactes sont regroupées; une facture révisée demeure à rapprocher de ses autres versions.</p></section><section class="card"><h2>4. Compléter</h2><p>Enregistrer les nouveaux originaux dans leur dossier thématique. L’index et le site doivent ensuite être régénérés; leur date reste affichée.</p></section></div><section class="panel"><h2>Lecture hors connexion et travail à distance</h2><p>Dans OneDrive, choisir « Toujours conserver sur cet appareil » pour ce dossier si vous devez travailler sans connexion. La page locale lit les fichiers voisins. Le site publie une copie datée; il n’est pas un éditeur partagé et ne synchronise pas automatiquement les modifications.</p><p>Les sous-dossiers existants contiennent les originaux. Les sections du maître sont des vues organisées pour éviter de multiplier les copies. Les courriels, déclarations, analyses et extractions restent identifiés. Les anciens index sont accessibles comme archives, mais leurs anciens champs interactifs ne servent pas à la recherche actuelle.</p></section><article>'+renderer.markdown(coverage,coverage_md)+'</article>'
    write(guide,layout('Méthode et couverture',body,guide))
    launcher = '<p class="eyebrow">Espace de travail OneDrive</p><h1>Votre dossier maître</h1><p class="intro">Les trois dossiers, la remise à Me Dufourd, les annexes et une recherche dans les textes disponibles.</p><div class="actions">'+link('Ouvrir le dossier maître',HOME,'OUVRIR-LES-DOSSIERS.html','button')+link('Table des matières',MASTER+'/05_Table_des_matieres/index.html','OUVRIR-LES-DOSSIERS.html','button secondary')+'</div><p>Commencez toujours par ce fichier. Les pièces et leurs emplacements d’origine sont conservés.</p>'
    write('OUVRIR-LES-DOSSIERS.html',layout('Ouvrir le dossier maître',launcher,'OUVRIR-LES-DOSSIERS.html'))
    removed = []
    for old, old_hash in previous.items():
        if old in written: continue
        target = ROOT/old
        if not target.resolve().is_relative_to((ROOT/MASTER).resolve()): continue
        if '..' in PurePosixPath(old).parts or target.is_symlink(): raise RuntimeError('Ancien chemin généré non autorisé')
        if target.is_file():
            if sha(target.read_bytes()) != old_hash: raise RuntimeError('Ancienne vue modifiée à conserver : '+old)
            target.unlink(); removed.append(old)
    manifest = {'generated_at':metadata['generated_at'],'document_count':len(documents),'reader_count':len(reader_sources),'data_chunks':len(scripts),'files':written,'unresolved_source_references':missing,'obsolete_generated_views_removed':removed,'rule':RULE}
    write(MASTER+'/07_Controle_des_sources/CONTROLE-DU-MAITRE.json',json.dumps(manifest,ensure_ascii=False,indent=2))
    print(json.dumps({'documents':len(documents),'readers':len(reader_sources),'chunks':len(scripts),'files':len(written),'missing_source_references':len(missing)},ensure_ascii=False))

def request_panel(source):
    rows = list(csv.DictReader((ROOT/REM/'SUIVI-DES-DEMANDES.csv').open(encoding='utf-8-sig',newline='')))
    annexes = {r['cote']: REM+r['fichier_remise'] for r in csv.DictReader((ROOT/REM/'BORDEREAU-DES-ANNEXES.csv').open(encoding='utf-8-sig',newline=''))}
    heads = re.findall(r'^### (Demande (\d+) .+)$',(ROOT/REM/'REPONSES-AUX-25-DEMANDES.md').read_text(encoding='utf-8-sig'),re.M)
    anchors = {n: re.sub(r'[^\w\- ]','',heading.lower()).replace(' ','-') for heading,n in heads}
    body = '<section class="panel accent"><p class="eyebrow">Remise à Me Dufourd · 25 demandes</p><h2>Réponses, annexes et points ouverts</h2><div class="actions">'+link('Réponses en PDF',REM+'REPONSES-AUX-25-DEMANDES.pdf',source,'button')+link('312 annexes — bordereau',REM+'BORDEREAU-DES-ANNEXES.md',source,'button secondary')+link('Télécharger le dossier ZIP',REM+'DOSSIER-DUFOURD-2026-10-21.zip',source,'button secondary')+'</div><p class="muted">État documentaire : 5 disponibles, 17 partiels, 3 non repérés. Les réponses du client et les documents effectivement obtenus sont distingués.</p><div class="toc">'
    for row in rows:
        n = row['numero']; body += f'<details id="demande-{n}"><summary>Demande {n} · {esc(row["statut_documentaire"])}</summary><p>{esc(row["demande"])}</p><p><strong>Annexes :</strong> '
        body += ' · '.join(link(cote,annexes[cote],source) if cote in annexes else esc(cote) for cote in row['annexes'].split('; '))+'</p>'
        for key,label in [('manquants','Reste à documenter'),('demarches','Démarches prévues')]:
            if row[key]: body += '<p><strong>'+label+' :</strong> '+esc(row[key])+'</p>'
        target = readers.get(REM+'REPONSES-AUX-25-DEMANDES.md',REM+'REPONSES-AUX-25-DEMANDES.md')
        body += '<a href="'+href(target,source)+'#'+quote(anchors.get(n,''))+'">Lire la réponse détaillée à cette demande</a></details>'
    return body+'</div></section>'

def home_body(documents,corpus):
    text_count = sum(any(p.get('text','').strip() for p in d.get('pages',[])) for d in documents)
    body = '<section class="hero"><p class="eyebrow">OneDrive · Espace de préparation pour l’avocat</p><h1>Tout le dossier,<br>un point de départ.</h1><p class="intro">Retrouver une pièce, suivre les 25 demandes et préparer la remise. Une navigation commune pour Léger, Somerled et Harmony Movers.</p><div class="stats"><div class="stat"><strong>'+str(len(documents))+'</strong><span>documents distincts indexés</span></div><div class="stat"><strong>'+str(text_count)+'</strong><span>avec du texte exploitable</span></div><div class="stat"><strong>312</strong><span>annexes dans la remise</span></div></div></section><section class="grid" aria-label="Les trois dossiers">'
    descriptions = ['Assurance, chronologie, équipements, dommages et correspondance.','Propriétaire, échanges, mises en demeure et pièces du litige.','Déménagement, factures, constats, 25 demandes et annexes.']
    for i,case in enumerate(CASES[:3]):
        count = sum(case in (d.get('cases') or [d['case']]) for d in documents)
        body += f'<article class="card"><span class="number">0{i+1} / {count} documents</span><h2>{esc(case)}</h2><p>{descriptions[i]}</p>'+link('Ouvrir la table du dossier →',section_path(i),HOME)+'</article>'
    body += '</section><section class="panel accent"><p class="eyebrow">04 / Remise et suivis</p><h2>Le dossier à remettre à Me Dufourd</h2><p>Courriel préparé, autorisation SPVM à signer, demandes de pièces à Abdel, à l’huissier et à Élite.</p><div class="actions">'+link('Préparer la remise',section_path(3),HOME,'button')+link('Réponses aux 25 demandes',REM+'REPONSES-AUX-25-DEMANDES.pdf',HOME,'button secondary')+link('Autorisation SPVM',SPVM,HOME,'button secondary')+'</div><p class="muted">Préparé, non envoyé. Les pièces manquantes et les vérifications ouvertes restent indiquées.</p></section>'
    body += '<section class="panel" id="recherche"><p class="eyebrow">Recherche dans les pièces et les textes disponibles</p><h2>Retrouver un passage</h2><p id="index-status" class="status">Chargement de l’index local…</p><p id="loading">Chargement des textes. Si ce message persiste, ouvrir le dossier complet avec les sous-dossiers assets et 06_Index_recherche disponibles sur cet appareil.</p><noscript><p>La recherche nécessite JavaScript. La table des matières et les documents restent accessibles par les liens de navigation.</p></noscript><form id="search-form" hidden><label for="query">Nom, numéro de facture, mot-clé ou expression entre guillemets</label><div class="search-row"><input id="query" type="search" placeholder="Ex. Daniel Simard, Frigospec, MTLEV2500487177…" autocomplete="off"><button type="submit">Rechercher</button><button id="clear" type="button" class="secondary">Effacer</button></div><div class="filters"><div><label for="case-filter">Dossier</label><select id="case-filter"><option value="">Tous les dossiers</option></select></div><div><label for="format-filter">Type de fichier</label><select id="format-filter"><option value="">Tous les formats</option></select></div></div></form><div class="chips"><button type="button" data-query="Daniel Simard">Daniel Simard</button><button type="button" data-query="Frigospec">Frigospec</button><button type="button" data-query="SPVM">SPVM</button><button type="button" data-query="Abdel">Abdel</button><button type="button" data-query="Racine Chamberland">Racine Chamberland</button></div><p class="muted">Tous les mots doivent être présents. Les accents et la casse sont ignorés. Les images et pages sans texte peuvent n’être trouvées que par leur nom; l’OCR reste à contrôler sur l’original.</p><p id="result-count" class="result-count" aria-live="polite"></p><div id="results"></div><p id="empty" hidden>Aucun résultat dans cette sélection. Essayer un mot plus court, retirer un filtre ou consulter la table des matières.</p><button id="more" type="button" hidden>Afficher les résultats suivants</button></section>'
    body += '<section class="grid"><article class="card"><p class="eyebrow">05 / Navigation</p><h2>Table générale</h2><p>Repères 1.1, 1.2 et sous-rubriques. Les cotes des annexes restent conservées.</p>'+link('Parcourir tous les dossiers',MASTER+'/05_Table_des_matieres/index.html',HOME)+'</article><article class="card"><p class="eyebrow">06 / Recherche</p><h2>Textes disponibles</h2><p>Les originaux PDF, les courriels et les documents de travail sont reliés à leurs extractions.</p><a href="#recherche">Chercher dans le contenu</a></article><article class="card"><p class="eyebrow">07 / Contrôle</p><h2>Sources et limites</h2><p>Consulter la couverture d’extraction et savoir comment ajouter de nouvelles pièces.</p>'+link('Mode d’emploi et couverture',MASTER+'/07_Controle_des_sources/index.html',HOME)+'</article></section>'
    return body

if __name__ == '__main__': main()
