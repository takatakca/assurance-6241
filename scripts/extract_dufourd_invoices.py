"""Reconcile six supplied Dufourd invoices; preserve cumulative balances separately."""
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import csv, hashlib, json, re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
CASE=ROOT/'HARMONY MOVERS'
SOURCE=CASE/'03_Courriels/Originaux_ooeuf_2026-10-20'
OUT=CASE/'04_Factures_et_comptabilite/Controle_Dufourd_2026-10-20'
(OUT/'Textes_PDF').mkdir(parents=True,exist_ok=True)
MONEY=r'(-?[0-9][0-9 ]*,[0-9]{2})'
ZERO=Decimal('0.00')
def amount(value):return Decimal(value.replace(' ','').replace(',','.'))
def match_money(label,text):
    match=re.search(re.escape(label)+r'\s*'+MONEY+r'\s*\$',text)
    if not match:raise ValueError('Missing amount '+label)
    return amount(match[1])
rows=[]
for f in sorted((SOURCE/'Pieces_jointes').glob('Facture No *.pdf')):
    pages=[p.extract_text() or '' for p in PdfReader(f).pages]
    text='\n'.join(pages).replace('\xa0',' ').replace('\u202f',' ')
    num=re.search(r'Facture no :\s*(\d+)',text)[1]
    date=datetime.strptime(re.search(r'au (\d{2}-\d{2}-\d{4})',f.stem)[1],'%d-%m-%Y').date().isoformat()
    assert 'Dossier : 4518-1' in text
    honoraires=match_money('Total des honoraires',text)
    # Taxes have both an assessment base and tax amount on the same line.
    taxes={}
    for tax in ['TPS','TVQ']:
        found=re.search(tax+r' - montant assujetti à la taxe :\s*'+MONEY+r'\s+'+MONEY+r'\s*\$',text)
        if not found:raise ValueError('Missing '+tax)
        taxes[tax]=amount(found[2])
    billed=match_money('Total facturé',text)
    credits=match_money('Moins acompte(s) reçu(s)',text)
    previous=match_money('Plus solde précédent',text)
    balance=match_money('Total à payer',text)
    subtotal=billed-taxes['TPS']-taxes['TVQ']
    disbursements=subtotal-honoraires
    assert billed-credits+previous==balance,(num,'Printed invoice arithmetic')
    assert disbursements>=ZERO
    total_page=next(i for i,p in enumerate(pages,1) if 'Total facturé' in p)
    text_file=OUT/'Textes_PDF'/f'{num}.txt'
    text_file.write_text('\n\n'.join(f'[Page {i}]\n{p}' for i,p in enumerate(pages,1)),encoding='utf-8')
    rows.append({'facture':num,'date':date,'dossier_cabinet':'4518-1','devise':'CAD présumé; symbole $ imprimé',
      'honoraires_ht':honoraires,'debours_ht':disbursements,'total_ht':subtotal,
      'tps':taxes['TPS'],'tvq':taxes['TVQ'],'total_facture_ttc':billed,
      'acompte_affiche_non_additif':credits,'solde_precedent_affiche':previous,'solde_cumulatif_affiche':balance,
      'page_totaux':total_page,'source':f.relative_to(CASE).as_posix(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),
      'texte_extrait':text_file.relative_to(CASE).as_posix()})
rows.sort(key=lambda r:r['date'])
assert len(rows)==6
initial_credit=rows[0]['acompte_affiche_non_additif']
cumulative=ZERO
for i,row in enumerate(rows):
    cumulative+=row['total_facture_ttc']
    row['cumul_facture_ttc_calcule']=cumulative
    row['credit_initial_consomme_sur_facture']=min(row['total_facture_ttc'],row['acompte_affiche_non_additif'])
    assert cumulative-initial_credit==row['solde_cumulatif_affiche'],(row['facture'],'Cumulative balance')
    if i:
        prior=rows[i-1]['solde_cumulatif_affiche']
        assert row['acompte_affiche_non_additif']==max(-prior,ZERO)
        assert row['solde_precedent_affiche']==max(prior,ZERO)
assert sum(r['credit_initial_consomme_sur_facture'] for r in rows)==initial_credit
totals={key:sum(r[key] for r in rows) for key in ['honoraires_ht','debours_ht','total_ht','tps','tvq','total_facture_ttc']}
totals['depot_initial_impute_par_cabinet']=initial_credit
totals['solde_final_factures']=rows[-1]['solde_cumulatif_affiche']
summary={'as_of':'2026-10-21','source_type':'Six PDF originaux joints au courriel reçu le 20 octobre 2026',
    'status':'Rapprochement arithmétique du compte du cabinet; aucune preuve bancaire ajoutée',
    'totals':totals,'invoices':rows,
    'payment_request':{'amount':3500,'date':'2026-10-20T16:29:08-04:00',
        'type':'Paiement minimal demandé sur honoraires; non additionné au solde facturé',
        'source':(SOURCE/'2026-10-20_1629_Christian_Dufourd.eml').relative_to(CASE).as_posix()},
    'forward_estimates':{'readiness_at_least':15000,'trial_range_low':20000,'trial_range_high':30000,
        'tax_treatment':'Non précisé dans le courriel','stenography':'Facture annoncée en attente, montant non fourni',
        'source':(SOURCE/'2026-10-20_1420_Christian_Dufourd_honoraires.eml').relative_to(CASE).as_posix(),
        'status':'Estimations futures; exclues du total facturé'},
    'checks':['Six arithmétiques de facture exactes','Six soldes cumulatifs rapprochés',
        'Crédits reportés et soldes précédents rapprochés','Dépôt initial consommé une seule fois'],
    'review_points':[{'invoice':'27738','page':1,'service_date':'2026-06-15','hours':0.75,
        'description':'Libellé mentionnant un jugement de divorce; confirmé visuellement sur le PDF. Demander au cabinet la justification du libellé et de son attribution au dossier 4518-1. Aucun ajustement du solde appliqué.'},
        {'description':'Les PDF portent Quadro Holdings Ltée, 6241 boul. Léger, dossier 4518-1, et une rubrique OBJET vide. Vérifier le mandat avant imputation définitive à un volet du litige.'}]}
def number(v):return float(v) if isinstance(v,Decimal) else v
(OUT/'dufourd-rapprochement.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=number),encoding='utf-8')
with (OUT/'dufourd-factures.csv').open('w',newline='',encoding='utf-8-sig') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');writer.writeheader()
    writer.writerows({k:(format(v,'.2f').replace('.',',') if isinstance(v,Decimal) else v) for k,v in row.items()} for row in rows)
def fr(v):return format(v,',.2f').replace(',',' ').replace('.',',')
table='\n'.join(f'| {r["facture"]} | {r["date"]} | {fr(r["total_facture_ttc"])} | {fr(r["acompte_affiche_non_additif"])} | {fr(r["solde_precedent_affiche"])} | {fr(r["solde_cumulatif_affiche"])} | {r["page_totaux"]} |' for r in rows)
readme=f'''# Factures Dufourd — rapprochement au 20 octobre 2026

Les six PDF du dossier cabinet **4518-1** totalisent **{fr(totals['total_facture_ttc'])} $ TTC**. Le dépôt initial de **{fr(initial_credit)} $**, imputé par le cabinet, conduit au **solde cumulatif de {fr(totals['solde_final_factures'])} $** imprimé sur la facture 27905. Ce rapprochement vérifie les factures; il ne constitue pas une preuve bancaire indépendante ni une reconnaissance du bien-fondé de chaque prestation.

| Facture | Date | Facturé TTC | Acompte affiché | Solde précédent | Solde cumulatif affiché | Page des totaux |
|---|---|---:|---:|---:|---:|---:|
{table}

Les acomptes affichés de 1 965,22 $ puis 676,35 $ représentent le crédit restant du même dépôt de 3 000 $, reporté d’une facture à l’autre. **Ne pas additionner ces acomptes, ni les soldes cumulatifs.** Les trois premières factures consomment respectivement 1 034,78 $, 1 288,87 $ et 676,35 $ de ce crédit, soit 3 000 $ au total.

Ventilation facturée : honoraires HT **{fr(totals['honoraires_ht'])} $**; débours HT **{fr(totals['debours_ht'])} $**; TPS **{fr(totals['tps'])} $**; TVQ **{fr(totals['tvq'])} $**. Les 143 $ de débours figurent sur la facture 27852. Le symbole $ est imprimé; CAD est présumé d’après le contexte québécois, sans code de devise explicite.

## Demandes et estimations distinctes

- Courriel Dufourd du 20 octobre 2026 à 16 h 29 : **paiement minimal demandé de 3 500 $**. Il n’établit ni un nouveau montant facturé, ni un paiement reçu. Ne pas l’ajouter au solde de 5 296,60 $.
- Courriel Dufourd du même jour à 14 h 20 : **au moins 15 000 $** pour mettre le dossier en état, puis **20 000 $ à 30 000 $** pour la préparation et la tenue du procès; estimations futures, traitement des taxes non précisé. Les frais de sténographie sont annoncés en attente, sans montant. Ces éléments sont exclus du total facturé.

## Points à clarifier

La facture **27738, page 1, prestation du 15 juin 2026, CR, 0,75 h**, mentionne un « jugement de divorce ». Cette mention a été confirmée visuellement sur le PDF. Demander au cabinet la justification du libellé et de son attribution au dossier 4518-1. Aucun montant n’a été retiré ni déclaré indu sur cette seule observation.

Les six PDF portent Quadro Holdings Ltée, 6241 boul. Léger, dossier 4518-1, avec une rubrique OBJET vide. Ils ont été déposés dans le volet Harmony par la collecte. Vérifier le mandat avant imputation définitive de ces honoraires à un sinistre, à un litige ou à une réclamation récupérable.

## Sources et contrôles

Les chemins de chaque PDF, pages des totaux et SHA-256 figurent dans [le CSV](dufourd-factures.csv) et [le JSON](dufourd-rapprochement.json). Les textes PDF natifs sont conservés dans `Textes_PDF/`. Les six formules de facture, les six soldes cumulatifs et les reports de crédit sont exacts au cent près. Le dépôt de 3 000 $ est également mentionné par Dufourd dans son courriel de 14 h 20.

Script reproductible : `scripts/extract_dufourd_invoices.py` depuis la racine du dossier. Extraction native avec pypdf; contrôle visuel des pages 1 des factures 27738 et 27905. Aucun original modifié.
'''
(OUT/'README.md').write_text(readme,encoding='utf-8')
print(json.dumps({'invoices':len(rows),'totals':totals,'output':OUT.relative_to(ROOT).as_posix()},ensure_ascii=False,default=number))
