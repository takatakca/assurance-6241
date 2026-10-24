# Entretien des équipements et tableaux IndemniPro

Contrôle documentaire du 24 octobre 2026. Cette analyse complète les demandes 5 et 22 de Me Dufourd. Elle rapproche les documents de service du sinistre antérieur et les versions du sommaire de l’assureur. Aucun montant n’est ajouté à la réclamation Harmony par cette analyse.

## Le tableau avec les numéros de factures est disponible

Trois versions du classeur **INDEMNIPRO — Sommaire dossier 24110-4833 — Assuré Hadmo** ont été identifiées. Leurs cellules donnent la description de l’équipement, le fournisseur, la référence documentaire, la date, des montants réclamés/évalués/alloués et des commentaires. Il s’agit d’un sommaire de réclamation du sinistre antérieur, distinct de l’inventaire général avec valeur marchande et de la liste d’un chargement U-Haul.

- [Version ancienne Hadmo](Originaux/Hadmo-version-ancienne.xlsx), sans date de version établie : devis 259 à 268 et montants alloués à zéro dans les lignes visibles.
- [Version désignée 15 janvier 2025](Originaux/Hadmo-version-15-janvier-2025.xlsx) : références de factures et devis, trois colonnes de montants.
- [Version désignée 22 avril 2025](Originaux/Hadmo-version-22-avril-2025.xlsx) : colonnes supplémentaires pour les sinistres des 3 et 8 juillet et les réserves. Cette version est identique par SHA-256 à la pièce déjà annexée A074; la copie ne crée pas une nouvelle preuve ni un nouveau montant.

Les [empreintes et sources des classeurs](PROVENANCE-TABLEAUX.json) et l’[extraction de leurs cellules et formules](TABLEAUX-HADMO-EXTRACTION-CELLULES.json) permettent de contrôler chaque référence. Les fichiers sources n’ont pas été modifiés; aucune formule n’a été recalculée pour créer un nouveau total.

La provenance par courriel est documentée : le [transfert du 1 juin 2026](19e847d203e73434-courriel-extrait.txt) cite le message de Joey Dubois du 15 janvier 2025 à 11:17, qui annonce son sommaire et précise que sa compréhension de certains éléments peut être erronée. Le [second transfert](19e847da779dcd5a-courriel-extrait.txt) cite son message du 23 avril 2025 à 07:37, qui demande confirmation des postes en réserve et évoque le manque de rapports de techniciens. Dates du transfert, du message cité et du nom de version restent distinctes. Ce sont des extractions des courriels déjà conservés, pas de nouveaux EML. Voir [provenance](PROVENANCE-COURRIELS-TABLEAUX.json).

## Dix PDF Frigo-Spec, cinq groupes de factures

Les dix PDF récupérés dans les archives ChatGPT se rattachent aux cinq références ci-dessous. Ils complètent le format et l’historique des versions des photographies déjà détenues. **Dix fichiers ne constituent pas dix dépenses.** Tous ces PDF d’une page ont été lus en texte natif et contrôlés visuellement dans le lot ChatGPT. Les photographies citées dans le tableau ont été revues individuellement le 24 octobre.

| Facture et service | Nouveaux PDF, p. 1 | Pièce déjà détenue | Concordances et différences à conserver |
|---|---|---|---|
| A245 — installation de climatisation fournie par le client; 1 145,00 $ HT, 1 316,46 $ TTC | [G23](../ChatGPT/Pieces_extraites/G23_192b6e5ddbebbe4b-Facture.pdf), [G26](../ChatGPT/Pieces_extraites/G26_192b695cec4fb023-Facture.pdf) | [Photo 1000069205](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069205.jpg) | Textes des deux PDF identiques, empreintes différentes. Facture et photo : 25 juin 2024. Tableau janvier E45 et avril E48 : 26 juin. Ce service précède juillet; ce n’est pas la preuve d’achat de l’appareil. |
| A266 — unité frigorifique 2 hp 230 V; 8 320,00 $ HT, 9 565,92 $ TTC | [G24](../ChatGPT/Pieces_extraites/G24_192b6e62f5eb5fb3-Facture.pdf), [G25](../ChatGPT/Pieces_extraites/G25_192b696201394ef4-Facture.pdf) | [Photo 1000069207](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069207.jpg) | 10 juillet 2024 dans les deux PDF. G24/photo précisent l’installation sur chambre congélateur et la mise en route; G25 a un libellé final plus général. Tableau avril D22/F22 : A266 et 8 320. Pas deux interventions à additionner. |
| A267 — compresseur CRD1 0200 CAB/chambre froide; 2 960,00 $ HT, 3 403,26 $ TTC | [G28](../ChatGPT/Pieces_extraites/G28_192b696b2a3af44a-Facture.pdf), [G30](../ChatGPT/Pieces_extraites/G30_192b6e67a28f1bfc-Facture.pdf) | [Photo 1000069203](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069203.jpg) | G28 : 10 juillet; G30 et photo : 13 juillet 2024. La photo montre A267 sur la feuille au premier plan et seulement l’en-tête A290 d’une feuille derrière. Le tableau janvier D19 et avril D20 indique A290 et classe 2 960 sous chambre de congélation : rapprochement à corriger après confirmation fournisseur, sans modifier les originaux. |
| A280 — compresseur CS20 côté gauche de machine à crème glacée; 5 990,00 $ HT, 6 887,00 $ TTC | [G27](../ChatGPT/Pieces_extraites/G27_192b69707dcc14ba-Facture.pdf), [G29](../ChatGPT/Pieces_extraites/G29_192b6e6d937fa268-Facture.pdf) | [Photo 1000069206](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069206.jpg) | 15 juillet 2024; textes PDF identiques, empreintes différentes. Tableau avril ligne29 : devis264/Electro Freeze; ligne39 : A280, montant évalué et alloué zéro, commentaire L39 « Ne reclame pas dédoublement ». Ne pas additionner devis264 et A280 comme deux pertes sans rattachement technique. |
| A281 — BUNN CDS2, carte de contrôle et agitateur gauche; 2 340,00 $ HT, 2 690,42 $ TTC | [G22](../ChatGPT/Pieces_extraites/G22_192b69775df0e947-Facture.pdf), [G31](../ChatGPT/Pieces_extraites/G31_192b6e7272d2e3d0-Facture.pdf) | [Photo 1000069201](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069201.jpg) | G22 : 15 juillet; G31 et photo : 17 juillet. Tableau avril B31 porte « Machine à Slush taylor », D31 A281, E31 7 juillet. Les factures portent BUNN. La [photo A290](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069204.jpg) du 22 juillet concerne aussi une machine à slush BUNN, avec le même total; intervention distincte ou version à faire préciser. |

Le [contrôle des PDF](../ChatGPT/CONTROLE-FACTURES-ARCHIVES.json) conserve le texte extrait. Le [contrôle des archives](../ChatGPT/CONTROLE-ARCHIVES-CHATGPT.json) conserve les empreintes et chemins internes. Les archives intégrales restent localement dans OneDrive sous `ChatGPT/99_Travail_et_collecte`; les PDF extraits sont accessibles dans le site.

Le onzième PDF est la [facture Rapide 2 Nette no 45](<../ChatGPT/Pieces_extraites/G10_Invoice_45_2025-07-28 (1).pdf>) de juillet 2025 à **Les Délices d’Aden**, 5837 Jean-Talon Est. Il ne s’agit pas d’une facture Frigo-Spec, d’un bail Quadro ou d’un mandat Remorquage Élite. Il reste hors de ce rapprochement d’entretien.

## Four à gaz et documents techniques : points précis à remettre au cabinet

La [photographie Choquette CKS N82145](../../07_Assurance_et_etat_anterieur/Archive_2026-10-05/lectures-factures2024/1000069214.jpg), revue visuellement, est datée du 26 novembre 2024 au nom de Quadro, 6241 Léger. Elle indique que le PS360WB et son pilote à gaz ne fonctionnent plus, que le problème persiste malgré des pièces remplacées et recommande un remplacement. Elle affiche 6 700,68 $ HT, 7 704,10 $ TTC, dépôt 700 $, payé 7 004,10 $, solde zéro et tampon PAYÉ. Ces inscriptions ne sont pas trois paiements à additionner et ne prouvent pas la livraison d’un four de remplacement.

Le tableau d’avril cite N82145 en D34, 6 700,68 en F33, et ajoute en B53/H53 « Déplacements techniciens / Choquette CKS » pour 7 704,10 avec « Aout 2024 » en E53. Il faut faire confirmer si cette ligne est le TTC du même document ou une autre facture : le rapprochement HT/TTC est un signal de recouvrement, pas la preuve de deux services. Le commentaire L35 « CKS a fait le travail » et L36 « Pas de facture » sont conservés comme commentaires du tableau, sans les transformer en attestation technique.

La facture A315 de septembre 2024 mentionne une mise en route, alors que N82145 décrit ensuite une panne persistante. Les feuillets SCC Auger, les propos de l’assureur et les déclarations du client doivent rester séparés. Identifier le four du haut, le four du bas, les numéros de série, les pièces et les essais pour chaque intervention demeure nécessaire. Les devis Tzanet 141455/141490 déjà rassemblés sont des soumissions de remplacement; ils n’établissent pas ces essais.

## Documents et vérifications encore ouverts

1. Confirmation Frigo-Spec des dates/versions A267 et A281, du rapport entre A281 et A290, et de la référence utilisée pour les 2 960 $ du tableau.
2. Bons de travail finaux, dates d’intervention, identité et numéros de série de chaque appareil; résultats des essais après réparation et avant la remise au déménageur.
3. Pièces bancaires de paiement, avoirs, annulations et indication de la version finale de chaque facture.
4. Ventilation CKS entre le HT 6 700,68 $ et le TTC 7 704,10 $, et justification de la ligne « Déplacements techniciens ».
5. Confirmation des appareils comptés ensemble dans le tableau IndemniPro et des postes déjà réglés au titre du sinistre antérieur. Une allocation d’assurance ou une réserve n’est pas une nouvelle dépense Harmony.

L’analyse renforce la documentation de l’entretien et du dossier transmis à l’assureur. Elle ne clôt pas les huit demandes sans leur document exact et ne démontre pas, seule, l’état fonctionnel de chaque équipement au 12 juin 2025.
