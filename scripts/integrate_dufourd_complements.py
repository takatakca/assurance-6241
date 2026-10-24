"""Fusion contrôlée des recherches complémentaires du 21 octobre 2026."""
from pathlib import Path
from collections import Counter
import json, hashlib, shutil

ROOT=Path(__file__).resolve().parents[1]
LOT=ROOT/'HARMONY MOVERS/13_Complements_Dufourd_2026-10-21'
OO=LOT/'Recherche_Ooeuf'
INPUT=ROOT/'scripts/remise-dufourd'
BACK=ROOT/'scripts/.build-livrables/remise-baseline/audits'
BACK.mkdir(parents=True,exist_ok=True)
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

# Pièces d'identité rencontrées dans le fil commercial : conservées dans la
# collecte locale, hors des demandes du cabinet et hors publication du site.
identity=(ROOT/'99_Travail_et_collecte/Complements_Dufourd/Identite_hors_demandes').resolve()
assert identity.is_relative_to(ROOT)
identity.mkdir(parents=True,exist_ok=True)
for name in ['1000102281.jpg','1000102282.jpg','1000102283.jpg','1000102284.jpg']:
    p=OO/name; dst=identity/name
    if p.exists():
        assert p.resolve().is_relative_to(OO.resolve())
        if dst.exists():
            assert sha(dst)==sha(p), 'Copie de collecte divergente'
        else: shutil.move(str(p),str(dst))

groups={}; rows={}
for name in ['audit-communications','audit-pieces','audit-finances']:
    path=INPUT/(name+'.json')
    if not (BACK/path.name).exists(): shutil.copyfile(path,BACK/path.name)
    data=read(BACK/path.name)
    groups[name]=[int(x['id']) for x in data]
    rows.update({int(x['id']):x for x in data})
assert set(rows)==set(range(1,26))

for rel in ['Recherche_Takatak_communications/patch-demandes-communications.json',
            'Recherche_Takatak_finances/patches-demandes.json',
            'Recherche_ChatGPT/patch-demandes-10-16-18-huissier.json']:
    for patch in read(LOT/rel):
        ident=int(patch['id']); old=rows[ident]
        prior={p['path'] for p in patch['pieces']}
        patch['pieces'] += [p for p in old['pieces'] if p['path'] not in prior]
        rows[ident]=patch

# La recherche sur l'autorisation n'a pas retrouvé le formulaire signé.
twenty=next(x for x in read(LOT/'Recherche_ChatGPT/complements-demandes-10-16-18-20.json') if int(x['id'])==20)
rows[20]['reponse_proposee']+=' '+twenty['apport_nouveau']
seen={p['path'] for p in rows[20]['pieces']}
rows[20]['pieces'] += [p for p in twenty['pieces'] if p['path'] not in seen]
rows[20]['controles'].append(twenty['controle'])

coverage={
 'tzanet': {'query':'in:anywhere {TZANET TEZANET TESANET 1000026855 1000026854}','conversations_affichees':18,'journal':'recherche-tzanet-dom.txt'},
 'huissier': {'query':'in:anywhere {"gaucherhuissier.com" "huissierdejustice.ca" "Kronis" "Kostas"}','conversations_affichees':11,'journal':'recherche-huissier-dom.txt'},
 'uhaul_elite': {'query':'in:anywhere {"U-Haul" "UHaul" "Remorquage Elite" "Remorquage Élite"}','conversations_affichees':23,'journal':'recherche-uhaul-elite-dom.txt'},
 'occupation': {'query':'in:anywhere {"5837" "5839"} {bail convention occupation lease} -from:toogoodtogo.com -from:doordash.com','conversations_affichees':23,'journal':'recherche-jeantalon-bail-dom.txt'},
 'cv_police': {'query':'in:anywhere {"curriculum vitae" "autorisation police" "autorisation SPVM" "rapport de police"}','conversations_affichees':16,'journal':'recherche-cv-police-dom.txt'}
}
write(OO/'COUVERTURE-RECHERCHE.json',{'date_locale':'2026-10-21','compte':'ooeuf.ca@gmail.com','recherches':coverage,'limite':'Recherches ciblées et lecture des candidats pertinents. Aucune certification de fouille exhaustive de la boîte ou de toutes les pièces de tous les fils. Les doublons de fil ne sont pas des communications nouvelles.'})

sources={
 '1000026855.jpg':('1000026855.jpg','2025-07-30-1831-Tzanet-courriel-dom.txt','Ooeuf à Joey, 30 juillet 2025 18 h 31'),
 '1000026854.jpg':('1000026854.jpg','2025-07-30-1831-Tzanet-courriel-dom.txt','Ooeuf à Joey, 30 juillet 2025 18 h 31'),
 'Sales Quotation - 141455.pdf':('Sales Quotation - 141455.pdf','Quotation-dom.txt','Panos Liveris à Ooeuf, 28 juillet 2025 15 h 09'),
 'Sales Quotation - 141490.pdf':('Sales Quotation - 141490.pdf','Quotation-dom.txt','Panos Liveris à Ooeuf, 28 juillet 2025 15 h 09'),
 'Declaration-TPS-TVQ-2024-09-30.pdf':('Production_-_Déclaration_TPS-TVH-TVQ_-_AR_SX_NoRefTT_010700112412425_USA_1228709740_SDU_TQ0001_2024-9-30 (2).pdf','2026-09-29-fiscal-dom.txt','Ooeuf à Christian Dufourd, 29 septembre 2026 17 h 07; transfert à cdufourd 17 h 54'),
 'Scan2026-04-03_120155.pdf':('Scan2026-04-03_120155.pdf','2026-09-29-fiscal-dom.txt','Même fil fiscal du 29 septembre 2026'),
 'final (1).xls':('final (1).xls','2026-09-29-fiscal-dom.txt','Même fil fiscal du 29 septembre 2026'),
 'RAPPORT_F.pdf':('RAPPORT_F.pdf','2026-05-01-MANDAT-COMPLETE-dom.txt','Saj à Ooeuf et romanowskiyan@gmail.com, 1 mai 2026 15 h 24'),
 'PV_SIGNE.pdf':('PV_SIGNE.pdf','2026-05-01-MANDAT-COMPLETE-dom.txt','Même fil MANDAT COMPLÉTÉ du 1 mai 2026'),
 'Facture_8695.pdf':('Facture_8695.pdf','2026-05-01-MANDAT-COMPLETE-dom.txt','Même fil MANDAT COMPLÉTÉ du 1 mai 2026'),
 'Quadro-confirm-Jean-Talon-20260424.pdf':('Quadro confirm Jean-Talon _20260424_232808_0000.pdf','DoorDash-Inquiry-2026-04-24.txt','Ooeuf à support@doordash.com, 24 avril 2026 23 h 31'),
 'Etat-renseignements-Quadro-2026-04-24.pdf':('État des renseignements - Revenu Québec(25).PDF','DoorDash-Inquiry-2026-04-24.txt','Même fil DoorDash Inquiry du 24 avril 2026')
}
native=[]
for name,(original,journal,email) in sources.items():
    p=OO/name
    assert p.is_file(),name
    native.append({'fichier':p.relative_to(ROOT).as_posix(),'nom_piece_jointe':original,'courriel':email,'preuve_consultation':(OO/journal).relative_to(ROOT).as_posix(),'sha256':sha(p),'octets':p.stat().st_size,'nature':'pièce jointe binaire téléchargée depuis Gmail; authenticité du contenu non certifiée'})
write(OO/'PROVENANCE-OOEUF.json',{'date_locale':'2026-10-21','compte':'ooeuf.ca@gmail.com','pieces_jointes':native,'extractions':'Les textes et captures DOM sont des extractions de consultation, pas des EML natifs. Certains fils sont tronqués dans Gmail, explicitement conservés avec cette limite. Un secret de paiement Interac est masqué dans les deux extractions du fil du 1 mai; le courriel source est inchangé.','classement_hors_demandes':'Quatre pièces d’identité trouvées dans le fil DoorDash sont conservées dans la collecte locale hors paquet et hors site, car elles ne répondent pas aux demandes examinées.','doublons':'final (1).xls est identique à A018; 1000026854 est une photo du devis 141455, sans nouvelle dépense. La facture 8695 existe en plusieurs versions du même poste.'})

mapping={1:'cv_police',5:'tzanet',6:'uhaul_elite',7:'uhaul_elite',9:'uhaul_elite',10:'huissier',11:'huissier',12:'occupation',16:'huissier',17:'tzanet',18:'huissier',20:'cv_police',24:'uhaul_elite'}
for ident,key in mapping.items():
    rows[ident].setdefault('recherche_effectuee',[]).append('Reprise Ooeuf du 21 octobre 2026 : '+coverage[key]['query']+'; résultats et limites conservés dans Recherche_Ooeuf/COUVERTURE-RECHERCHE.json')
for ident in [2,8,25]:
    rows[ident].setdefault('recherche_effectuee',[]).append('Corroboration du fil Situation de transport dans Ooeuf; contenu substantiel déjà présent dans Takatak, fil affiché partiellement tronqué.')
for ident in [4,13,14,22,23]:
    rows[ident].setdefault('recherche_effectuee',[]).append('Compléments Takatak et pièces natives Ooeuf du fil fiscal du 29 septembre 2026; provenance et empreintes dans Recherche_Ooeuf/PROVENANCE-OOEUF.json.')
for ident in [1,6,7,9,10,11,12,15,16,18,20,24]:
    rows[ident].setdefault('controles',[]).append('Reprise ChatGPT : une conversation accessible sans pièce utile; quatre conversations Harmony affichent une erreur de chargement. Aucun contenu manquant reconstitué; les extractions antérieures restent distinctes.')
for ident,row in rows.items():
    row['controles']=[v.replace('Recherches Gmail actuelles limitées à la boîte Takatak exposée; messages d’Ooeuf et Pierre souvent reçus par transfert.', 'Le premier audit par connecteur portait sur Takatak et ses transferts. La reprise dans Ooeuf est documentée séparément dans les compléments.') for v in row.get('controles',[])]
    for p in row.get('pieces',[]):
        src=(ROOT/p['path']).resolve()
        assert src.is_relative_to(ROOT) and src.is_file(),p['path']
    row['date_recherche_complementaire']='2026-10-21'
for name,ids in groups.items(): write(INPUT/(name+'.json'),[rows[i] for i in ids])
counts=dict(Counter(r['statut'] for r in rows.values()))
oldrows={int(x['id']):x for n in groups for x in read(BACK/(n+'.json'))}
changes=[{'demande':i,'avant':oldrows[i]['statut'],'apres':rows[i]['statut']} for i in rows if oldrows[i]['statut']!=rows[i]['statut']]
write(LOT/'EVOLUTION-DES-DEMANDES.json',{'date':'2026-10-21','avant':dict(Counter(x['statut'] for x in oldrows.values())),'apres':counts,'statuts_modifies':changes,'pieces_jointes_ooeuf':len(native),'envoi_effectue':False})
print(json.dumps({'statuts':counts,'changements':changes,'sources_ooeuf':len(native)},ensure_ascii=False))
