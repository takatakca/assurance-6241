# Reprise ciblée Takatak — demandes Dufourd

Préparé le 21 octobre 2026. Compte vérifié : **takatak.ca@gmail.com**. Statut de transmission : **non envoyé**. Aucun message n’a été envoyé, déplacé ou modifié.

## Résultat exploitable

La demande **11 passe de non repérée à partielle**. Une photographie de convention de novembre 2024 mentionne un bureau et une unité d’entreposage au 5505 rue Irwin et porte des signatures visibles. Une photographie de convention antérieure, le projet non signé CINTEC–Quadro de juillet 2025, sa proposition de résiliation de l’ancienne convention et l’avis CINTEC du 15 août 2025 sont également disponibles. Ces versions documentent le terrain et doivent être présentées ensemble; elles n’établissent pas encore l’identité et la capacité du locataire bénéficiaire pour Quadro, le lien entre 5505 Irwin et 5007 « Herwin », ni le droit d’utiliser le chariot élévateur le 12 juin 2025.

Les neuf autres demandes de ce lot conservent leur statut précédent. Aucun nouveau contrat U-Haul du 12 juin, mandat Élite, inventaire des biens réellement chargés dans U-Haul, CV ou titre d’occupation de Jean-Talon n’a été identifié par cette recherche.

## Livrables

- [Dix lignes JSON à fusionner](patch-demandes-communications.json) : réponses proposées, pièces, manquants, démarches et réserves. Elles incluent les références antérieures; fusionner les apports financiers/Ooeuf avant mise à jour finale.
- [Version lisible des réponses](patch-demandes-communications.md).
- [Index des huit courriels](messages-index.json) et exports MIME complets dans `MIME/`.
- [Index des onze pièces originales téléchargées](pieces-index.json), chemins et SHA-256.
- [Quinze requêtes et couverture](recherche-couverture.json); résultats de chaque page dans `Recherches/`.
- [Contrôle visuel et qualification des nouvelles pièces](CONTROLE-DES-PIECES.md).

## Couverture réelle

Quinze requêtes ciblées, dix-sept pages de résultats et **333 apparitions, soit 214 identifiants Gmail distincts**. La pagination des quinze requêtes est épuisée. Cela ne démontre pas une recherche exhaustive de toute la boîte : les résultats dépendent des mots-clés, de l’indexation Gmail et des pièces indexées. Les 214 courriels n’ont pas tous été relus intégralement; les résultats ont été comparés au corpus antérieur de 189 messages et triés pour sélectionner les nouveaux candidats.

**Huit nouveaux messages lus et conservés en arbre MIME, onze pièces téléchargées.** Les pièces comprennent cinq PDF totalisant dix-sept pages et six photographies/captures. Seize pages PDF ont du texte natif exploitable. L’avis CINTEC d’une page est une image scannée : OCR Windows réalisé et original contrôlé visuellement. Les six images ont également fait l’objet d’OCR Windows; la reconnaissance des manuscrits et petits caractères est imparfaite. Toutes les images ont été vues; les clauses déterminantes du bail ont été vérifiées sur les captures et la page de signature du projet PDF. L’OCR sert à la recherche, pas à certifier le texte ou les signatures.

Les exports MIME sont des réponses du connecteur conservant l’arbre et les en-têtes. Ce ne sont pas des EML bruts RFC 822. Les textes `Textes/` en sont des extractions; certains corps CINTEC présentent un mauvais décodage d’accents dans le connecteur. Les originaux des pièces jointes sont conservés séparément, avec taille attendue contrôlée et SHA-256.

## Limites et candidats écartés

- Le relevé BMO de Quadro portant l’adresse Jean-Talon ne constitue pas un bail ni une autorisation d’occupation.
- La facture Rapide 2 Nette no 43 concerne **Les Délices d’Aden**, pas Quadro. Son total de 1 807,65 $ et sa mention de paiement comptant n’ont pas été ajoutés à la réclamation Harmony. La facture no 45, déjà examinée, n’a pas été téléchargée à nouveau.
- Les quatre images envoyées par Yan Romanowski le 28 octobre 2025 sont un projet manuscrit de procédure. Les allégations et montants y sont des éléments de rédaction, pas des preuves indépendantes ni une liste des biens U-Haul. Aucun statut « produit au tribunal » n’en est déduit.
- Les résultats concernant le dossier d’assurance Les Délices d’Aden 6804A5559, les activités de concessionnaire U-Haul antérieures au transport, Somerled, les newsletters et activités personnelles ont été distingués. Aucun de ces résultats n’est assimilé au contrat du camion de juin 2025.
- `releves (3).zip`, message 197fec78a27b3735 du 12 juillet 2025, est explicitement non pris en charge par Gmail read_attachment. Aucun appel à cette action n’a été fait pour ce ZIP. L’agent financier l’a récupéré séparément via RAW : cinq relevés Desjardins, février à juin 2025, sous `../Recherche_Takatak_finances/Contenu_archives/197fec78a27b3735/`. Voir son propre index et sa lecture des paiements; ne pas compter deux récupérations.
- Les SMS/Messenger, audios et boîtes de Pierre/M. Constantino ne sont pas accessibles par cette recherche Takatak. Ooeuf et ChatGPT sont traités séparément par les autres agents. Ne pas inférer leur absence de ces recherches.

## Prochaines vérifications précises

1. Confirmer avec l’auteur des conventions photographiées l’identité/capacité du locataire et fournir des originaux lisibles. Rapprocher l’accord 2024, le projet 2025 et l’avis de non-renouvellement, sans trancher leur effet juridique ici.
2. Faire identifier la compagnie ayant engagé U-Haul puis obtenir son contrat, sa facture, la preuve de paiement et ses messages. Une dépense personnelle ou antérieure au transport n’établit pas cette opération.
3. Obtenir l’accord chariot/horaires, le droit d’occupation Jean-Talon, le CV et les documents Élite. Aucun de ces documents n’est reconstitué à partir d’une simple déclaration.
4. Pour les demandes 2, 8 et 25, confronter la pièce P-2 effectivement déposée aux quatre EML déjà conservés et aux chaînes ultérieures. La demande écrite 8 vise Harmony; l’engagement oral E9 vise la compagnie ayant engagé le U-Haul. La différence demeure à confirmer par le cabinet.

Aucune somme des différentes versions de loyers/factures n’est totalisée. Aucune conclusion juridique n’est tirée de la seule présence d’une signature, d’un avis ou d’une allégation.

## Comparaison complémentaire Ooeuf

Le fil [Situation de transport](../Recherche_Ooeuf/Situation-transport-fil-Ooeuf.txt), extrait par l’agent parent, a été confronté aux transferts Takatak. Il corrobore les messages séparés du 15 août 2025 (11 h 02, 14 h 15, 15 h 17) et leurs pièces annoncées, sans nouveau contenu substantiel par rapport aux chaînes déjà conservées. Plusieurs messages sont tronqués dans l’interface. Les demandes 2, 8 et 25 restent partielles. Cette comparaison ne change pas les comptes de collecte Takatak ci-dessus.

## Dernier contrôle de la demande 12

Les documents Ooeuf d’inscription TPS et du registre des entreprises confirment une adresse administrative Jean-Talon, sans établir le droit d’occupation. La demande 12 reste non repérée pour le document demandé. L’avis TPS d’une page daté du 3 octobre 2025 annonce une prise d’effet le 7 octobre 2025; le même compte apparaît sur la déclaration de juillet–septembre 2024. Historique à rapprocher, sans conclusion d’irrégularité. Le verso annoncé sur l’avis manque. Quatre photographies de documents d’identité ont été examinées puis écartées des annexes de cette demande; aucune donnée personnelle de ces cartes n’est recopiée ici.
