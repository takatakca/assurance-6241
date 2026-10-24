"""Assemble les réponses documentaires sans modifier les sources ni envoyer de message."""
from pathlib import Path
import csv, hashlib, html, json, re, shutil, sys, zipfile
from collections import Counter, defaultdict
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / 'scripts/remise-dufourd'
OUT = ROOT / 'HARMONY MOVERS/12_Remise_Dufourd_2026-10-21'
DATE = '21 octobre 2026'
COMMON = 'Les originaux, les déclarations et les analyses sont identifiés par leur provenance. Les doublons et les versions d’une facture ne s’additionnent pas. Une extraction OCR reste à contrôler sur la pièce originale. Les documents à obtenir et les vérifications ouvertes figurent dans les synthèses de chaque dossier.'
LABELS = {'document_disponible':'Document demandé disponible', 'partiel':'Pièces disponibles en partie', 'non_repere':'Document non repéré', 'a_confirmer':'Existence ou portée à confirmer'}
REQUESTS = [
'Produire une copie de votre curriculum vitae.',
'Produire toutes les communications entre vous-même, M. Lévesque et M. Constantino envers la défenderesse concernant le déménagement;',
'Produire tout titre de propriété ou document d’acquisition établissant la propriété des équipements.',
'Produire les états financiers de Quadro reflétant la valeur des équipements inscrite aux livres.',
'Produire les factures, soumissions, déclarations d’experts et toute autre documentation concernant l’entretien et le service des équipements.',
'Produire le contrat de location conclu avec U-Haul. Il n’y a en a pas si je comprends bien.',
'Produire les factures et les preuves de paiement relatives à tout contrat conclu avec la société ayant transigé avec Quadro dans le cadre de la location du véhicule U-Haul.',
'Produire toutes les communications, y compris les messages textes, entre Quadro et la partie défenderesse, qu’elles proviennent de vous-même, de Monsieur Levesque ou de Monsieur Constantino.',
'Produire la liste des équipements chargés dans le véhicule U-Haul.',
'Indiquer le lieu d’entreposage des équipements.',
'Produire le contrat de bail relatif à l’entreposage des équipements ainsi que le contrat relatif à l’utilisation du chariot élévateur.',
'Produire le bail ou tout document établissant le droit d’occupation des lieux situés au 5837, rue Jean-Talon Est.',
'Produire les contrats conclus avec DoorDash, Uber Eats, Sky et Descheuse, ainsi que tous les relevés relatifs à ces entreprises.',
'Produire les rapports de caisse ainsi que les déclarations de TPS et de TVQ pour les années 2024 et 2025.',
'Produire une copie des photos envoyées avant le déménagement ainsi que toute liste des équipements préparée avant le déménagement, le cas échéant.',
'Produire le contrat conclu avec le gardien relativement à l’entreposage actuel des équipements.',
'Produire la documentation de Tezanet concernant l’évaluation des équipements.',
'Produire les vidéos et les photos prises par l’huissier, dans la mesure où elles sont en votre possession.',
'Produire la carte remise par les policiers indiquant le numéro du rapport relatif à leur intervention.',
'Fournir le formulaire d’autorisation d’accès dûment signé permettant aux avocats d’obtenir le rapport de police.',
'Produire une copie de la police d’assurance de QH couvrant les biens concernés.',
'Produire le dossier transmis à l’assureur ainsi que la réponse de celui-ci.',
'Produire tous les documents justifiant la perte d’exploitation réclamée.',
'Produire toutes les communications et tous les documents relatifs au mandat confié à Remorquage Élite pour le déménagement résiduel.',
'Produire l’échange complet avec l’autre partie, y compris la réponse de celle-ci.'
]
TITLES = ['Curriculum vitae','Communications sur le déménagement','Propriété des équipements','Valeur comptable des équipements','Entretien et service','Contrat de location U Haul','Prestataire du véhicule U Haul','Communications et messages textes','Équipements chargés dans le U Haul','Lieu d’entreposage','Bail et utilisation du chariot élévateur','Occupation du 5837 Jean Talon Est','Contrats et relevés des plateformes','Caisse et déclarations TPS TVQ','Photos et listes avant le déménagement','Contrat avec le gardien','Évaluation Tezanet','Photos et vidéos de l’huissier','Carte de police','Autorisation pour le rapport de police','Police d’assurance','Dossier et réponse de l’assureur','Perte d’exploitation','Mandat Remorquage Élite','Échange complet avec l’autre partie']
BASE = [
('HARMONY MOVERS/03_Courriels/takatak.ca@gmail.com/Textes/1a10d5436a58b8f3.txt','Liste écrite des 25 demandes du 5 octobre 2026','extraction'),
('HARMONY MOVERS/03_Courriels/Originaux_ooeuf_2026-10-20/2026-10-20_1420_Christian_Dufourd_honoraires.eml','Demande du cabinet du 20 octobre à 14 h 20','original'),
('HARMONY MOVERS/03_Courriels/Originaux_ooeuf_2026-10-20/2026-10-20_1629_Christian_Dufourd.eml','Réponses du cabinet du 20 octobre à 16 h 29','original'),
('HARMONY MOVERS/11_Fieldy/2026-10-05-Fieldy-interrogatoire-Quadro-Harmony.pdf','Export Fieldy de 79 pages et transcription automatique brute','original'),
('HARMONY MOVERS/11_Fieldy/CONTROLE-ENGAGEMENTS-FIELDY.md','Concordance du courriel et de la transcription Fieldy','analyse'),
('HARMONY MOVERS/11_Fieldy/ANALYSE-FIELDY-POUR-CABINET.md','Analyse documentaire de la transcription Fieldy','analyse'),
('HARMONY MOVERS/11_Fieldy/acquisition-pdf.json','Provenance et empreinte de l’export Fieldy','analyse'),
('HARMONY MOVERS/07_Assurance_et_etat_anterieur/Collecte_2026-10-21/PROVENANCE-SNB.json','Provenance et contrôle visuel de la lettre SNB du 4 août 2026','analyse')]
BASE += [
('HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md','Bilan de la recherche complémentaire du 21 octobre 2026 et évolution des demandes','analyse'),
('HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_Ooeuf/PROVENANCE-OOEUF.json','Provenance et empreintes des pièces natives récupérées dans Ooeuf','analyse'),
('HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_ChatGPT/ANALYSE-NOUVEAUX-RAPPORTS-HUISSIER.md','Contrôle des rapports de saisie et du procès-verbal signé nouvellement acquis','analyse')]

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def jwrite(p, data): p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n',encoding='utf-8')
def s(v): return str(v or '').strip()
def source_path(value):
    p = (ROOT / s(value).replace('\\','/')).resolve()
    if not p.is_relative_to(ROOT) or not p.is_file(): raise ValueError('Source absente ou hors dossier : '+s(value))
    return p
def load_rows():
    rows=[]
    for name in ['audit-communications','audit-pieces','audit-finances']:
        data=json.loads((AUDITS/(name+'.json')).read_text(encoding='utf-8-sig'))
        if isinstance(data,dict): data=data.get('demandes',data.get('engagements',data.get('rows')))
        rows.extend(data)
    rows.sort(key=lambda x:int(x['id']))
    if [int(x['id']) for x in rows] != list(range(1,26)): raise ValueError('Il faut exactement les 25 demandes, sans doublon')
    for r in rows:
        r['id']=int(r['id']); r['demande_originale']=REQUESTS[r['id']-1]; r['titre']=TITLES[r['id']-1]
        if r['statut'] not in LABELS: raise ValueError('Statut inconnu '+r['statut'])
        if not s(r['reponse_proposee']): raise ValueError('Réponse vide')
        for key in ['pieces','manquants','demarches','controles','recherche_effectuee']: r.setdefault(key,[])
        for p in r['pieces']: source_path(p['path'])
    return rows

def load_annexe_registry():
    """Réutilise les cotes publiées et refuse toute divergence avant allocation."""
    manifest=OUT/'BORDEREAU-DES-ANNEXES.json'
    annex_dir=(OUT/'ANNEXES').resolve()
    if not manifest.exists():
        if annex_dir.exists() and any(annex_dir.iterdir()):
            raise ValueError('ANNEXES existe sans bordereau : allocation interrompue pour préserver les cotes')
        return {},0
    previous=json.loads(manifest.read_text(encoding='utf-8-sig'))
    if not isinstance(previous,list): raise ValueError('Bordereau antérieur invalide')
    byhash={}; used_ids=set(); used_paths=set(); highest=0
    for prior in previous:
        entry=dict(prior)
        ident=s(entry.get('id')); digest=s(entry.get('sha256')).lower()
        match=re.fullmatch(r'A(\d{3,})',ident)
        if not match or int(match.group(1))<1 or ident in used_ids:
            raise ValueError('Cote antérieure invalide ou répétée : '+ident)
        if not re.fullmatch(r'[a-f0-9]{64}',digest) or digest in byhash:
            raise ValueError('Empreinte antérieure invalide ou répétée : '+ident)
        relative=Path(s(entry.get('fichier')).replace('\\','/'))
        dst=(OUT/relative).resolve()
        if not dst.is_relative_to(annex_dir) or not dst.name.startswith(ident+'__') or dst in used_paths:
            raise ValueError('Chemin d’annexe antérieure invalide : '+ident)
        if not dst.is_file() or sha(dst)!=digest:
            raise ValueError('Annexe antérieure absente ou modifiée : '+ident)
        if sha(source_path(entry.get('source')))!=digest:
            raise ValueError('Source antérieure modifiée : '+ident)
        entry['sha256']=digest
        entry['copies_identiques']=list(entry.get('copies_identiques',[]))
        entry['demandes']=[]  # Les références de la nouvelle version sont recalculées.
        entry['utilisee_dans_version_courante']=False
        byhash[digest]=entry; used_ids.add(ident); used_paths.add(dst)
        highest=max(highest,int(match.group(1)))
    # Les anciennes annexes restent inscrites même si une réponse ne les cite plus.
    return byhash,highest

def annexes(rows):
    byhash,highest=load_annexe_registry(); bypath={}
    entries=[{'path':p,'apport':a,'nature':n,'demande':None} for p,a,n in BASE]
    entries += [dict(p,demande=r['id']) for r in rows for p in r['pieces']]
    for item in entries:
        src=source_path(item['path']); relative=src.relative_to(ROOT).as_posix(); digest=sha(src)
        if digest not in byhash:
            highest+=1
            ident=f'A{highest:03d}'
            basename=re.sub(r'[^\w. -]+','_',src.stem,flags=re.UNICODE).strip(' .')[:66]
            # Les analyses sont conservées octet pour octet comme texte autonome;
            # leurs liens relatifs ne doivent pas être réinterprétés dans ANNEXES.
            suffix='.txt' if src.suffix.lower() in ['.md','.html','.htm'] else src.suffix.lower()
            dst=f'ANNEXES/{ident}__{basename}{suffix}'
            byhash[digest]={'id':ident,'fichier':dst,'source':relative,'copies_identiques':[], 'sha256':digest,'octets':src.stat().st_size,'nature':s(item.get('nature')),'demandes':[], 'description':s(item.get('apport'))}
        entry=byhash[digest]
        entry['utilisee_dans_version_courante']=True
        if relative!=entry['source'] and relative not in entry['copies_identiques']: entry['copies_identiques'].append(relative)
        if item['demande'] and item['demande'] not in entry['demandes']: entry['demandes'].append(item['demande'])
        bypath[relative]=entry
    for r in rows:
        for p in r['pieces']:
            entry=bypath[source_path(p['path']).relative_to(ROOT).as_posix()]
            p.update(annexe=entry['id'],fichier_remise=entry['fichier'])
    return sorted(byhash.values(),key=lambda a:int(a['id'][1:]))

def write_csv(path,fields,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)

def write_texts(rows,ann):
    counts=Counter(r['statut'] for r in rows)
    intro=[f'# Réponses documentaires aux 25 demandes de Me Dufourd',f'\nQuadro Holdings ltée et Harmony Movers — État du {DATE}.', '\nCe dossier prépare la remise au cabinet des documents disponibles pour chacune des 25 demandes du 5 octobre, réitérées le 20 octobre 2026. Les réponses ci-dessous s’appuient sur les pièces annexées. Les documents absents ou incomplets sont indiqués séparément. **Dossier préparé, non envoyé.**', '\nLes références A001 et suivantes sont des cotes de classement internes. Une annexe n’est conservée qu’une fois lorsque ses octets sont identiques; elle peut servir à plusieurs demandes. La disponibilité d’une pièce ne vaut ni confirmation de réception par le cabinet, ni reconnaissance que l’engagement est satisfait.', '\n'+COMMON, '\n## État des réponses', '\n| Statut documentaire | Nombre |','|---|---:|']
    intro += [f'| {LABELS[k]} | {counts[k]} |' for k in LABELS if counts[k]]
    intro += ['\nLes statuts portent sur les documents demandés, sans jugement sur leur force probante. Le cabinet pourra préciser la portée des engagements, notamment l’écart entre le n° 8 écrit et l’E9 oral, ainsi que la réserve relative à certains échanges internes.', '\nLa transcription Fieldy demeure automatique, avec locuteurs non identifiés et audio absent. Son usage est celui d’un repérage par page et heure; elle ne remplace pas les notes officielles.', '\n## Réponses par demande']
    md='\n'.join(intro)+'\n'
    missing=['# Documents manquants et démarches ciblées',f'\nÉtat du {DATE}. Les personnes ou organismes mentionnés sont des détenteurs à confirmer; aucune demande ne leur a été envoyée.']
    for r in rows:
        md += f"\n### Demande {r['id']} — {r['titre']}\n\n**Demande du cabinet :** {r['demande_originale']}\n\n**État : {LABELS[r['statut']]}.** Transmission de ce dossier non effectuée.\n\n{r['reponse_proposee']}\n\n**Pièces jointes à cette réponse**\n\n"
        if not r['pieces']: md+='Aucune annexe répondant directement à cette demande n’a été identifiée dans la recherche décrite.\n'
        for p in r['pieces']:
            repere='; '.join(filter(None,[('page(s) '+s(p.get('pages'))) if p.get('pages') else '',s(p.get('repere'))]))
            md+=f"- [{p['annexe']}]({quote(p['fichier_remise'])}) — {p['apport']}"+(f" Repère : {repere}." if repere else '')+f" Nature : {s(p.get('nature'))}.\n"
        for title,key in [('Ce qui manque','manquants'),('Démarches proposées','demarches'),('Réserves et contrôles','controles')]:
            md+=f'\n**{title}**\n\n'
            md+='\n'.join('- '+s(v) for v in r[key])+'\n' if r[key] else 'Aucun élément supplémentaire identifié pour cette rubrique dans les limites du contrôle décrit.\n'
        md+='\n**Périmètre de recherche**\n\n'+'; '.join(s(v) for v in r['recherche_effectuee'])+'.\n'
        if r['manquants']:
            missing += [f"\n## Demande {r['id']} {r['titre']}", '\n'+ '\n'.join('- '+s(v) for v in r['manquants']), '\n**Action ciblée**\n', '\n'.join('- '+s(v) for v in r['demarches'])]
    (OUT/'REPONSES-AUX-25-DEMANDES.md').write_text(md,encoding='utf-8')
    (OUT/'DOCUMENTS-A-OBTENIR.md').write_text('\n'.join(missing)+'\n',encoding='utf-8')
    jwrite(OUT/'SUIVI-DES-DEMANDES.json',rows)
    write_csv(OUT/'SUIVI-DES-DEMANDES.csv',['numero','demande','statut_documentaire','annexes','manquants','demarches','transmission'],[{'numero':r['id'],'demande':r['demande_originale'],'statut_documentaire':LABELS[r['statut']],'annexes':'; '.join(dict.fromkeys(p['annexe'] for p in r['pieces'])),'manquants':' | '.join(r['manquants']),'demarches':' | '.join(r['demarches']),'transmission':'non envoyée'} for r in rows])
    jwrite(OUT/'BORDEREAU-DES-ANNEXES.json',ann)
    write_csv(OUT/'BORDEREAU-DES-ANNEXES.csv',['cote','fichier_remise','nature','demandes','apport','source_originale','copies_identiques','octets','sha256'],[{'cote':a['id'],'fichier_remise':a['fichier'],'nature':a['nature'],'demandes':'; '.join(map(str,a['demandes'])),'apport':a['description'],'source_originale':a['source'],'copies_identiques':' | '.join(a['copies_identiques']),'octets':a['octets'],'sha256':a['sha256']} for a in ann])
    b='# Bordereau des annexes\n\nLes cotes sont internes au dossier de remise. Les empreintes complètes et les emplacements sources figurent dans les fichiers CSV et JSON.\n\n| Cote | Document | Nature | Demandes |\n|---|---|---|---|\n'
    for a in ann: b+=f"| {a['id']} | [{Path(a['source']).name.replace('|',' ')}]({quote(a['fichier'])}) | {a['nature']} | {', '.join(map(str,a['demandes'])) or 'Contexte'} |\n"
    (OUT/'BORDEREAU-DES-ANNEXES.md').write_text(b,encoding='utf-8')
    mail=f'''# Projet de courriel de remise

Projet à relire par le client avant envoi. Aucun courriel n’a été envoyé.

**Destinataire proposé :** Me Christian Dufourd, cdufourd@dufourdion.com.

**Objet proposé :** Quadro Holdings ltée — Réponses documentaires aux 25 demandes du 5 octobre 2026

Maître,

Le dossier préparé en réponse à vos demandes des 5 et 20 octobre 2026 comprend une réponse numérotée pour chacun des 25 engagements, un bordereau de {len(ann)} annexes distinctes et la liste précise des documents restant à obtenir.

Les pièces disponibles sont reliées aux demandes correspondantes. Les réponses distinguent les documents retrouvés, les déclarations rapportées et les analyses. Les factures successives et les copies identiques ne sont pas additionnées.

Le PDF Fieldy de 79 pages est inclus, avec sa concordance par page et heure. Il s’agit d’une transcription automatique; l’audio et les notes sténographiques officielles restent à rapprocher. La portée du n° 8 de votre liste diffère de l’E9 oral, et une réserve concernant certains échanges internes apparaît dans la transcription. Ces points sont signalés pour votre examen.

Merci de confirmer les pièces que votre cabinet détient déjà, celles permettant de répondre aux engagements selon leur portée exacte, et les compléments prioritaires. Les démarches restant à organiser comprennent les pièces manquantes, les expertises et les médias de saisie indiqués dans votre courriel du 20 octobre.

Ce dossier ne confirme pas que toutes les pièces demandées ont été obtenues. Les disponibilités et démarches proposées sont indiquées sans annoncer une production non réalisée. Merci de confirmer la réception effective des fichiers remis et de signaler toute pièce illisible ou absente.

Salutations distinguées,

[Nom et qualité du signataire à compléter]

Avant envoi : joindre les fichiers du dossier ou insérer le lien de remise retenu; vérifier le destinataire et compléter la signature. Le présent projet ne contient aucun accord sur des honoraires, un règlement ou un changement de représentation.
'''
    (OUT/'PROJET-COURRIEL-DE-REMISE.md').write_text(mail,encoding='utf-8')

def make_pdf(rows,ann):
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether
    pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
    pdfmetrics.registerFont(TTFont('Arial-Bold','C:/Windows/Fonts/arialbd.ttf'))
    pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='Arial-Bold',italic='Arial',boldItalic='Arial-Bold')
    styles=getSampleStyleSheet()
    for name in ['Normal','BodyText','Title','Heading1','Heading2','Heading3']:
        styles[name].fontName='Arial-Bold' if name in ['Title','Heading1','Heading2','Heading3'] else 'Arial';styles[name].textColor=colors.black
    styles['Normal'].fontSize=10;styles['Normal'].leading=14;styles['Normal'].spaceAfter=7
    styles['Normal'].allowWidows=0;styles['Normal'].allowOrphans=0
    styles['Title'].fontSize=21;styles['Title'].leading=26;styles['Title'].alignment=0;styles['Title'].spaceAfter=18
    styles['Heading1'].fontSize=15;styles['Heading1'].leading=19;styles['Heading1'].spaceAfter=12
    styles['Heading2'].fontSize=11;styles['Heading2'].leading=15;styles['Heading2'].spaceBefore=9;styles['Heading2'].spaceAfter=5
    for name in ['Title','Heading1','Heading2','Heading3']: styles[name].keepWithNext=True
    styles.add(ParagraphStyle('Small',parent=styles['Normal'],fontSize=8.5,leading=11,spaceAfter=5))
    styles.add(ParagraphStyle('Cell',parent=styles['Normal'],fontSize=8.5,leading=11,spaceAfter=0))
    styles.add(ParagraphStyle('CellHeader',parent=styles['Cell'],fontName='Arial-Bold',textColor=colors.white))
    esc=lambda x:html.escape(s(x).replace('—','-').replace('–','-').replace('\u2011','-').replace('..','.').replace('.;',';')).replace('\n','<br/>')
    P=lambda txt,style='Normal':Paragraph(esc(txt),styles[style])
    story=[P('Réponses documentaires aux 25 demandes','Title'),P('Quadro Holdings ltée et Harmony Movers','Heading1'),P('Pour Me Christian Dufourd\nÉtat du '+DATE),P('Ce dossier réunit les réponses préparées aux 25 demandes du 5 octobre 2026 et les documents disponibles. Chaque réponse indique ses annexes, ce qui manque et les démarches ciblées. Dossier préparé, non envoyé.'),P(f'{len(ann)} annexes distinctes accompagnent ce document. Les cotes A001 et suivantes sont des références internes; une même annexe peut soutenir plusieurs réponses. Le bordereau CSV et JSON précise les emplacements sources et les empreintes SHA256.'),P(COMMON),P('Statut des documents','Heading2')]
    counts=Counter(r['statut'] for r in rows)
    for k in LABELS:
        if counts[k]:story.append(P(f'{LABELS[k]} : {counts[k]} demande(s).'))
    story += [P('La disponibilité d’un document est distincte de sa transmission, de son acceptation et de sa valeur probante. Les statuts ci-dessus ne certifient pas que les engagements sont juridiquement satisfaits.'),P('Points de portée à faire confirmer','Heading2'),P('La liste écrite du cabinet conserve sa numérotation. Le n° 8 écrit vise la défenderesse, tandis que l’E9 oral vise la compagnie ayant engagé le U-Haul. La réserve évoquée pour certains échanges internes est conservée. Le cabinet doit confirmer le périmètre attendu.'),P('L’export Fieldy contient du texte automatique et des locuteurs étiquetés Unknown. L’audio et les notes officielles ne sont pas acquis. Les conversations avant séance, pendant la pause et après son arrêt sont distinguées dans les analyses annexées.'),PageBreak(),P('Repères des 25 réponses','Heading1')]
    table=[[P('N°','CellHeader'),P('Demande','CellHeader'),P('État documentaire','CellHeader')]]
    for r in rows:table.append([P(r['id'],'Cell'),P(r['titre'],'Cell'),P(LABELS[r['statut']],'Cell')])
    t=Table(table,colWidths=[28,265,209],repeatRows=1,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#263B46')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F4F5F6')]),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D9D9')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]));story.append(t)
    for r in rows:
        story += [PageBreak(),P(f"Demande {r['id']} {r['titre']}",'Heading1'),P('Demande du cabinet','Heading2'),P(r['demande_originale']),P(LABELS[r['statut']]+' — Transmission non effectuée.','Small'),P('Réponse proposée','Heading2'),P(r['reponse_proposee']),P('Pièces disponibles jointes','Heading2')]
        if not r['pieces']:story.append(P('Aucune annexe répondant directement à cette demande n’a été identifiée.'))
        for p in r['pieces']:
            marker='; '.join(filter(None,[('page(s) '+s(p.get('pages'))) if p.get('pages') else '',s(p.get('repere'))]))
            story.append(P(p['annexe']+' — '+s(p['apport'])+((' Repère : '+marker+'.') if marker else '')+' Nature : '+s(p.get('nature'))+'.','Small'))
        for title,key in [('Ce qui manque','manquants'),('Démarches proposées','demarches'),('Réserves et contrôles','controles')]:
            story.append(P(title,'Heading2'))
            story.extend(P('• '+s(x)) for x in r[key]) if r[key] else story.append(P('Aucun élément supplémentaire identifié pour cette rubrique dans les limites du contrôle décrit.'))
        story += [P('Périmètre de recherche','Heading2'),P('; '.join(s(x) for x in r['recherche_effectuee']),'Small')]
    story += [PageBreak(),P('Bordereau des annexes','Heading1'),P('Les noms de fichiers courts ci-dessous correspondent aux fichiers du sous-dossier ANNEXES. Les CSV et JSON conservent aussi les chemins sources complets, les copies identiques et les empreintes.')]
    for a in ann:
        story.append(KeepTogether([P(a['id']+' '+Path(a['fichier']).name,'Heading2'),P(a['description'],'Small'),P('Nature : '+a['nature']+' — Demandes : '+(', '.join(map(str,a['demandes'])) or 'Contexte')+' — '+str(a['octets'])+' octets.','Small')]))
    def footer(canvas,doc):
        canvas.setFont('Arial',8);canvas.setFillColor(colors.HexColor('#555555'));canvas.drawString(55,28,'Quadro Holdings ltée — Dossier préparé pour Me Dufourd — '+DATE);canvas.drawRightString(557,28,str(doc.page))
    path=OUT/'REPONSES-AUX-25-DEMANDES.pdf'
    SimpleDocTemplate(str(path),pagesize=letter,rightMargin=55,leftMargin=55,topMargin=50,bottomMargin=48,title='Réponses documentaires aux 25 demandes de Me Dufourd',author='Dossier Quadro Holdings').build(story,onFirstPage=footer,onLaterPages=footer)

def finish(rows,ann):
    counts=dict(Counter(r['statut'] for r in rows))
    controls={'date':'2026-10-21','demandes':len(rows),'statuts':counts,'annexes_uniques':len(ann),'octets_annexes':sum(a['octets'] for a in ann),'copies_identiques_non_dupliquees':sum(len(a['copies_identiques']) for a in ann),'originaux_modifies':False,'courriel_envoye':False,'sha_erreurs':[],'pdf_controle_visuel':'à effectuer avant livraison'}
    for a in ann:
        if sha(OUT/a['fichier'])!=a['sha256'] or sha(source_path(a['source']))!=a['sha256']:controls['sha_erreurs'].append(a['id'])
    if controls['sha_erreurs']:raise ValueError('Empreinte divergente')
    jwrite(OUT/'CONTROLES-DU-DOSSIER.json',controls)
    readme=f'''# Dossier de remise à Me Christian Dufourd

État du {DATE}. **Préparé, non envoyé.** Les 25 demandes ont une réponse documentaire individualisée, avec les pièces disponibles et les manquants précis. Le dossier ne certifie pas que tous les engagements sont satisfaits.

1. Lire les [réponses en PDF](REPONSES-AUX-25-DEMANDES.pdf) ou la [version en ligne](REPONSES-AUX-25-DEMANDES.md).
2. Consulter le [bordereau des {len(ann)} annexes](BORDEREAU-DES-ANNEXES.md), avec [empreintes et chemins sources CSV](BORDEREAU-DES-ANNEXES.csv).
3. Compléter les [documents encore à obtenir](DOCUMENTS-A-OBTENIR.md) et suivre les [25 demandes dans le tableau CSV](SUIVI-DES-DEMANDES.csv).
4. Relire et compléter le [projet de courriel de remise](PROJET-COURRIEL-DE-REMISE.md), notamment le nom et la qualité du signataire.

Les annexes sont des copies binaires des sources, dédupliquées par SHA256 et classées sous des noms courts. Une source peut servir à plusieurs demandes. Les extraits et analyses restent identifiés par leur nature; ils ne remplacent pas les originaux qui y sont cités. Les liens des analyses anciennes renvoient à leur classement d’origine; les annexes physiques et le bordereau font foi pour le contenu de cette remise.

{COMMON}

Les frais d’avocat et la gestion du mandat demeurent distincts de la réponse aux engagements. La préparation du dossier ne constitue ni paiement ni acceptation d’une offre de règlement. La date et la preuve d’une éventuelle transmission devront être enregistrées après l’envoi réel.
'''
    (OUT/'LIRE-EN-PREMIER.md').write_text(readme,encoding='utf-8')
    print(json.dumps(controls,ensure_ascii=False))

def build():
    rows=load_rows();ann=annexes(rows)
    if '--validate-only' in sys.argv:
        print(json.dumps({'demandes':len(rows),'annexes':len(ann),'octets':sum(a['octets'] for a in ann),'statuts':dict(Counter(r['statut'] for r in rows))},ensure_ascii=False));return
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'ANNEXES').mkdir(exist_ok=True)
    for a in ann:
        src=source_path(a['source']);dst=OUT/a['fichier']
        if not dst.exists():shutil.copyfile(src,dst)
        elif sha(dst)!=a['sha256']:raise ValueError('Annexe existante différente '+a['id'])
    write_texts(rows,ann);make_pdf(rows,ann);finish(rows,ann)

if __name__=='__main__':build()
