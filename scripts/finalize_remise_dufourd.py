"""Valide la remise, actualise la matrice puis crée l'archive documentaire autonome."""
from pathlib import Path
import csv, hashlib, io, json, zipfile
from pypdf import PdfReader
from build_remise_dufourd import ROOT, OUT, LABELS, sha, jwrite

rows=json.loads((OUT/'SUIVI-DES-DEMANDES.json').read_text(encoding='utf-8'))
ann=json.loads((OUT/'BORDEREAU-DES-ANNEXES.json').read_text(encoding='utf-8'))
pdf=OUT/'REPONSES-AUX-25-DEMANDES.pdf'
qa=json.loads((ROOT/'scripts/remise-dufourd/controle-visuel.json').read_text(encoding='utf-8'))
pages=len(PdfReader(pdf).pages)
assert qa['pdf_sha256']==sha(pdf), 'Contrôle visuel correspondant au PDF final requis'
assert sorted(qa['pages_revisees'])==list(range(1,pages+1)) and not qa['defauts_restants']
assert len(rows)==25 and len({r['id'] for r in rows})==25
assert len(ann)==len({a['sha256'] for a in ann})
for a in ann:
    assert sha(OUT/a['fichier'])==sha(ROOT/a['source'])==a['sha256'],a['id']

# La matrice de consultation reprend le dernier état documenté.
matrix=ROOT/'HARMONY MOVERS/01_Synthese_et_chronologie/ENGAGEMENTS-DUFOURD.md'
base='../12_Remise_Dufourd_2026-10-21/'
md='# Matrice des 25 demandes de Me Christian Dufourd\n\nÉtat documentaire du 21 octobre 2026. **Réponses préparées, non envoyées.** Une pièce disponible ne confirme ni sa réception par le cabinet ni l’accomplissement juridique de l’engagement.\n\n'
md+=f'[Dossier complet et archive à remettre]({base}LIRE-EN-PREMIER.md) · [Réponses PDF]({base}REPONSES-AUX-25-DEMANDES.pdf) · [Documents à obtenir]({base}DOCUMENTS-A-OBTENIR.md)\n\n'
md+='Source de numérotation : courriel du 5 octobre 2026, réitéré le 20 octobre. Les références orales Fieldy sont rapprochées séparément, notamment le n° 8 écrit et l’E9 oral.\n\n| N° | Demande | État documentaire | Annexes | Complément précis |\n|---|---|---|---|---|\n'
for r in rows:
    ids=', '.join(dict.fromkeys(p['annexe'] for p in r['pieces'])) or 'Aucune'
    missing=' ; '.join(r['manquants']).replace('|','/') or 'Aucun complément nécessaire pour la carte demandée; rapport de police et autorisation relèvent de documents distincts.'
    md+=f"| {r['id']} | {r['titre']} | {LABELS[r['statut']]} | {ids} | {missing} |\n"
md+='\nContrôles ayant corrigé le classement antérieur : H01/H02 sont des captures de courriel procédural; les images de factures alimentaires ne sont pas le lot de photos d’équipements annoncé. La carte de police porte MTLEV2500487177. La lettre SNB du 4 août 2026 est jointe à la nouvelle remise. Les contrats, pièces comptables et confirmations encore nécessaires sont détaillés dans chaque réponse.\n'
matrix.write_text(md,encoding='utf-8')

# Corriger les métadonnées de l'ancien bordereau, sans toucher aux sources.
old=ROOT/'HARMONY MOVERS/01_Synthese_et_chronologie/Reponse_Dufourd_20_octobre_2026'
oldj=old/'bordereau-pieces.json'
data=json.loads(oldj.read_text(encoding='utf-8-sig'))
limits='Lecture visuelle du 21 octobre 2026 : courriel de Mario Taoutel du 12 février 2026 concernant une demande de rejet; aucun contrat de conteneur dans ces deux captures.'
for x in data:
    if x['id']=='RD-14': x.update(title='Captures de courriel procédural — classement corrigé',engagements=[],limits=limits)
    if x['id']=='RD-15': x['limits']='Carte contrôlée visuellement : MTLEV2500487177, Bouchard Stéphane, matricule 4388, PDQ 16. Autorisation signée et rapport distincts.'
jwrite(oldj,data)
oldcsv=old/'bordereau-pieces.csv'
with oldcsv.open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);fields=reader.fieldnames;oldrows=list(reader)
for x in oldrows:
    # Les noms du schéma historique sont lus ci-dessous; seules les valeurs ciblées changent.
    for k,v in list(x.items()):
        if v=='Captures de location de conteneur':x[k]='Captures de courriel procédural — classement corrigé'
        if v=='Ne remplacent pas le bail intégral signé ni le contrat du gardien actuel.':x[k]=limits
    if any(v=='RD-14' for v in x.values()):
        for k in x:
            if 'engagement' in k:x[k]=''
with oldcsv.open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(oldrows)

control=json.loads((OUT/'CONTROLES-DU-DOSSIER.json').read_text(encoding='utf-8'))
control.update(pdf_controle_visuel='Toutes les pages du PDF final ont été contrôlées visuellement; aucun défaut restant.',pdf_pages=pages,pdf_sha256=sha(pdf),pages_controlees=qa['pages_revisees'],references_pieces=sum(len(r['pieces']) for r in rows))
jwrite(OUT/'CONTROLES-DU-DOSSIER.json',control)

zipname='DOSSIER-DUFOURD-2026-10-21.zip'
readme=OUT/'LIRE-EN-PREMIER.md'
text=readme.read_text(encoding='utf-8')
block=f'\n## Télécharger et remettre\n\n[Télécharger le dossier complet en ZIP]({zipname}). Décompresser ce fichier dans un dossier, puis ouvrir REPONSES-AUX-25-DEMANDES.pdf. Le dossier contient les 75 annexes avec leur bordereau, les réponses modifiables, les documents à obtenir et le projet de courriel. Les analyses initialement en Markdown sont conservées sous extension .txt, sans modification de leurs octets.\n\nLe contrôle visuel porte sur les {pages} pages du PDF final. Les 75 annexes correspondent aux empreintes des sources; les vérifications comptables ou documentaires restant ouvertes demeurent indiquées dans les réponses.\n'
if '## Télécharger et remettre' in text:text=text.split('\n## Télécharger et remettre')[0]
readme.write_text(text+block,encoding='utf-8')
# Dans l'archive, le lien vers l'archive elle-même n'est pas nécessaire.
package_files=[p for p in OUT.rglob('*') if p.is_file() and p.suffix.lower()!='.zip' and p.name!='ARCHIVE-CONTROLE.json']
with zipfile.ZipFile(OUT/zipname,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(package_files):z.write(p,p.relative_to(OUT).as_posix())
with zipfile.ZipFile(OUT/zipname) as z:
    assert z.testzip() is None
    assert len(z.namelist())==len(package_files)==len(set(z.namelist()))
    for a in ann:assert hashlib.sha256(z.read(a['fichier'])).hexdigest()==a['sha256']
    for p in package_files:assert hashlib.sha256(z.read(p.relative_to(OUT).as_posix())).hexdigest()==sha(p)
assert (OUT/zipname).stat().st_size<95*1024*1024
result={'archive':zipname,'octets':(OUT/zipname).stat().st_size,'sha256':sha(OUT/zipname),'fichiers':len(package_files),'annexes':len(ann),'controle_crc':'réussi','empreintes_annexes':'75 sur 75 conformes aux sources','transmission':'non effectuée'}
jwrite(OUT/'ARCHIVE-CONTROLE.json',result)
print(json.dumps(result,ensure_ascii=False))
