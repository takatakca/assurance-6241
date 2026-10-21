# Couverture et traçabilité — passe du 21 octobre 2026

## Sources effectivement traitées

Compte connecté confirmé : **takatak.ca@gmail.com**. Cinq recherches sont consignées dans [recherches-effectuees.json](recherches-effectuees.json), incluant Somerled/Summerlet, 6280/6284, Bar Sora, Nathalie/Barcera, propane, MAPAQ, résiliation et Romanowski. Chaque réponse retournait un jeton de page suivant nul. Les résultats se chevauchent et comprennent des faux positifs; leurs nombres ne doivent pas être additionnés.

**22 messages / 13 fils** sont conservés en JSON avec en-têtes sélectionnés et texte MIME exact. **4 messages de 2 fils supplémentaires** sont représentés par des extraits ciblés Interac, sans liens permettant d'encaisser. **2 messages RFC originaux** (.eml) sont conservés. Au total, **26 messages distincts / 15 fils ont été lus**, mais seuls 22 sont conservés intégralement en texte. Période des messages conservés : 1er décembre 2025 au 15 octobre 2026.

Les messages annoncent **37 occurrences de PJ**, soit **19 combinaisons nom/taille**. **19 pièces originales** sont conservées : 14 PDF, 3 DOCX, 1 PNG et 1 JPG. La pièce 1000144788.jpg (426 410 octets) a été récupérée lors de la reprise du 21 octobre, après la limite de requêtes initiale. Elle a été contrôlée visuellement et traitée par OCR.

Les rapprochements entre les autres occurrences d'une même pièce utilisent **nom et taille**, pas une supposition d'identité binaire. Les SHA-256 certifient la stabilité locale des fichiers conservés, pas l'authenticité juridique de leur contenu.

## Texte, OCR et vérification

Les 14 PDF représentent **218 pages**, dont des répétitions de police dans les assemblages de transmission. Extraction locale avec pypdf : texte page par page enregistré dans Texte_et_OCR. Une extraction textuelle a été produite pour chaque page après téléchargement; les aperçus du connecteur, parfois tronqués, n’ont pas servi de preuve d’extraction complète. La présence de texte extrait ne garantit pas que tous les éléments graphiques, annotations ou écritures manuscrites soient transcrits.

L'avis de résiliation, une page image sans texte, a été rendu avec Poppler, reconnu par Windows OCR et **contrôlé visuellement** : identité, date manuscrite 14 septembre, échéance 31 octobre, signature et description contractuelle. L'OCR automatique reste séparé des observations de contrôle.

Contrôles visuels supplémentaires : projet consolidé pages 1 et 5 (statut projet/champs vides), certificat hotte page 1 (nom/signature/cachet vides), police pages 3 et 7 (relevé et tableau), image 3.png (modèle d'enseigne). Les autres pages disposent d'extraction textuelle mais n'ont pas toutes été contrôlées visuellement.

Le contrat DOCX a été extrait depuis le message RFC original; son XML contient les cases de signature vierges. Les deux variantes Word du 21 septembre ont également été récupérées depuis le RFC original, malgré l'absence de prise en charge directe de leurs pièces octet-stream.

### Bilan par page vérifié le 21 octobre 2026

**217 pages disposent d’une couche texte existante extraite avec pypdf; 1 page sans texte a nécessité l’OCR; 0 page des 218 PDF téléchargées reste sans extraction textuelle connue.** « Couche texte existante » décrit le mécanisme constaté : l’origine native du texte ou un éventuel OCR antérieur n’a pas été authentifiée.

L’unique page nécessitant l’OCR détectée est la page 1 de **Avis_resiliation_cuisine_Quadro_FINAL（signature）.pdf**. L’OCR a produit 1 831 caractères mais comporte des erreurs, notamment 9054-0233 au lieu de 9054-0238 et une date manuscrite mal reconnue. La lecture visuelle de l’original confirme 9054-0238 et le 14 septembre 2026; ces corrections sont prises en compte dans la synthèse, sans modifier l’OCR brut.

**6 pages PDF ont été contrôlées visuellement; les 212 autres n’ont pas bénéficié de cette validation.** Il ne s’agit donc pas d’une certification de transcription exhaustive des 218 pages. Le compteur zéro concerne seulement les pages du corpus PDF effectivement téléchargé; il ne couvre ni les autres comptes ou conversations restant à recueillir.

| PDF (préfixe de message omis) | Pages | Couche texte extraite | OCR effectué | Sans extraction connue |
| --- | ---: | ---: | ---: | ---: |
| TRANSMISSION_PREUVE_ASSURANCE_QUADRO_HOLDINGS_SANS_LIENS_2026-09-10.pdf | 62 | 62 | 0 | 0 |
| Avis_resiliation_cuisine_Quadro_FINAL（signature）.pdf | 1 | 0 | 1 | 0 |
| Certificat_nettoyage_hotte_Rapid2Net_2026-09-14.pdf | 1 | 1 | 0 | 0 |
| LOCAL_6280_MISE_EN_DEMEURE_CONSOLIDEE_MAPAQ_21_SEPT_2026.pdf | 5 | 5 | 0 | 0 |
| LOCAL_6280_Mise_en_demeure_Quadro_BAR_SORA_20_septembre_2026.pdf | 3 | 3 | 0 | 0 |
| LOCAL_6280_NOTE_CONFIDENTIELLE_AVOCAT_21_SEPT_2026.pdf | 2 | 2 | 0 | 0 |
| MISE_EN_DEMEURE_Quadro_BAR_SORA_ACCUSÉ_RECEPTION_2026-09-10.pdf | 6 | 6 | 0 | 0 |
| Mise_en_demeure_Quadro_Holdings_Bar_Sora.pdf | 3 | 3 | 0 | 0 |
| MISE_EN_DEMEURE_Quadro_Holdings_Ltee_c_BAR_SORA_2026-09-10.pdf | 7 | 7 | 0 | 0 |
| MISE_EN_DEMEURE_Quadro_Holdings_Ltee_c_BAR_SORA_CORRIGEE_2026-09-10.pdf | 5 | 5 | 0 | 0 |
| Nouvelle affaire 2026-27(1).pdf | 59 | 59 | 0 | 0 |
| Suivi_mise_en_demeure_interruption_propane.pdf | 1 | 1 | 0 | 0 |
| Suivi_mise_en_demeure_propane_style_formel.pdf | 1 | 1 | 0 | 0 |
| TRANSMISSION_PREUVE_ASSURANCE_QUADRO_HOLDINGS_2026-09-10.pdf | 62 | 62 | 0 | 0 |

Détail vérifiable : [couverture-extraction-pages.json](couverture-extraction-pages.json), [index initial d’extraction](Texte_et_OCR/extraction-index.json), [résultat OCR](Texte_et_OCR/Rendus/ocr-resultats.json) et [notes de contrôle visuel](CONTROLE-VISUEL.md).

## Couverture restant ouverte

- **ChatGPT :** dix liens repérés par l'agent principal, contenus non extraits dans cette passe; réponse Too many requests sur read_thread. La liste peut continuer après Show more.
- **Autres comptes :** ooeuf et autres comptes ne sont pas couverts par le connecteur utilisé dans cette passe.
- **PandaDoc du 7 octobre :** notifications lues, fichier intégral et journal de consultation/signature non récupérés.
- **Contrat exécuté et modifications :** à retrouver pour rapprocher janvier/mars, durée, dépôt 3 000/1 000 $, horaire et accès.
- **Comptabilité :** relevés bancaires, encaissements de juin, dépôt, loyers et commissions, factures de gaz, ventes nettes et marges restent à rapprocher. Aucun solde locatif définitif calculé.
- **Faits techniques :** rapport MAPAQ, facture/attestation signée de hotte, diagnostics friteuses/tablettes, photos datées, inventaires, rapport policier et vidéos pertinents non récupérés dans ce corpus.
- **Transmission des avis :** plusieurs variantes et accusés vierges; rechercher les messages ou journaux de remise propres à chaque version.

Ces éléments sont « non récupérés dans cette passe », pas déclarés inexistants. Les recherches et fichiers doivent être complétés avec le reste du dossier existant, sans remplacer les sources par les notes de synthèse.

## Reprise du 21 octobre 2026

Le corpus est maintenant de **26 messages distincts / 15 fils** : 22 courriels avec texte et en-têtes, plus 4 extraits Interac. **19 pièces originales** sont conservées : 14 PDF (218 pages), 3 DOCX, 1 PNG et 1 JPG. Les deux EML originaux sont comptés séparément.

La [capture Messenger 1000144788.jpg](../04_Pieces_jointes/Reprise_2026-10-21/1a0d034bcb239873__1000144788.jpg), annoncée dans le message 1a0d034bcb239873 du 23 septembre, est désormais récupérée, empreinte vérifiée et contrôlée visuellement. L'affichage de l'interlocuteur est partiellement masqué (« Khaled Rizka… »). Il propose de servir de communication entre Natalie et Quadro; la réponse bleue accepte la proposition. Aucune date calendaire n'est visible dans la capture. Elle étaye l'existence d'une discussion de médiation rapportée, **pas une instruction directe de Natalie de parler sans avocat**, ni une identité complète vérifiée. L'OCR brut est conservé séparément.

Le [courriel Skip du 29 septembre 2026](../03_Courriels/takatak.ca@gmail.com/1a0ee10a2cdcadac.json), envoyé par Ann B., indique les établissements actifs ou non sur la plateforme et demande de confirmer ceux concernés par une mise à jour bancaire. NutriShake au 6280 y figure actif; Pâtisserie Boulangerie Viennoise et Bin Molle & Bin Dure au 6280 y figurent inactifs. Ce sont les indications de Skip à cette date; elles ne prouvent pas le motif de l'inactivité, une responsabilité de Bar Sora ou un montant perdu. Aucune nouvelle donnée bancaire n'a été transmise.

La couverture PDF reste **217 pages avec couche texte existante + 1 page OCR, 0 page téléchargée sans extraction connue, 6 pages contrôlées visuellement**. La nouvelle capture JPG a son OCR et son contrôle séparés. Les contenus ChatGPT restent non extraits par cet agent (Too many requests); le compte Ooeuf n'est pas couvert par ce connecteur. Les pièces à obtenir et les rapprochements comptables précédemment listés restent ouverts.
