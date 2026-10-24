# Copie statique pour GitHub Pages

`python scripts/build_remote_site.py --audit-only` prépare et contrôle la publication en mémoire. Après stabilisation de la collecte et régénération des index locaux, `python scripts/build_remote_site.py --build` écrit `dist-site/`. Ce répertoire est exclu du dépôt de travail par `.gitignore`; il contient le paquet statique à publier séparément par le responsable du déploiement. Ces deux commandes de génération ne transmettent aucun fichier au réseau.

Le générateur de publication utilise seulement la bibliothèque standard Python. Les sources restent intactes. Les trois dossiers sont copiés avec leurs chemins; `index.html` reprend le lanceur `OUVRIR-LES-DOSSIERS.html`, `.nojekyll` désactive Jekyll, et les textes Markdown conservent leur original avec une version lisible `.md.html`. Les lecteurs et la navigation fonctionnent sous un préfixe de dépôt, sans chemins absolus de domaine, sans serveur ni connexion à un service tiers. Les PDF et images sont consultables par le navigateur; les fichiers Office restent téléchargeables et modifiables avec une application compatible.

Le dossier maître `00_DOSSIER_MAITRE/` apporte une table des matières, des vues de lecture et une recherche dans les textes disponibles des trois dossiers. Les mots, expressions entre guillemets, dossiers et formats peuvent être recherchés; chaque résultat conserve sa provenance et son lien vers la pièce. Les pages sans texte extrait peuvent seulement être retrouvées par leur nom. Les données sont chargées par des scripts locaux afin de fonctionner aussi depuis OneDrive sans serveur. La recherche porte sur l’index daté; elle ne prouve pas l’exhaustivité des comptes courriel ni des pièces.

Le maître est produit par `scripts/build_master_corpus.py`, puis `scripts/build_master_workspace.py`, avec les modèles `scripts/master/*.js` et `scripts/master/*.css`. Exécuter ces commandes après la stabilisation des sources et avant le générateur de publication; le second maintient le lanceur commun. Ne pas exécuter l’ancien `scripts/build_dossier_hub.py` dans ce cycle : il remplacerait ce lanceur et le contrôle des modifications extérieures interromprait la génération suivante. Le corpus d’extraction peut nécessiter les bibliothèques documentaires indiquées dans le script.

```sh
python scripts/build_master_corpus.py
python scripts/build_master_workspace.py
python scripts/site/test_reader_navigation.py
python scripts/site/test_master_publication.py
python scripts/site/verify_reader_navigation.py
python scripts/site/verify_remote_site.py
python scripts/build_remote_site.py --audit-only
python scripts/build_remote_site.py --build
```

Les HTML, CSS, JavaScript et données du maître sont copiés sans transformation de leur interface ni seconde CSP. Les deux fichiers `06_Index_recherche/corpus.json` et `07_Controle_des_sources/CONTROLE-DU-MAITRE.json` restent locaux. Les fichiers de recherche JavaScript publiés passent le même contrôle de signatures de secrets que les autres textes; leur syntaxe est vérifiée avec Node, et leurs liens HTML sont inclus dans l’audit général. Les Markdown de `04_Remise_et_suivis/` disposent aussi de lecteurs `.md.html`.

Les index HTML historiques deviennent des lecteurs sans code actif; leur source est conservée avec le suffixe `.source.txt`. Les liens d’archive déplacés sont rapprochés uniquement si une correspondance de suffixe existe et si toutes les copies candidates ont le même SHA-256. Une référence absente ou ambiguë est signalée visiblement, sans créer un faux lien.

Le rendu Markdown prend en charge titres, tableaux, paragraphes, listes, citations, liens, images locales, emphase et blocs de code. Il échappe le HTML brut. Les mises en page Markdown complexes peuvent être simplifiées; le téléchargement de la source reste disponible. Les liens de téléchargement ne sont pas remplacés par les lecteurs HTML.

Les caches et `99_Travail_et_collecte/` sont exclus. Les textes OCR, leurs manifestes et les originaux classés sont conservés. Les noms de fichiers de clés/identifiants de service sont exclus et les textes sont contrôlés pour des signatures précises de clés privées et jetons courants; une détection interrompt la génération avant copie. Ce contrôle n’est pas une qualification juridique des pièces ni une certification d’absence de tout secret possible.

Contrôles reproductibles : `python scripts/site/verify_remote_site.py` pour les liens, CSP et scripts, `python scripts/site/verify_reader_navigation.py` pour les destinations de lecture et ancres réelles. Les résultats et l’audit complet sont dans `scripts/.build-livrables/remote-site-validation.json`, `reader-navigation-validation.json` et `remote-site-audit.json`. Ces contrôles construisent en mémoire sans écrire `dist-site/`. Avant publication, contrôler la taille du paquet, la liste des exclusions et les références indisponibles. La limite officielle GitHub Pages est [1 Go par site publié](https://docs.github.com/fr/pages/getting-started-with-github-pages/github-pages-limits).

Le générateur refuse d’écraser un répertoire de sortie contenant des fichiers non gérés. Il supprime uniquement d’anciens fichiers listés dans son manifeste, à l’intérieur de `dist-site`, puis vérifie que les sources n’ont pas changé pendant la copie. Il ne modifie aucun des générateurs locaux existants.

La génération et la copie de publication sont incrémentales : un fichier déjà présent dont le SHA-256 correspond au contenu attendu n’est pas réécrit. Les empreintes sont toujours recalculées; la validation finale et la détection de modifications distantes restent actives. Une modification ou suppression d’une pièce publiée doit être réconciliée avant remplacement. Les reçus indiquent les fichiers et octets recopiés ou conservés.

La consultation, la recherche et le téléchargement fonctionnent sur le site public. Les liens « Modifier sur GitHub » nécessitent un compte autorisé à modifier le dépôt. Une modification Markdown ne régénère pas automatiquement sa page `.md.html`, ni les index : une nouvelle génération et publication sont nécessaires. Il n’y a pas de synchronisation automatique avec OneDrive.

Les outils de publication sont distincts et utilisent le dépôt existant `takatakca/assurance-6241` : `publish_remote_site.py` vérifie le manifeste, copie vers le clone `.publish-repo/docs`, puis effectue un commit et un push ordinaires; `configure_github_pages.py --configure` règle uniquement GitHub Pages sur `main` et `/docs`. Les identifiants proviennent du gestionnaire officiel Git et ne sont pas enregistrés par ces scripts. `verify_static_transport.py` teste le transport HTTP local; `verify_public_site.py` compare le hub, les trois entrées de dossier et un PDF publics aux empreintes du paquet local.

Lorsqu’ils sont présents, les contrôles publics incluent également l’entrée de remise Dufourd, son PDF et son ZIP, le bilan des compléments, les états financiers et la déclaration fiscale nouvellement acquis. Le guide publié reprend les nombres de pages, annexes et statuts depuis `CONTROLES-DU-DOSSIER.json`, après vérification de l’empreinte du PDF; aucun ancien compteur n’est conservé en dur.
