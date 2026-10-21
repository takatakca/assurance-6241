# Dossiers de travail pour l’avocat

[Ouvrir le site public](https://takatakca.github.io/assurance-6241/) · [État de publication](documentation/ETAT-PUBLICATION-GITHUB.md)

Le site rassemble trois dossiers : **6241 Léger**, **6280 Somerled NDG** et **HARMONY MOVERS**. Il permet la consultation, la recherche et le téléchargement des documents classés. Le tableau de bord Léger contient aussi une recherche dans les textes PDF/OCR et une chronologie attribuée aux sources. Le classeur comptable et le PowerPoint se téléchargent depuis les rubriques du dossier Léger.

## Provenance et couverture

Les originaux, les déclarations et les analyses sont identifiés par leur provenance. Les doublons et les versions d’une facture ne s’additionnent pas. Une extraction OCR reste à contrôler sur la pièce originale. Les documents à obtenir et les vérifications ouvertes figurent dans les synthèses de chaque dossier.

[Règles communes](docs/documentation/REGLES-COMMUNES.md). Les limites d’acquisition et les vérifications ouvertes figurent dans les synthèses de chaque dossier. Les positions des intervenants, les déclarations et les réponses ChatGPT ne sont pas automatiquement des faits établis. L’export Fieldy de 79 pages est identifié par un courriel de partage, mais son PDF n’a pas été acquis ni analysé intégralement dans cette publication.

## Travailler à distance

Les pièces publiées se trouvent dans **docs/**. Elles peuvent être consultées et téléchargées depuis le site ou GitHub. Les liens « Modifier sur GitHub » ouvrent la source avec les droits de votre compte GitHub; les collaborateurs doivent disposer des droits du dépôt pour y enregistrer leurs modifications.

Une modification d’un fichier Markdown sur GitHub ne régénère pas automatiquement son lecteur `.md.html`, la recherche ou les index. Une nouvelle génération et publication sont nécessaires. Le site n’a pas de serveur applicatif, de compte utilisateur propre ou de synchronisation automatique avec OneDrive. L’état de synchronisation OneDrive n’a pas été vérifié.

## Génération et publication

Les scripts, modèles et assets sont conservés dans **scripts/**. Le générateur statique Python utilise la bibliothèque standard. Les générateurs comptables et de présentation ont leurs dépendances précisées dans leurs sources.

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

Le paquet publié contient 1,761 fichiers, dont 1,539 sources sélectionnées et 115 lecteurs Markdown, pour environ 514.35 Mo. Le manifeste distingue sources, copies et pages générées; ces nombres ne sont pas des nombres de preuves distinctes.

[Commit du paquet documentaire](https://github.com/takatakca/assurance-6241/commit/9aff96e5b7e741149062fb86dc239aab3ada247d). Le hub, les trois entrées de dossier, un PDF et un courriel EML ont répondu HTTP 200 avec des empreintes identiques au paquet local le 2026-10-21T19:46:17.401857+00:00. Les vérifications ne constituent pas une attestation d’exhaustivité de tous les comptes courriel ou ChatGPT.
