"""Reconcile the 24 October sources with the frozen previous delivery."""
from pathlib import Path
import json, hashlib, re

ROOT=Path(__file__).resolve().parents[1]
LOT=ROOT/'HARMONY MOVERS/14_Recherche_complementaire_2026-10-24'
AUD=ROOT/'scripts/remise-dufourd'
OLD=ROOT/'scripts/.build-livrables/remise-baseline-2026-10-24/audits'
PREFIX=LOT.relative_to(ROOT).as_posix()+'/'
NAMES=['audit-communications','audit-pieces','audit-finances']

def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def piece(rel,apport,repere='',nature='analyse'):
    path=PREFIX+rel
    assert (ROOT/path).is_file(),path
    return dict(path=path,apport=apport,repere=repere,nature=nature)
def add(r,items):
    seen={p['path'] for p in r['pieces']}
    for p in items:
        assert (ROOT/p['path']).is_file(),p['path']
        if p['path'] not in seen:r['pieces'].append(p);seen.add(p['path'])

def extend_unique(target, items):
    for item in items:
        if item and item not in target:target.append(item)

def apply_patch(rows, patch, *, research_only=False):
    """Merge evidence, never upgrade a status from a searcher's recommendation alone."""
    rid=int(patch['id']);assert rid in rows,rid
    r=rows[rid];add(r,patch.get('pieces',[]))
    if patch.get('apport_nouveau'):
        if research_only:
            scope=patch.get('compte','sous-lot de recherche')
            extend_unique(r['recherche_effectuee'],[f"Recherche du 24 octobre ({scope}) : "+patch['apport_nouveau']])
        else:r['reponse_proposee']+=' Complément du 24 octobre : '+patch['apport_nouveau']
    if not research_only:extend_unique(r['manquants'],patch.get('manquants_maintenus',[]))
    extend_unique(r['recherche_effectuee'],patch.get('recherche_effectuee',[]))
    extend_unique(r['controles'],patch.get('risques_controles',[]))
    extend_unique(r['controles'],patch.get('controles',[]))

def patch_list(path):
    patches=read(path)
    if isinstance(patches,dict):
        if 'id' in patches:return [patches]
        patches=patches.get('demandes',patches.get('patches',[]))
    assert isinstance(patches,list),path
    return patches

def main():
    groups={n:read(OLD/(n+'.json')) for n in NAMES}
    rows={r['id']:r for group in groups.values() for r in group}
    assert sorted(rows)==list(range(1,26))
    old_pieces={rid:{p['path'] for p in r['pieces']} for rid,r in rows.items()}
    input_paths=[OLD/(n+'.json') for n in NAMES]
    # Historical extracts and annexes stay immutable. Only current responses change.
    for r in rows.values():
        for key in ['controles','recherche_effectuee','manquants','demarches']:r.setdefault(key,[])
        for key in ['controles','recherche_effectuee']:
            r[key]=[x for x in r[key] if not ('quatre conversations' in x.lower() and any(t in x.lower() for t in ['bloqu','erreur','chargement']))]
        r['controles']=[('Les recherches négatives initiales étaient limitées à Takatak; les recherches du 24 octobre dans Takatak et Ooeuf sont documentées séparément. Leur absence de résultat ne prouve pas l’absence dans les téléphones, les comptes tiers ou les archives non indexées. Aucun message envoyé.' if x.startswith('Résultat négatif limité') else x) for x in r['controles']]
        r['date_recherche_complementaire']='2026-10-24'
        r['date_controle']='2026-10-24'
        r['statut_transmission']='non_envoye'
        r['mise_a_jour']='Intégration du 24 octobre 2026 à partir de la livraison figée; originaux et anciennes annexes conservés.'
        r['recherche_effectuee'].append('Reprise du 24 octobre 2026 : quatre conversations ChatGPT accessibles; recherches ciblées dans Takatak et Ooeuf, pièces et précisions nouvelles du client. Périmètre et limites consignés dans le bilan du lot 14.')
    for rel in ['Textos_fournis_client/patch-incremental.json','Inventaire_Daniel_Simard/patch-incremental.json','Huissier_analyse_24/patch-incremental.json']:
        input_paths.append(LOT/rel)
        for p in patch_list(LOT/rel):apply_patch(rows,p)
    for rel in ['Takatak_transport/patch-incremental.json','Takatak_huissier_police_cv/patch-incremental.json']:
        input_paths.append(LOT/rel)
        for p in patch_list(LOT/rel):apply_patch(rows,p,research_only=True)
    upkeep=read(LOT/'Entretien_inventaire_24/INTEGRATION-PROPOSEE.json')
    input_paths.append(LOT/'Entretien_inventaire_24/INTEGRATION-PROPOSEE.json')
    for key,p in upkeep.items():
        match=re.fullmatch(r'demande(\d+)',key)
        if not match or not isinstance(p,dict):continue
        rid=int(match.group(1));assert rid in rows,rid
        r=rows[rid];add(r,p.get('ajouts_pieces',[]))
        if p.get('texte_a_integrer'):r['reponse_proposee']+=' Complément du 24 octobre : '+p['texte_a_integrer']
        if p.get('note'):r['reponse_proposee']+=' '+p['note'].replace('La version avril déduplique A074.','La version d’avril est identique par SHA-256 à la pièce déjà annexée A074; elle ne crée pas une seconde preuve ou un montant supplémentaire.')
        if p.get('controle_visuel_a_preciser'):extend_unique(r['controles'],[p['controle_visuel_a_preciser']])
        extend_unique(r['controles'],p.get('controles',[]))
    declarations=piece('PRECISIONS-DU-CLIENT-24-OCTOBRE.md','Précisions du client sur les réponses et les détenteurs à contacter.','Échanges du 24 octobre 2026','declaration')
    contacts=piece('SUIVIS-ET-CONTACTS.md','Coordonnées fournies par le client et demandes précises à adresser; aucun appel ni message envoyé.')
    for rid in [3,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25]:add(rows[rid],[declarations])
    for rid in [10,11,12,16,18,24]:add(rows[rid],[contacts])

    r=rows[1];r['statut']='document_disponible'
    r['reponse_proposee']='La copie de CV-Final.docx fournie directement par le client le 24 octobre 2026 est jointe. Le document de deux pages porte le nom Matthieu Wallace Barnard. Il répond à la demande de copie du curriculum vitae. Le contenu décrit son parcours; il ne constitue pas une vérification indépendante des formations et emplois. Le document ne porte pas de date imprimée.'
    add(r,[piece('Documents_fournis_par_client/CV-Final.docx','CV de Matthieu Wallace Barnard fourni par le client, deux pages.','Document Word natif','original'),piece('Documents_fournis_par_client/PROVENANCE-CV.json','Provenance de l’acquisition du CV et empreinte du fichier.')])
    r['manquants']=[];r['demarches']=['Faire relire le CV par son auteur avant la remise au cabinet.']
    r['controles']=[x for x in r['controles'] if 'Résultat négatif' not in x]

    rows[2]['reponse_proposee']=rows[2]['reponse_proposee'].replace('Les échanges directs de M. Constantino, les SMS/Messenger et les enregistrements téléphoniques annoncés par Harmony restent à rapprocher de ce lot.','Les échanges directs de M. Constantino, les treize captures SMS/MMS reçues le 24 octobre et les enregistrements téléphoniques annoncés par Harmony restent à rapprocher de ce lot. Les captures sont désormais disponibles; leur complétude et les autres canaux restent à vérifier.')
    rows[2]['manquants']=[('Comparaison des treize captures reçues aux conversations sur les téléphones : numéros, coupures, médias natifs et éventuels échanges supplémentaires SMS/Messenger des trois intervenants.' if x.startswith('Exports intégraux SMS/Messenger') else x) for x in rows[2]['manquants']]
    rows[2]['controles'].append('Les captures prouvent le contenu affiché; elles ne valent ni export intégral ni vérification indépendante de l’identité du contact. La complétude annoncée par le client reste une déclaration.')
    rows[5]['controles']=[('Le lot antérieur comportait quinze images et dix PDF; les dix PDF ajoutés le 24 octobre couvrent cinq références et plusieurs copies ou versions. Les fichiers ne sont pas des dépenses indépendantes.' if x.startswith('Quinze images et dix PDF') else x) for x in rows[5]['controles']]
    rows[5]['demarches']=[('Faire confirmer les variantes de dates et de contenu A267/A290, A281/BUNN/Taylor, les versions de devis 259 et les relations devis/factures; la photo 1000069203 montre A267 devant un autre feuillet A290.' if x.startswith('Faire confirmer les numéros ambigus A 290/A 267') else x) for x in rows[5]['demarches']]
    rows[5]['controles'].extend(['Les tableaux IndemniPro sont des tableaux de réclamation du sinistre antérieur, pas un inventaire autonome de valeur marchande actuelle. Les colonnes réclamé, évalué et alloué ne prouvent pas un paiement encaissé.','Le rapport CKS N82145 du 26 novembre 2024 décrit des problèmes persistants et une recommandation de remplacement; il ne prouve pas l’installation ultérieure d’un nouvel appareil. Le montant HT de 6 700,68 $ et le montant TTC de 7 704,10 $ doivent être rapprochés avant toute totalisation.'])

    aka=piece('Ooeuf/Invoice_1020_from_AKA_Moving.pdf','Facture AKA Moving 1020 à Quadro du 11 juin 2025 : 600 $ HT, 689,85 $ TTC, montant dû affiché.','p. 1; description « Moving Globo Shoe Company »','original')
    aka_note=piece('Ooeuf/ANALYSE-ET-PROVENANCE-OOEUF.md','Contrôle des factures AKA, des versions et du lien U-Haul déclaré par le client.')
    for rid in [6,7]:
        r=rows[rid];r['statut']='partiel';add(r,[aka,aka_note])
        r['pieces']=[p for p in r['pieces'] if not (p['path'].startswith(PREFIX+'Ooeuf/') and '1026' in p['path'])]
    rows[6]['reponse_proposee']='Selon la précision donnée par le client le 24 octobre, le prestataire du véhicule U-Haul était AKA Moving et la réponse documentaire à produire est sa facture. Nous joignons la facture 1020 du 11 juin 2025 à Quadro, pour 689,85 $ TTC. La date la rapproche de l’opération de juin; le client n’a pas précisé le numéro de facture dans sa déclaration. Le PDF décrit un service commercial de déménagement et porte le libellé « Moving Globo Shoe Company », sans mention U-Haul. L’identité du prestataire est donc déclarée par le client; le contrat ou numéro de location U-Haul lui-même reste non retrouvé. Aucun contrat distinct n’est inventé.'
    rows[6]['manquants']=['Confirmation par le client ou AKA que la facture 1020 est bien la facture visée et explication du libellé « Moving Globo Shoe Company ».','Contrat/réservation U-Haul détenu par AKA, ou confirmation de non-détention et modalités effectivement convenues.']
    rows[6]['demarches']=['Présenter la facture AKA et la déclaration au cabinet; faire confirmer par le donneur d’ordre le numéro, le véhicule et la date.']
    rows[7]['reponse_proposee']='Même réponse documentaire que pour la demande 6, conformément à la précision du client : facture AKA Moving 1020 du 11 juin 2025, 689,85 $ TTC, jointe une seule fois au bordereau et référencée aux deux demandes. Elle affiche un montant dû; aucune preuve bancaire ou quittance d’acquittement correspondante n’est produite par cette facture seule. Les factures 1026 d’août, relatives notamment à des fours à pizza, sont traitées séparément et ne sont pas ajoutées au prix du véhicule U-Haul.'
    rows[7]['manquants']=['Rapprochement confirmé de la facture 1020 avec le véhicule U-Haul de juin.','Preuve de paiement de cette facture : reçu, virement ou ligne bancaire, avec payeur et date.']
    rows[7]['demarches']=['Rechercher la ligne de règlement correspondant à la facture 1020 auprès du payeur ou du comptable; conserver les opérations d’août et de décembre séparées.']
    rows[7]['controles']=[x.replace('Aucun original sauvegardé/annexé.','Un exemplaire PDF a depuis été récupéré dans les archives ChatGPT du lot 14; il reste écarté comme justificatif de Quadro/U-Haul.') for x in rows[7]['controles']]

    rows[8]['reponse_proposee']='Les courriels conservés et les treize captures SMS/MMS envoyées par Pierre le 24 octobre sont joints et référencés ci-dessous. Les captures montrent le contact « Transport Resto 6141 », se présentant comme Allen, des échanges sur les photos et le devis avant le déménagement, puis des messages sur la livraison, les biens restants et le mandat. Le client déclare que tous les échanges sont déjà au dossier. Cette déclaration est consignée; les captures ne permettent pas, seules, de contrôler l’intégralité technique des trois téléphones et de tous les médias. La portée écrite de la demande 8 et l’engagement oral E9 relatif au prestataire U-Haul restent distingués.'
    rows[8]['manquants']=['Vérification des éventuelles coupures, du numéro de contact et des médias natifs par comparaison au téléphone; confirmation de la complétude déclarée par le client.','Rapprochement de la portée écrite 8 et de la portée orale E9 avec le cabinet.']
    rows[8]['demarches']=['Remettre le lot disponible et la déclaration de complétude du client; vérifier uniquement les coupures ou pièces annoncées sans fichier correspondant.']
    rows[9]['statut']='partiel'
    rows[9]['reponse_proposee']='Le client désigne l’inventaire établi par l’huissier comme sa réponse à la demande 9 et déclare qu’il comprend tous les biens déménagés ce jour-là. Le rapport et les annexes de saisie sont joints. Ils documentent la saisie du 17 décembre 2025 : le rapport comporte 18 lignes ou catégories, qui ne représentent pas nécessairement 18 objets. L’annexe II manuscrite précise que certains items ont été retrouvés après coup. Ces pièces peuvent servir au rapprochement demandé; leur correspondance article par article avec le chargement U-Haul de juin reste à confirmer, car les dates et opérations sont distinctes.'
    rows[9]['manquants']=['Correspondance entre les lignes des inventaires de saisie et les biens chargés dans U-Haul en juin, à confirmer par une personne présente.','Identification de la date visée par « ce jour-là » dans la déclaration du client et prise en compte des biens retrouvés après coup.']

    for rid in [10,11]:
        rows[rid]['reponse_proposee']+=' Le 24 octobre, le client précise pour les demandes 10 et 11 qu’il ne dispose d’aucun bail supplémentaire, seulement de factures et de paiements immédiats. Cette précision ne retire pas les anciennes conventions CINTEC conservées; elle doit être rapprochée de la période et du site concernés.'
        rows[rid]['demarches'].insert(0,'Identifier les factures et règlements immédiats évoqués par le client : émetteur, adresse, période et objet (entreposage ou chariot).')
    rows[12]['reponse_proposee']+=' Le client désigne maintenant Abdel, au 514 996-4247, comme la personne qui sous-loue l’espace et qu’il faut joindre. Le courriel natif du 1er juillet 2025 à Maude Robidoux, joint, annonce la relocalisation au 5837 Jean-Talon et une concertation avec le propriétaire; il s’agit d’une déclaration adressée au courtier, pas d’un accord du sous-locateur.'
    rows[12]['demarches'].insert(0,'Joindre Abdel au 514 996-4247 pour obtenir une confirmation écrite de la sous-location : parties, adresse exacte, dates, espace, loyers et autorisations; projet de demande dans la fiche de suivi.')
    add(rows[12],[piece('Ooeuf/2025-07-01-Relocalisation-Jean-Talon.eml','Courriel du 1er juillet 2025 annonçant la relocalisation au 5837 Jean-Talon; déclaration du client au courtier.','En-têtes et corps du message','original')])

    fiscal=piece('Entretien_inventaire_24/NOTE-DOSSIER-FISCAL-TOMMASO-NICK.md','Repérage du dossier fiscal Tommaso Di Paola/Nicholas Cristiano et limites par demande.')
    for rid in [13,14,23]:
        add(rows[rid],[fiscal]);rows[rid]['reponse_proposee']+=' Le client désigne le dossier fiscal déjà transmis par Tommaso/Nick comme sa réponse. Les sources identifient Nicholas « Nick » Cristiano, CPA, CMA, au cabinet Tommaso Di Paola Inc.; les classeurs et le rapport de compilation au 30 juin 2025 sont déjà joints. La note de rapprochement distingue les documents effectivement disponibles des contrats, périodes ou calculs restant à documenter.'
    add(rows[13],[piece('Ooeuf/Quadro_Holding_Lettre_UberEats_FR_Clean.pdf','Lettre unilatérale Quadro demandant l’activation de seize marques chez Uber Eats; date imprimée du 24 avril 2024, adresse 5839 Jean-Talon.','3 pages; jointe au courriel du 16 juillet 2025 à Benson Noisy','original'),piece('Ooeuf/PROVENANCE-OOEUF-24.json','Provenance du courriel et de la lettre Uber Eats; date imprimée et date d’envoi distinguées.'),piece('Ooeuf/ANALYSE-ET-PROVENANCE-OOEUF.md','Analyse des documents récupérés dans Ooeuf, dont la lettre unilatérale Uber Eats et ses limites.')])
    rows[13]['reponse_proposee']+=' Une lettre Quadro de trois pages demandant l’activation de seize marques sur Uber Eats est également disponible. Elle porte la date imprimée du 24 avril 2024 et l’adresse 5839 Jean-Talon, et figure en pièce jointe du courriel du 16 juillet 2025 à Benson Noisy. Il s’agit d’une démarche unilatérale du client : aucune acceptation Uber, aucun contrat contresigné ni revenu n’en est déduit.'
    rows[13]['controles'].append('Lettre Uber : date imprimée du 24 avril 2024 distincte de sa transmission le 16 juillet 2025; adresse 5839 distincte du 5837, à rapprocher sans correction du document source.')
    rows[15]['reponse_proposee']='Le lot comprend désormais le devis QT1076, la liste « INVENTAIRE RESTO.xlsx » transmise dans une chaîne de mai 2023 et les captures des échanges avec Allen fournies par Pierre le 24 octobre. Certaines captures affichent des galeries de photos envoyées le 6 juin 2025 à 17 h 59; elles documentent l’envoi avant le déménagement. Le classeur contient 39 lignes d’équipements avec de nombreux modèles et séries; le client confirme qu’il s’agit de l’inventaire lors de l’achat. Sa colonne VALEUR est vide. Les captures, le classeur et leur provenance sont remis; les photos natives et les correspondances entre les listes restent à contrôler.'
    rows[15]['manquants']=['Fichiers natifs des photos visibles dans les galeries, si une lecture de détail ou des métadonnées est nécessaire.','Rapprochement entre la liste de mai 2023, le devis QT1076 et les photos envoyées en juin 2025; confirmation des ajouts ou retraits.']
    rows[15]['demarches']=['Comparer les galeries envoyées le 6 juin à 17 h 59 avec les photos natives et les captures J02–J04, sans supposer qu’elles représentent exactement les mêmes fichiers.','Faire identifier par la personne présente les équipements de la liste de 2023 et ceux du devis de 2025; consigner les modèles, séries, ajouts et retraits confirmés.']
    rows[16]['reponse_proposee']+=' Le client fournit le contact « Costantinos Chronis », 514 910-6319, indique qu’il est disponible par téléphone et qu’il a été témoin du déménagement. Ce nom déclaré sera rapproché des variantes KOSTAS/KOSTA KRONIS inscrites aux procès-verbaux, sans correction silencieuse de ces pièces.'
    rows[16]['demarches'].insert(0,'Joindre le contact fourni au 514 910-6319 pour confirmer son identité, les conditions de garde, les documents détenus et ses observations personnelles datées; fiche de demande préparée.')
    rows[17]['statut']='document_disponible'
    rows[17]['reponse_proposee']='La documentation Tzanet désignée par le client comme son évaluation complète est disponible : soumission 141455 du 28 juillet 2025 à Quadro, sa photographie et le courriel/capture de Panos Liveris sur le modèle Tim Hortons. Nous remettons ce lot pour répondre à la demande 17. La soumission est un chiffrage commercial de remplacement, de 90 620 $ HT et 104 190,35 $ TTC, livraison exclue. Le classement « document disponible » porte sur la production de ce lot identifié par le client; il ne transforme pas le devis en expertise indépendante de l’état, de la valeur marchande de chaque bien ou de la cause des dommages. Le devis 141490 au nom de Les délice d’aden est distingué et exclu du montant Quadro.'
    rows[17]['manquants']=[]
    rows[17]['demarches']=['Faire confirmer au cabinet que le lot Tzanet ainsi identifié correspond à la portée de la demande; s’il requiert une évaluation technique supplémentaire, en préciser le mandat.']
    rows[17]['controles'].append('Le client confirme le 24 octobre que ce lot constitue l’évaluation qu’il entend produire. Aucune nouvelle expertise technique n’a été acquise; disponibilité documentaire et portée probante restent distinctes.')
    rows[17]['portee_statut']='Disponibilité du lot Tzanet désigné par le client; chiffrage commercial de remplacement, sans conclusion d’expertise indépendante.'
    rows[18]['reponse_proposee']+=' Le 24 octobre, le client précise que les images relèvent de la production TV et doivent être demandées directement à Michel Gaucher, 514 863-0116. Leur détenteur, leur auteur, les droits de copie et leur lien aux constats de l’huissier sont à confirmer auprès de lui. Les médias ne sont pas présentés comme reçus.'
    rows[18]['demarches']=[x for x in rows[18]['demarches'] if not x.startswith('Élargir la recherche aux adresses du domaine gaucherhuissier.com')]
    rows[18]['demarches'].insert(0,'Joindre Michel Gaucher au 514 863-0116 : demander qui détient les photos/vidéos, copie ou modalités de remise, dates, auteur, inventaire des fichiers et éventuelles observations écrites de dommages.')
    rows[24]['reponse_proposee']='Le client précise le 24 octobre que Remorquage Élite a été sollicité par téléphone, que la facture n’est pas repérée et que le contact est Polo, 514 928-4444. Cette déclaration et la fiche de suivi sont jointes. Aucun mandat écrit, facture ou reçu Élite n’a encore été acquis. AKA Moving est traité séparément aux demandes 6 et 7; ses factures ne sont pas attribuées à Élite.'
    rows[24]['manquants']=['Duplicata de facture ou reçu Élite; confirmation écrite du mandat téléphonique, de la date, du trajet, des biens et du payeur.','Identité légale de l’entreprise et qualité de Polo; rapprochement de tout règlement avec l’opération concernée.']
    rows[24]['demarches']=['Joindre Polo au 514 928-4444 pour demander le duplicata et la confirmation du mandat; conserver sa réponse avec la date et les pièces reçues.']
    rows[25]['reponse_proposee']+=' Les treize captures reçues le 24 octobre complètent les échanges entrants et sortants. Le client indique avoir maintenant répondu à l’ensemble du questionnaire de son côté. Les documents sont présentés avec leur provenance, sans conclusion de responsabilité ni admission ajoutée; les échanges divergents sont conservés pour examen par le cabinet.'

    # Later agents provide additive source-backed patches; no fabricated status upgrade.
    integrated_late=[]
    for folder in ['Daniel_Simard','Racine_Chamberland']:
        p=LOT/folder/'patch-incremental.json'
        if not p.exists():continue
        input_paths.append(p);integrated_late.append(folder)
        for patch in patch_list(p):apply_patch(rows,patch)

    # This full-row proposal predates the client additions: merge its pieces rather
    # than replacing the row, so the declaration and historical annexes survive.
    auth_path=LOT/'Autorisation_SPVM/PROPOSITION-DEMANDE-20.json'
    input_paths.append(auth_path);auth=read(auth_path)
    assert auth['id']==20 and auth['statut']=='partiel'
    r=rows[20];add(r,auth['pieces'])
    for key in ['statut','reponse_proposee','manquants','demarches']:r[key]=auth[key]
    r['reponse_proposee']=r['reponse_proposee'].replace('demande20','demande 20')
    extend_unique(r['controles'],auth.get('controles',[]))
    extend_unique(r['recherche_effectuee'],auth.get('recherche_effectuee',[]))
    r['reponse_proposee']+=' La rubrique facultative d’attestation est réservée au cabinet; aucune assermentation n’est tenue pour accomplie ou systématiquement obligatoire.'
    r['portee_statut']='Projet d’autorisation préparé, non signé, non assermenté et non envoyé; l’autorisation personnelle signée reste à obtenir.'

    # The native policy now supplies the requested copy. Keep later correspondence
    # and client declarations while replacing the obsolete "full policy missing" row.
    policy_path=LOT/'Ooeuf/Polices/PROPOSITION-DEMANDE-21.json'
    input_paths.append(policy_path);policy=read(policy_path)
    assert policy['id']==21 and policy['statut']=='document_disponible'
    r=rows[21];add(r,policy['pieces'])
    for key in ['statut','reponse_proposee','manquants','demarches','portee_statut']:r[key]=policy[key]
    extend_unique(r['controles'],policy.get('controles',[]))
    extend_unique(r['recherche_effectuee'],policy.get('recherche_effectuee',[]))
    if 'Racine_Chamberland' in integrated_late:
        r['reponse_proposee']+=' Les correspondances du courtier sont également jointes avec leur chronologie; les brouillons restent distingués des messages envoyés.'
        rows[22]['demarches']=[('Le fil du 4 août 2026 est désormais documenté par les copies de lecture du corpus expert. Obtenir au besoin son EML d’origine et ses annexes annoncées pour vérifier la complétude native, puis rapprocher le dossier de l’assureur avec les 22 fils conservés.' if x.startswith('Compléter la collecte ciblée du fil du 4 août 2026') else x) for x in rows[22]['demarches']]

    # Combine overlapping checklists without discarding a distinct missing item.
    rows[2]['manquants'][0]='Comparaison des treize captures reçues aux conversations sur les téléphones : numéro du contact, identité de l’utilisateur, coupures, médias natifs et éventuels échanges supplémentaires SMS/Messenger détenus par les trois intervenants.'
    rows[3]['manquants'][0]="Facture d’achat, acte de cession ou crédit-bail de chaque équipement concerné, avec vendeur, acquéreur, date, désignation et justificatif de paiement."
    rows[3]['manquants'][1]="Rapprochement des titres avec chaque item de l’annexe du PV et du classeur de 2023, ses modèles/séries et les transferts entre entités; auteur et contexte du classeur à confirmer."
    redundant={
        2:['Numéro du contact et identité de l’utilisateur du téléphone à documenter.','Export complet et éventuels échanges détenus par les autres intervenants.'],
        3:['Acte ou facture d’achat/cession et preuve de paiement.','Lien entre vendeur, acquéreur, biens du classeur et équipements réclamés; auteur et contexte du classeur à confirmer.'],
        10:['Confirmation du lieu et du périmètre actuel des biens, ainsi que de tout déplacement ultérieur.'],
        12:['Bail, sous-location, cession ou autorisation du propriétaire établissant le droit d’occupation du 5837 Jean-Talon Est, parties, date d’effet et signatures.'],
        16:['Modalités détaillées de garde, auteur/date de la signature ajoutée, confirmation de la garde actuelle.'],
        18:['Photos et vidéos natives prises par l’huissier, métadonnées et repères des observations.'],
    }
    for rid,duplicates in redundant.items():rows[rid]['manquants']=[x for x in rows[rid]['manquants'] if x not in duplicates]
    # Late collection adds overlapping checklists. Consolidate their substance
    # without dropping a distinct document or confusing the two insurance claims.
    rows[3]['manquants']=[x for x in rows[3]['manquants'] if x not in [
        'Actes d’acquisition, factures d’achat ou contrats de crédit-bail acceptés, par équipement.',
        'Correspondance vendeur/acquéreur/date/marque/modèle/numéro de série avec les biens de la saisie et chaîne de transferts entre entités.']]
    if 'Racine_Chamberland' in integrated_late and 'Daniel_Simard' in integrated_late:
        rows[22]['manquants']=[
            'Dossier assureur/expert SNB 53640-196353 / 23910-009447 : bordereau exhaustif des documents transmis et reçus, courriels natifs, pièces jointes et accusés de réception; compléments des passages tronqués ou repliés et pièces seulement annoncées.',
            'Preuve de perte détaillée par bien, devis/rapports, photographies, factures, chaîne de garde, dates et lieux, ainsi que tout complément transmis depuis la lettre du 4 août 2026.',
            'Rapport final ou position plus récente de l’assureur, si émis; justificatifs bancaires des indemnités réellement encaissées et ventilation par sinistre, bien et période. Un paiement de prime ou un montant de garantie ne démontre pas une indemnité.',
            'Rapprochement documenté par bien, poste et période entre le dossier antérieur Léger/Hadmo, le dossier SNB et les biens réclamés contre Harmony.',
            'PDF natif « Lettre à l’Assuré.pdf » du 21 octobre 2025 (DLL 32-10296) et contrôle de son périmètre distinct.'
        ]
    rows[20]['demarches']=[x.replace('la page1','la page 1') for x in rows[20]['demarches']]

    # Current prose must not inherit stale results from the frozen previous delivery.
    for r in rows.values():
        for key in ['manquants','demarches','controles','recherche_effectuee']:
            r[key]=list(dict.fromkeys(r[key]))
        assert old_pieces[r['id']].issubset({p['path'] for p in r['pieces']}),r['id']
        assert len(r['pieces'])==len({p['path'] for p in r['pieces']}),r['id']
        for p in r['pieces']:assert (ROOT/p['path']).is_file(),p['path']
        current=' '.join([r['reponse_proposee'],*r['manquants'],*r['demarches'],*r['controles']])
        assert 'quatre conversations Harmony affichent une erreur' not in current,r['id']
    assert not rows[1]['manquants']
    assert rows[17]['statut']=='document_disponible'
    assert rows[20]['statut']=='partiel' and 'signature réelle' in rows[20]['reponse_proposee']
    counts={s:sum(r['statut']==s for r in rows.values()) for s in sorted({r['statut'] for r in rows.values()})}
    assert counts=={'document_disponible':5,'non_repere':3,'partiel':17},counts

    for n,group in groups.items():write(AUD/(n+'.json'),group)
    write(LOT/'ETAT-APRES-INTEGRATION.json',{'date':'2026-10-24','statuts':{str(i):rows[i]['statut'] for i in sorted(rows)},'comptes_statuts':counts,'demandes':25,'envoi':False,'patches_complementaires_integres':integrated_late,'inputs':[{'path':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in input_paths],'controles':{'anciennes_pieces_conservees':True,'chemins_pieces_existants':True,'doublons_de_chemin_par_demande':0,'statuts_verifies_sur_25_demandes':True}})
    print(json.dumps({'demandes':25,'statuts':counts,'patches_complementaires_integres':integrated_late},ensure_ascii=False))

if __name__=='__main__':main()
