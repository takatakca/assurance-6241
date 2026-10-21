# Contrôle du portail local — 21 octobre 2026

Le portail `00_Lire_en_premier/index.html` a été régénéré après l’ajout du classeur comptable et de la présentation. Le contrôle porte sur les fichiers locaux et l’exécution du JavaScript avec un DOM simulé sous Node; il ne constitue pas une inspection visuelle dans un navigateur.

## Résultat

- **266 fichiers classés, 256 contenus distincts** : existence, taille et empreintes SHA-256 rapprochées de l’inventaire. Les index techniques et les fichiers de collecte ne font pas partie de ce décompte.
- **39 entrées de chronologie affichées** : 20 issues des courriels et 19 des conversations. Ce sont des entrées documentaires, pas nécessairement 39 événements distincts. Les 39 références de source pointent vers des fichiers présents.
- **14 groupes de contrôles réussis** : liens statiques et générés; filtres catégorie/format; recherches avec ou sans accents; filtres de provenance; recherche par intervenant; absence de résultats; aperçu du texte; export CSV; insertion des données.
- Aucun avertissement d’indexation au moment du contrôle. Les 143 textes OCR réussis disposent de leur copie locale dans `Texte_et_OCR/`. Douze n’ont pas de texte reconnu; le succès technique de l’OCR ne prouve pas sa fidélité.

## Corrections appliquées

La chronologie chargeait les courriels sans les afficher. Elle présente maintenant les deux corpus et permet de filtrer leur origine. Chaque entrée conserve la date retenue, la date du message ou du transfert, l’auteur lorsqu’il est identifié, son statut documentaire, la citation disponible et la référence de source. Les anciennes mentions d’originaux absents restent contextualisées par leur portée limitée au chat d’origine.

Les références Windows et celles avec un repère `#additional_messages/...` sont normalisées vers les fichiers locaux réels. Le repère reste visible séparément. Les liens locaux sont limités aux ressources connues; les liens Gmail sont limités à `https://mail.google.com`. Les contenus sont insérés comme texte, et les caractères susceptibles de fermer le bloc JavaScript sont échappés. L’export CSV neutralise les débuts de formule, y compris après des espaces ou caractères de contrôle.

Le document d’accueil est écrit avant son calcul d’empreinte. Le générateur privilégie les textes OCR placés à côté de l’index, pour permettre le déplacement du dossier OneDrive. Il signale les sources ou textes indisponibles au lieu de les faire disparaître sans indication.

## Reproduire

Depuis la racine du dossier, exécuter `python scripts/build_case_portal.py`, puis `node scripts/verify_case_portal.mjs`. Aucun module externe n’est nécessaire pour ces deux scripts. Le reçu détaillé est écrit dans `scripts/.build-livrables/portal-validation.json`.

Une nouvelle collecte modifie l’inventaire : régénérer le portail puis relancer les contrôles. Ce contrôle ne prouve ni l’exhaustivité des comptes de messagerie, ni l’encaissement des montants cités, ni la synchronisation OneDrive. Aucun original n’a été modifié.
