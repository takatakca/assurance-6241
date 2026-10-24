"""Publish generator sources and a factual access guide after live HTTP checks pass."""
from pathlib import Path
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import importlib.util, json, shutil

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('publisher',ROOT/'scripts/site/publish_remote_site.py')
publisher=importlib.util.module_from_spec(spec);spec.loader.exec_module(publisher)
REPO=publisher.REPO

def main():
    publication=json.loads((ROOT/'scripts/.build-livrables/publication-result.json').read_text(encoding='utf-8'))
    live=json.loads((ROOT/'scripts/.build-livrables/public-site-verification.json').read_text(encoding='utf-8'))
    manifest=json.loads((ROOT/'dist-site/.site-build.json').read_text(encoding='utf-8'))
    if not publication.get('ok') or not live.get('ok'):raise RuntimeError('Publication and public HTTP verification must succeed first')
    if publisher.text('remote','get-url','origin') not in publisher.ALLOWED_REMOTES:raise RuntimeError('Unexpected remote')
    if publisher.text('symbolic-ref','--short','HEAD')!='main' or publisher.git('status','--porcelain').stdout:raise RuntimeError('Expected a clean main branch')
    publisher.git('pull','--ff-only','origin','main')
    live_url=live['base_url'];commit=publication['commit']
    live_label=datetime.fromisoformat(live['as_of']).astimezone(ZoneInfo('America/New_York')).strftime('%Y-%m-%d à %H:%M %Z')
    rule=manifest['rules']
    fieldy_pdf='HARMONY MOVERS/11_Fieldy/2026-10-05-Fieldy-interrogatoire-Quadro-Harmony.pdf'
    fieldy_note='L’export Fieldy de 79 pages est identifié par un courriel de partage, mais son PDF n’a pas été acquis ni analysé intégralement dans cette publication.'
    if fieldy_pdf in manifest['output_hashes']:
        acquisition=json.loads((ROOT/'dist-site/HARMONY MOVERS/11_Fieldy/acquisition-pdf.json').read_text(encoding='utf-8'))
        if acquisition['sha256']!=manifest['output_hashes'][fieldy_pdf]:raise RuntimeError('Fieldy acquisition hash differs from the published PDF')
        fieldy_note=f"Le PDF Fieldy est acquis et publié : {acquisition['pages']} pages, dont {acquisition['nonempty_pages']} avec du texte natif extrait. L’original, l’extraction paginée et les analyses attribuées sont accessibles dans `HARMONY MOVERS/11_Fieldy/`. Le texte n’a pas été corrigé; l’audio et l’attribution des locuteurs ne sont pas confirmés par cette extraction."
    remise_note=''
    remise='HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/'
    if remise+'LIRE-EN-PREMIER.md.html' in manifest['output_hashes']:
        remise_url=live_url+'HARMONY%20MOVERS/12_Remise_Dufourd_2026-10-21/LIRE-EN-PREMIER.md.html'
        remise_note=f"La [remise documentaire Dufourd]({remise_url}) rassemble les réponses préparées, les pièces annexées et les téléchargements disponibles. Elle distingue les pièces disponibles et les vérifications ouvertes; la publication ne signifie pas que les documents ont été envoyés au cabinet."
        control_path=ROOT/'dist-site'/remise/'CONTROLES-DU-DOSSIER.json'
        if control_path.is_file():
            control=json.loads(control_path.read_text(encoding='utf-8'))
            if control.get('pdf_sha256')!=manifest['output_hashes'].get(remise+'REPONSES-AUX-25-DEMANDES.pdf'):
                raise RuntimeError('Remise control does not match the published PDF')
            counts=control['statuts']
            remise_note+=f" Le PDF compte {control['pdf_pages']} pages et le bordereau {control['annexes_uniques']} annexes distinctes. La matrice indique {counts.get('document_disponible',0)} documents demandés disponibles, {counts.get('partiel',0)} réponses partielles et {counts.get('non_repere',0)} documents demandés non repérés. Ces catégories décrivent la disponibilité documentaire."
    complements_note=''
    complements='HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md.html'
    if complements in manifest['output_hashes']:
        complements_url=live_url+'HARMONY%20MOVERS/13_Complements_Dufourd_2026-10-21/BILAN-DE-LA-RECHERCHE.md.html'
        complements_note=f"Le [bilan de la recherche complémentaire]({complements_url}) présente les pièces nouvelles, leur provenance et les documents encore manquants. Les états financiers, données de plateformes, déclarations fiscales et devis ne sont pas assimilés à un dommage net démontré."
    latest='HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/BILAN-DE-LA-RECHERCHE.md.html'
    if latest in manifest['output_hashes']:
        latest_url=live_url+'HARMONY%20MOVERS/14_Recherche_complementaire_2026-10-24/BILAN-DE-LA-RECHERCHE.md.html'
        complements_note+=f" Le [bilan du 24 octobre 2026]({latest_url}) documente la reprise des recherches dans les deux boîtes courriel et les quatre conversations ChatGPT désormais accessibles. Les déclarations et analyses récupérées restent distinctes des pièces originales; les demandes sans document suffisant restent indiquées. Les archives de collecte contenant d’anciens scripts sont conservées localement dans OneDrive; les extraits pertinents et leur provenance sont publiés."
    remise_checks=[c['path'] for c in live['checks'] if c['path'].startswith(remise) and c.get('ok')]
    remise_checked=(remise+'LIRE-EN-PREMIER.md.html' in remise_checks and any(p.endswith('.pdf') for p in remise_checks) and any(p.endswith('.zip') for p in remise_checks))
    checked_note=' La vérification couvre également l’entrée de la remise Dufourd, son PDF et une archive ZIP.' if remise_checked else ''
    readme=f'''# Dossiers de travail pour l’avocat

[Ouvrir le site public]({live_url}) · [État de publication](documentation/ETAT-PUBLICATION-GITHUB.md)

Le site rassemble trois dossiers : **6241 Léger**, **6280 Somerled NDG** et **HARMONY MOVERS**. Il permet la consultation, la recherche et le téléchargement des documents classés. Le tableau de bord Léger contient aussi une recherche dans les textes PDF/OCR et une chronologie attribuée aux sources. Le classeur comptable et le PowerPoint se téléchargent depuis les rubriques du dossier Léger.

{remise_note}

{complements_note}

## Provenance et couverture

{rule}

[Règles communes](docs/documentation/REGLES-COMMUNES.md). Les limites d’acquisition et les vérifications ouvertes figurent dans les synthèses de chaque dossier. Les positions des intervenants, les déclarations et les réponses ChatGPT ne sont pas automatiquement des faits établis. {fieldy_note}

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

Le paquet publié contient {manifest['published_files']:,} fichiers, dont {manifest['source_files']:,} sources sélectionnées et {manifest['markdown_readers']} lecteurs Markdown, pour environ {publication['bytes']/1_000_000:.2f} Mo. Le manifeste distingue sources, copies et pages générées; ces nombres ne sont pas des nombres de preuves distinctes.

[Commit du paquet documentaire](https://github.com/takatakca/assurance-6241/commit/{commit}). Le hub, les trois entrées de dossier, un PDF et un courriel EML ont répondu HTTP 200 avec des empreintes identiques au paquet local le {live_label}.{checked_note} Les vérifications ne constituent pas une attestation d’exhaustivité de tous les comptes courriel ou ChatGPT.
'''
    status=f'''# État de publication GitHub

Vérification : {live_label} (America/New_York).

- [Site public]({live_url})
- [Dépôt public](https://github.com/takatakca/assurance-6241)
- [Commit du paquet documentaire](https://github.com/takatakca/assurance-6241/commit/{commit})
- Source GitHub Pages : branche `main`, répertoire `/docs`.
- Fichiers publiés : {manifest['published_files']}; sources sélectionnées : {manifest['source_files']}; volume réel incluant le manifeste : {publication['bytes']:,} octets.
- Plus gros fichier : {manifest['largest_files'][0]['bytes']:,} octets.
- Liens générés contrôlés : {manifest['static_links_checked']}; liens cassés : 0.
- Contrôles HTTP publics : {len(live['checks'])} réussis, avec comparaison SHA-256 du hub, des trois entrées de dossier, d’un PDF et d’un EML.{checked_note}

Les pièces, courriels, textes OCR, classeur, présentation, index et synthèses sélectionnés sont désormais dans `docs/`. Les originaux de travail restent dans le dossier local; la copie publiée est distincte. `.gitattributes` impose `docs/** -text` pour préserver les octets et les empreintes des documents.

Le site permet consultation, recherche et téléchargement. Les modifications passent par GitHub authentifié ou l’espace source, puis une nouvelle génération/publication. Modifier un Markdown ne met pas automatiquement à jour son lecteur HTML ni les index. Il n’y a pas de synchronisation automatique avec OneDrive.

{rule}

{fieldy_note} Les limites de couverture sont conservées dans les synthèses; la publication n’implique pas que tous les échanges et toutes les pièces possibles ont été obtenus.

{remise_note}

{complements_note}
'''
    (ROOT/'README.md').write_text(readme,encoding='utf-8')
    (ROOT/'documentation/ETAT-PUBLICATION-GITHUB.md').write_text(status,encoding='utf-8')
    selected=[ROOT/'README.md',ROOT/'documentation/ETAT-PUBLICATION-GITHUB.md',ROOT/'documentation/REGLES-COMMUNES.md']
    selected += [p for p in (ROOT/'scripts').iterdir() if p.is_file() and p.suffix in {'.py','.mjs','.ps1','.html'}]
    selected += [p for p in (ROOT/'scripts/site').iterdir() if p.is_file() and p.suffix in {'.py','.mjs','.js','.css','.md'}]
    selected += sorted((ROOT/'scripts/remise-dufourd').glob('*.json'))
    for source in selected:
        dest=REPO/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
    ignore='dist-site/\n.publish-repo/\nscripts/.build-livrables/\nscripts/**/__pycache__/\n'
    (REPO/'.gitignore').write_text(ignore,encoding='utf-8')
    publisher.git('add','--','README.md','documentation','scripts','.gitignore')
    staged=publisher.git('diff','--cached','--name-only','-z').stdout.decode('utf-8').split('\0')
    allowed=lambda p:p in {'README.md','.gitignore'} or p.startswith(('scripts/','documentation/'))
    if any(p and not allowed(p) for p in staged):raise RuntimeError('Unexpected staged documentation path')
    if any(staged):
        config=[]
        if not publisher.git('config','user.name',allowed=(0,1)).stdout.strip():config+=['-c','user.name=Dossier 6241 automation']
        if not publisher.git('config','user.email',allowed=(0,1)).stdout.strip():config+=['-c','user.email=noreply@github.com']
        publisher.git(*config,'commit','-m','Documenter l’accès distant et sauvegarder les générateurs du site')
    final=publisher.text('rev-parse','HEAD');publisher.git('push','origin','main')
    if publisher.text('ls-remote','origin','refs/heads/main').split()[0]!=final:raise RuntimeError('Remote commit mismatch')
    result={'ok':True,'commit':final,'commit_url':'https://github.com/takatakca/assurance-6241/commit/'+final,
            'documentation_files':len(selected)+1,'site_url':live_url,'documentary_commit':commit}
    (ROOT/'scripts/.build-livrables/publication-documentation-result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))

if __name__=='__main__':
    try:main()
    except (OSError,ValueError,RuntimeError) as exc:
        print(json.dumps({'ok':False,'error':str(exc),'credential_output':'not retained'}));raise SystemExit(1)
