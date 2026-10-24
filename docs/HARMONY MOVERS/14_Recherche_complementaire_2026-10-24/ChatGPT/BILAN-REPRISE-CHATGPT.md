# Reprise ChatGPT du 24 octobre 2026 — Harmony Movers

Les quatre conversations qui affichaient une erreur le 21 octobre sont maintenant accessibles dans le compte affiché **Takatak Plus**, depuis le navigateur intégré. Le travail a été effectué dans un onglet distinct. Aucun prompt n’a été envoyé, aucune nouvelle réponse générée, aucun réglage de compte modifié.

## Ce qui a été récupéré

| Conversation | Contenu visible récupéré | Portée |
|---|---|---|
| Finaliser dossier Harmony Movers | 1 message utilisateur et 1 réponse assistant | Demande de poursuivre et promesse de consolidation; pas de pièce primaire jointe visible. |
| Extraire la conversation | 9 messages utilisateur et 8 réponses assistant | Déclarations, analyses et propositions de montage vidéo; lien vers la transcription Fieldy dans Google Docs. |
| Prepare Hearing Evidence | 3 messages utilisateur et 2 réponses assistant; 2 archives téléchargées | Déclaration sur l’état des appareils, leur réparation et la récupération; anciens dossiers administratifs et sources préparés dans ChatGPT. |
| Harmony Movers Incident | 4 messages utilisateur et 4 réponses assistant | Deux récits initiaux, une demande de fusion recopiée d’une réponse assistant et une demande de traduction; les deux récits avaient déjà fait l’objet d’une extraction ciblée dans le dossier 08. |

La provenance, les URL, les empreintes et les séparateurs de dates affichés sont dans [COUVERTURE-REPRISE-CHATGPT-2026-10-24.json](COUVERTURE-REPRISE-CHATGPT-2026-10-24.json). Les séparateurs ne montrent ni l’année ni le fuseau: ceux-ci ne sont pas inventés.

Les fichiers `*-roles.json` distinguent les marqueurs utilisateur et assistant. **Les réponses de ChatGPT sont des analyses ou reformulations antérieures, pas des preuves indépendantes des faits racontés.** Le troisième message utilisateur de Harmony Movers Incident recopie des reformulations de ChatGPT: sa répétition ne constitue pas une corroboration supplémentaire.

## Extraction et limites

La conversation Extraire la conversation charge ses anciens messages en remontant. Deux lectures du texte affiché ont été conservées (`partie-initiale.txt` et `partie-finale.txt`), puis assemblées avec recouvrement contrôlé sur la demande « OK. Là, je veux que tu commences à bâtir » et la réponse du teaser. Le texte assemblé fait 57 461 caractères. Les autres extractions sont des lectures du fil affiché. Cela ne constitue pas un export natif de toutes les branches, versions ou sources du compte.

Le lien Google Docs est conservé comme piste de provenance de Fieldy. Le document lié n’a pas été ouvert dans ce sous-travail. La réponse assistant prétendant avoir réécouté l’audio et les chiffres de longueur du transcript ne sont pas validés par cette reprise. La source Fieldy déjà détenue conserve ses limites de transcription automatique.

Les vidéos et GIF de mise en scène proposés dans Extraire la conversation ne sont pas des enregistrements de l’événement; ils n’ont pas été téléchargés comme pièces probantes.

## Deux archives récupérées

- `99_Travail_et_collecte/Harmony_Dossier_Administratif_Complet.zip`: 435 entrées, 38 565 753 octets.
- `99_Travail_et_collecte/Harmony_Movers_Sources_et_Comptabilite.zip`: 415 entrées, 47 646 250 octets.

Les archives intégrales sont conservées localement dans OneDrive, sous `99_Travail_et_collecte`; elles ne sont pas diffusées dans le site parce qu’elles comprennent d’anciens scripts. Les PDF pertinents extraits et les contrôles de provenance restent accessibles dans le site. Le déplacement local a été contrôlé par empreinte SHA-256, sans modification des octets.

Elles ont été téléchargées depuis les boutons visibles de Prepare Hearing Evidence. Elles mélangent sources, extractions et analyses produites antérieurement. **Les 850 entrées ne sont pas 850 nouvelles pièces**: les deux archives se recoupent, et une partie des fichiers existe déjà dans les dossiers locaux.

Le [contrôle des archives](CONTROLE-ARCHIVES-CHATGPT.json) conserve l’empreinte de chaque entrée et les correspondances locales exactes. La comparaison trouve 63 entrées déjà identiques dans la première archive et 48 dans la seconde, sans prétendre que le reste est nouveau: noms, en-têtes, OCR et formats différents empêchent une simple égalité de fichiers. Aucun script présent dans ces archives n’a été exécuté.

Une recherche textuelle ciblée a été faite dans les 276 exports de courriels de la seconde archive. Elle donne 63 correspondances de termes, souvent dans des citations répétées, dont 35 identifiants sont déjà des noms de fichiers sous `03_Courriels`. Les 28 autres en-têtes et passages repérés concernent surtout la convention CINTEC de 2023/2024, la préparation de procédures et les rappels de facture de l’huissier. Les références à d’anciens camions U-Haul dans la convention ne prouvent pas la location du 12 juin 2025. Voir [RECHERCHE-ARCHIVES-CIBLEE.json](RECHERCHE-ARCHIVES-CIBLEE.json). Aucun export n’est présenté comme un EML original.

## Contrôle des PDF additionnels

Onze PDF sans copie locale de même empreinte ont été extraits dans `Pieces_extraites`. Le texte natif de toutes leurs pages a été lu. Les dix factures Frigo-Spec d’une page et la première page de la facture Rapide 2 Nette ont été contrôlées visuellement. Les rendus de contrôle restent localement dans `99_Travail_et_collecte/Controle_visuel`, à l’écart du site; les PDF sources extraits restent accessibles.

Les factures Frigo-Spec sont adressées à Quadro en juin/juillet **2024**: A245, A266, A267, A280 et A281. Elles comportent des variantes; A267 apparaît avec les dates du 10 et du 13 juillet, A281 avec le 15 et le 17 juillet, A266 avec des descriptions finales différentes. Les copies A245 et A280 présentent des empreintes différentes malgré des textes extraits identiques. **Ne pas additionner les versions ni les présenter comme une preuve de fonctionnement continu jusqu’en juin 2025.** Elles peuvent compléter le rapprochement des réparations antérieures, après comparaison aux pièces déjà réunies.

La facture Rapide 2 Nette no 45 est adressée à **Les Délices d’Aden**, au 5837 Jean-Talon Est, pour des services de juillet 2025. Elle n’est ni un bail de Quadro, ni un mandat de Remorquage Élite, ni une preuve de paiement U-Haul. Ce document est conservé pour éviter une attribution erronée. Voir [CONTROLE-FACTURES-ARCHIVES.json](CONTROLE-FACTURES-ARCHIVES.json).

## Apport aux huit demandes encore sans le document demandé

Cette reprise **ne fournit aucun des huit documents exacts manquants**. Les statuts des demandes 1, 6, 7, 9, 12, 18, 20 et 24 restent inchangés sur la seule base de cette recherche ChatGPT. Le [tableau d’apport](APPORT-AUX-HUIT-DEMANDES.json) précise chaque cas. Le constat ancien « quatre conversations bloquées » doit toutefois être actualisé: cette limite d’accès est maintenant levée.

Les récits de constats de l’huissier ne sont pas ses photos natives. L’intervention policière racontée ne remplace pas l’autorisation signée d’accès au rapport. L’inventaire global et les photographies évoquées ne donnent pas la liste du chargement U-Haul. Les citations juridiques et qualifications figurant dans les anciennes réponses assistant restent à l’écart des faits établis.

Les originaux, les déclarations et les analyses restent identifiés par leur provenance. Les doublons et les versions d’une facture ne s’additionnent pas. Toute extraction doit être contrôlée sur la pièce source. Les pièces à obtenir restent listées par demande.
