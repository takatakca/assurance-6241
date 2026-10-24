# Dossiers de travail pour l’avocat

[Ouvrir le site public](https://takatakca.github.io/assurance-6241/) · [État de publication](documentation/ETAT-PUBLICATION-GITHUB.md)

Le site rassemble trois dossiers : **6241 Léger**, **6280 Somerled NDG** et **HARMONY MOVERS**. Il permet la consultation, la recherche et le téléchargement des documents classés. Le tableau de bord Léger contient aussi une recherche dans les textes PDF/OCR et une chronologie attribuée aux sources. Le classeur comptable et le PowerPoint se téléchargent depuis les rubriques du dossier Léger.

La [remise documentaire Dufourd](https://takatakca.github.io/assurance-6241/HARMONY%20MOVERS/12_Remise_Dufourd_2026-10-21/LIRE-EN-PREMIER.md.html) rassemble les réponses préparées, les pièces annexées et les téléchargements disponibles. Elle distingue les pièces disponibles et les vérifications ouvertes; la publication ne signifie pas que les documents ont été envoyés au cabinet. Le PDF compte 100 pages et le bordereau 312 annexes distinctes. La matrice indique 5 documents demandés disponibles, 17 réponses partielles et 3 documents demandés non repérés. Ces catégories décrivent la disponibilité documentaire.

Le [bilan de la recherche complémentaire](https://takatakca.github.io/assurance-6241/HARMONY%20MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md.html) présente les pièces nouvelles, leur provenance et les documents encore manquants. Les états financiers, données de plateformes, déclarations fiscales et devis ne sont pas assimilés à un dommage net démontré. Le [bilan du 24 octobre 2026](https://takatakca.github.io/assurance-6241/HARMONY%20MOVERS/14_Recherche_complementaire_2026-10-24/BILAN-DE-LA-RECHERCHE.md.html) documente la reprise des recherches dans les deux boîtes courriel et les quatre conversations ChatGPT désormais accessibles. Les déclarations et analyses récupérées restent distinctes des pièces originales; les demandes sans document suffisant restent indiquées. Les archives de collecte contenant d’anciens scripts sont conservées localement dans OneDrive; les extraits pertinents et leur provenance sont publiés.

## Provenance et couverture

Les originaux, les déclarations et les analyses sont identifiés par leur provenance. Les doublons et les versions d’une facture ne s’additionnent pas. Une extraction OCR reste à contrôler sur la pièce originale. Les documents à obtenir et les vérifications ouvertes figurent dans les synthèses de chaque dossier.

[Règles communes](docs/documentation/REGLES-COMMUNES.md). Les limites d’acquisition et les vérifications ouvertes figurent dans les synthèses de chaque dossier. Les positions des intervenants, les déclarations et les réponses ChatGPT ne sont pas automatiquement des faits établis. Le PDF Fieldy est acquis et publié : 79 pages, dont 79 avec du texte natif extrait. L’original, l’extraction paginée et les analyses attribuées sont accessibles dans `HARMONY MOVERS/11_Fieldy/`. Le texte n’a pas été corrigé; l’audio et l’attribution des locuteurs ne sont pas confirmés par cette extraction.

## Travailler à distance

Les pièces publiées se trouvent dans **docs/**. Elles peuvent être consultées et téléchargées depuis le site ou GitHub. Les liens « Modifier sur GitHub » ouvrent la source avec les droits de votre compte GitHub; les collaborateurs doivent disposer des droits du dépôt pour y enregistrer leurs modifications.

Une modification d’un fichier Markdown sur GitHub ne régénère pas automatiquement son lecteur `.md.html`, la recherche ou les index. Une nouvelle génération et publication sont nécessaires. Le site n’a pas de serveur applicatif, de compte utilisateur propre ou de synchronisation automatique avec OneDrive. L’état de synchronisation OneDrive n’a pas été vérifié.

## Génération et publication

Les scripts, modèles et assets sont conservés dans **scripts/**. Le générateur statique Python utilise la bibliothèque standard. Les générateurs comptables et de présentation ont leurs dépendances précisées dans leurs sources.

La remise Dufourd est reproductible avec `scripts/build_remise_dufourd.py` et les entrées de `scripts/remise-dufourd/`. Son PDF utilise ReportLab et les polices Arial installées sous Windows; adapter ces chemins de polices sur un autre système. Après toute nouvelle génération, contrôler visuellement le PDF et actualiser `controle-visuel.json` avec son empreinte réelle avant d’exécuter `scripts/finalize_remise_dufourd.py` (dépendance : pypdf). Ce dernier vérifie les annexes et crée le ZIP. Le contrôle visuel fourni correspond au PDF publié, pas à une future version modifiée.

Les commandes suivantes s’exécutent depuis un **espace source** contenant à sa racine `6241 Léger/`, `6280 Somerled NDG/`, `HARMONY MOVERS/`, `documentation/` et `scripts/`, comme le dossier de travail OneDrive. Cette disposition diffère du répertoire **docs/** du clone publié; conserver les originaux et les manifestes lors de la préparation d’un nouvel espace source. Les lecteurs `.md.html` et les index de répertoires sont des sorties générées.

```sh
python scripts/build_case_portal.py
python scripts/build_dossier_hub.py
python scripts/build_remote_site.py --audit-only
python scripts/build_remote_site.py --build
python scripts/site/verify_static_transport.py
```

Le paquet `dist-site/` est contrôlé avant publication. [Les outils de publication](scripts/site/README.md) décrivent la copie vers `docs/` du clone `.publish-repo`, le commit et le push ordinaires, puis les contrôles HTTP. GitHub Pages sert la branche **main**, dossier **/docs**. Réconcilier les modifications faites à distance avant de remplacer une publication; le script refuse d’écraser des documents modifiés depuis le dernier manifeste.

## Publication vérifiée

Le paquet publié contient 3,174 fichiers, dont 2,820 sources sélectionnées et 156 lecteurs Markdown, pour environ 767.20 Mo. Le manifeste distingue sources, copies et pages générées; ces nombres ne sont pas des nombres de preuves distinctes.

[Commit du paquet documentaire](https://github.com/takatakca/assurance-6241/commit/73e028a1d00f36162244b9e60f406df9af77ab7e). Le hub, les trois entrées de dossier, un PDF et un courriel EML ont répondu HTTP 200 avec des empreintes identiques au paquet local le 2026-10-24 à 02:08 EDT. La vérification couvre également l’entrée de la remise Dufourd, son PDF et une archive ZIP. Les vérifications ne constituent pas une attestation d’exhaustivité de tous les comptes courriel ou ChatGPT.
