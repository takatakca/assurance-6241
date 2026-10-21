# Factures Dufourd — rapprochement au 20 octobre 2026

Les six PDF du dossier cabinet **4518-1** totalisent **8 296,60 $ TTC**. Le dépôt initial de **3 000,00 $**, imputé par le cabinet, conduit au **solde cumulatif de 5 296,60 $** imprimé sur la facture 27905. Ce rapprochement vérifie les factures; il ne constitue pas une preuve bancaire indépendante ni une reconnaissance du bien-fondé de chaque prestation.

| Facture | Date | Facturé TTC | Acompte affiché | Solde précédent | Solde cumulatif affiché | Page des totaux |
|---|---|---:|---:|---:|---:|---:|
| 27604 | 2026-04-21 | 1 034,78 | 3 000,00 | 0,00 | -1 965,22 | 1 |
| 27686 | 2026-06-09 | 1 288,87 | 1 965,22 | 0,00 | -676,35 | 2 |
| 27738 | 2026-07-15 | 2 144,28 | 676,35 | 0,00 | 1 467,93 | 2 |
| 27816 | 2026-08-26 | 930,15 | 0,00 | 1 467,93 | 2 398,08 | 2 |
| 27852 | 2026-10-06 | 2 699,61 | 0,00 | 2 398,08 | 5 097,69 | 1 |
| 27905 | 2026-10-20 | 198,91 | 0,00 | 5 097,69 | 5 296,60 | 1 |

Les acomptes affichés de 1 965,22 $ puis 676,35 $ représentent le crédit restant du même dépôt de 3 000 $, reporté d’une facture à l’autre. **Ne pas additionner ces acomptes, ni les soldes cumulatifs.** Les trois premières factures consomment respectivement 1 034,78 $, 1 288,87 $ et 676,35 $ de ce crédit, soit 3 000 $ au total.

Ventilation facturée : honoraires HT **7 073,00 $**; débours HT **143,00 $**; TPS **360,80 $**; TVQ **719,80 $**. Les 143 $ de débours figurent sur la facture 27852. Le symbole $ est imprimé; CAD est présumé d’après le contexte québécois, sans code de devise explicite.

## Demandes et estimations distinctes

- Courriel Dufourd du 20 octobre 2026 à 16 h 29 : **paiement minimal demandé de 3 500 $**. Il n’établit ni un nouveau montant facturé, ni un paiement reçu. Ne pas l’ajouter au solde de 5 296,60 $.
- Courriel Dufourd du même jour à 14 h 20 : **au moins 15 000 $** pour mettre le dossier en état, puis **20 000 $ à 30 000 $** pour la préparation et la tenue du procès; estimations futures, traitement des taxes non précisé. Les frais de sténographie sont annoncés en attente, sans montant. Ces éléments sont exclus du total facturé.

## Points à clarifier

La facture **27738, page 1, prestation du 15 juin 2026, CR, 0,75 h**, mentionne un « jugement de divorce ». Cette mention a été confirmée visuellement sur le PDF. Demander au cabinet la justification du libellé et de son attribution au dossier 4518-1. Aucun montant n’a été retiré ni déclaré indu sur cette seule observation.

Les six PDF portent Quadro Holdings Ltée, 6241 boul. Léger, dossier 4518-1, avec une rubrique OBJET vide. Ils ont été déposés dans le volet Harmony par la collecte. Vérifier le mandat avant imputation définitive de ces honoraires à un sinistre, à un litige ou à une réclamation récupérable.

## Sources et contrôles

Les chemins de chaque PDF, pages des totaux et SHA-256 figurent dans [le CSV](dufourd-factures.csv) et [le JSON](dufourd-rapprochement.json). Les textes PDF natifs sont conservés dans `Textes_PDF/`. Les six formules de facture, les six soldes cumulatifs et les reports de crédit sont exacts au cent près. Le dépôt de 3 000 $ est également mentionné par Dufourd dans son courriel de 14 h 20.

Script reproductible : `scripts/extract_dufourd_invoices.py` depuis la racine du dossier. Extraction native avec pypdf; contrôle visuel des pages 1 des factures 27738 et 27905. Aucun original modifié.
