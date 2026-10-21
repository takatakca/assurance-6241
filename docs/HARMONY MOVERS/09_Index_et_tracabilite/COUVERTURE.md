# Couverture et méthode — 21 octobre 2026

**Archive locale** : 179 fichiers inventoriés dans `6241 Léger/10_Archive_avocat_2026-10-05`; 178 copiés, 1 exclu (rapport 18757 lié à CINTEC). Sources conservées. 43 fichiers d'analyses/index antérieurs sont séparés des 135 autres fichiers. 7 répétitions SHA256 sont indiquées sans suppression. Les PDF d'un même numéro de facture ayant des empreintes différentes restent distincts.

- [Inventaire de copie CSV](inventaire-copies.csv) et [JSON](inventaire-copies.json) : chemin source, destination, taille, SHA256, doublon exact et statut.
- [Extraction PDF](extraction-pdf-index.json) : texte natif de 37 PDF uniques. Un fichier texte vide ou incompréhensible ne vaut pas lecture du PDF. Le nombre de caractères inclut les marqueurs de page.
- L'OCR global associé aux sources est disponible dans [le manifeste du dossier Léger](<../../6241 Léger/09_Index_et_tracabilite/Texte_et_OCR/manifest-extraction.json>). Moteur anglais en-US appliqué à du français : chiffres, noms, négations et dates à contrôler sur l'image. DII janvier pages 5–6 contrôlées visuellement pour les montants du portrait.

**Gmail Takatak** : requête `("Harmony Movers" OR "500-17-136442-251" OR "CWIQUWOL" OR "dufourdion.com")`. Deux pages renvoient 189 candidats; absence de page suivante à la fin de cette requête. Cela ne garantit pas que tous les courriels pertinents contiennent ces termes. Des faux positifs du cabinet et des anciennes affaires sont présents.

- [189 candidats](../03_Courriels/takatak.ca@gmail.com/recherche-candidats-index.json).
- [189 messages récupérés](../03_Courriels/takatak.ca@gmail.com/messages-lus-index.json), textes dérivés et sept lots MIME conservés. La reprise ajoute 136 messages; chaque affirmation n’est pas pour autant vérifiée.
- Recherche et lectures en lecture seule : aucun envoi, brouillon, changement d'étiquette, déplacement ou suppression.
- Les textes conservent les chaînes transférées. Date d'en-tête = message capturé; date citée = message antérieur; ni l'une ni l'autre n'établit automatiquement la date d'un fait.
- L'index MIME décrit les pièces jointes; leur présence dans l'index ne signifie pas qu'elles ont toutes été téléchargées.

**Gmail Oeuf** : quatre originaux EML du 20 octobre 2026 et six factures PDF obtenus par le parent, indexés avec leurs SHA dans [manifest-originaux.json](../03_Courriels/Originaux_ooeuf_2026-10-20/manifest-originaux.json). Une chaîne 6–20 octobre provenant de la collecte Léger est aussi citée dans le portrait.

**ChatGPT Harmony** : cinq titres et identifiants repérés dans l'interface du projet. La tentative initiale `read_thread` est conservée et mentionne la limitation « Too many requests ». **Une conversation lue : Harmony Movers Incident**, dont les deux récits utilisateur initiaux sont transcrits dans une [note sourcée](../08_Conversations_ChatGPT/Harmony-Movers-Incident-lecture-source.md). Quatre messages utilisateur et quatre réponses assistant ont été consultés, mais seuls les deux premiers récits sont intégralement transcrits; aucun export exhaustif ou de pièces jointes n'est revendiqué. **Quatre autres conversations ont été tentées par l'agent principal dans le navigateur intégré et ont échoué au chargement**, avec le texte « Could not load this ChatGPT conversation » et « Unable to load history ». Un essai « Try again » sur Finaliser dossier Harmony Movers a également échoué. La cause de ces erreurs d'interface est inconnue; elles ne sont pas assimilées à la limite du connecteur. Les analyses antérieures locales ne remplacent pas les exports de ces conversations. [Index ChatGPT](../08_Conversations_ChatGPT/conversations-index.json), [tentatives](../08_Conversations_ChatGPT/TENTATIVES-CHARGEMENT-2026-10-21.md) et [différence d'accès entre agents](../08_Conversations_ChatGPT/ACCES-NAVIGATEUR-2026-10-21.md).

**Traçabilité et limites** : une empreinte confirme l'identité binaire des copies, pas l'authenticité ou la véracité du document. Le portrait n'affirme pas que des fonds ont été encaissés sans pièce de paiement. Les arguments juridiques des parties sont attribués, sans les adopter comme décisions. Le statut judiciaire actuel demande des actes et ordonnances récents.

## Reprise du 21 octobre

[23 pièces originales supplémentaires et contrôles](REPRISE-2026-10-21.md), dont 14 PDF, quatre EML, deux XLS et trois JPG. 23 empreintes contrôlées; 17 pages scannées avec OCR anglais à vérifier. Les 634 occurrences MIME incluent des répétitions et ne correspondent pas à 634 téléchargements. Le PDF Fieldy récent est suivi séparément dans [11_Fieldy](../11_Fieldy/).

**Fieldy — nouveau repérage** : courriel original de partage acquis séparément (21 octobre, 14:59:58 -04:00, identifiant 1a15fd5a4ddf7dfb), sans pièce jointe. Lien Adobe identifié; 79 pages et 423 672 octets affichés, mais PDF non acquis et lecture intégrale non effectuée. [Provenance et SHA du courriel](../11_Fieldy/provenance-export-2026-10-21.json). Le bordereau préparatoire pour le cabinet référence 23 groupes et 58 fichiers disponibles; il ne déclare aucun engagement clos.
