# Dossiers de travail pour l’avocat

Point d’entrée local : **OUVRIR-LES-DOSSIERS.html**. Le classement distingue trois dossiers :

- **6241 Léger** — assurance, chronologie, correspondances, pièces et comptabilité.
- **6280 Somerled NDG** — bail, propriétaire, avis, mises en demeure et litiges.
- **HARMONY MOVERS** — contrats, transport et entreposage, factures, état des biens et procédures.

Les fichiers sont préparés dans le répertoire OneDrive `Documents/ChatGPT/ASSURANCE 6241`. La présence locale ne confirme pas l’état de synchronisation OneDrive.

## Livrables locaux

Le dossier Léger contient un tableau de bord consultable hors ligne, un classeur comptable de dix onglets et une présentation PowerPoint de neuf diapositives. Chaque dossier contient ou reçoit sa synthèse, sa chronologie, son index de pièces et un état de couverture indiquant les documents obtenus et ceux restant à acquérir.

Les messages originaux, les pièces jointes et les documents conservés restent distincts des analyses. Les copies sont identifiées par empreinte SHA-256. Les dates originales restent inchangées. Les allocations d’assurance, les factures, les devis et les encaissements ne sont pas additionnés comme s’ils représentaient la même chose.

## Code de l’outil

- `scripts/extract_case_text.py` : extraction du texte PDF et préparation des pages ou images nécessitant un OCR.
- `scripts/run_case_ocr.ps1` : reconnaissance avec le moteur Windows disponible.
- `scripts/build_case_portal.py` et `scripts/case_portal_template.html` : génération du tableau de bord Léger.
- `scripts/build_dossier_hub.py` : index de recherche commun aux trois dossiers.
- `scripts/extract_downloaded_eml.py` : extraction locale des corps et pièces jointes des courriels EML conservés.

Les chemins et les générateurs décrivent l’espace de travail local. Le code publié ne télécharge pas automatiquement les courriels ou les conversations et n’embarque pas les pièces originales.

## État au 21 octobre 2026

Le dépôt GitHub public est créé. La publication du code de classement et la préparation des dossiers OneDrive sont deux étapes distinctes. Aucun site en production ni accès distant à l’ensemble des pièces n’est confirmé par ce README. L’extraction de toutes les conversations ChatGPT et de toutes les boîtes courriel reste à compléter selon les états de couverture locaux.

Pour reconstruire les index sur le poste où se trouvent les documents, exécuter `python scripts/build_case_portal.py`, puis `python scripts/build_dossier_hub.py`. Les index s’ouvrent ensuite directement dans un navigateur, sans serveur.

L’OCR facilite la recherche; les chiffres, dates et citations doivent être contrôlés sur les originaux. Les questions juridiques et les décisions procédurales restent à valider avec l’avocat chargé du dossier.