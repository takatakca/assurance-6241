import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const tmp=path.join(root,'scripts/.build-livrables');
const out=path.join(root,'6241 Léger/07_Dommages_et_pertes/Comptabilite');
await fs.mkdir(out,{recursive:true});
const D=JSON.parse(await fs.readFile(path.join(tmp,'finance-source-extract.json'),'utf8'));
const EQ=JSON.parse(await fs.readFile(path.join(tmp,'equipment.json'),'utf8'));
const arc='6241 Léger/10_Archive_avocat_2026-10-05/';
const round=x=>Math.round((x+Number.EPSILON)*100)/100;
const W=Workbook.create();
const sheets={};
for(const n of ['Synthese','Pertes nouvelles','Exploitation','Factures et devis','Indemnites','Ventes','Grand livre','Hadmo avril','Controles','Methode']) sheets[n]=W.worksheets.add(n);
const num='#,##0.00;(#,##0.00);"-"';
function col(n){let s='';for(;n>0;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function setup(n,title,heads,rows,widths){const s=sheets[n],end=rows.length+5,C=col(heads.length);s.showGridLines=false;s.getRange(`A1:${C}${end}`).format.font={name:'Arial',size:10,color:'#202D3A'};s.getRange(`A1:${C}${end}`).format.rowHeight=22;s.getRange('A2').values=[[title]];s.getRange('A2').format.font={size:16,bold:true,color:'#17324D'};s.getRange(`A5:${C}5`).values=[heads];s.getRange(`A5:${C}5`).format={fill:'#17324D',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:34,wrapText:true,verticalAlignment:'center'};if(rows.length)s.getRange(`A6:${C}${end}`).values=rows;heads.forEach((_,i)=>s.getRange(`${col(i+1)}1:${col(i+1)}${end}`).format.columnWidth=widths?.[i]??18);s.freezePanes.freezeRows(5);if(rows.length)s.tables.add(`A5:${C}${end}`,true,`Registre${Object.keys(sheets).indexOf(n)+1}`);return s;}
function f(s,c,v){s.getRange(c).formulas=[[v]];s.getRange(c).format.font.color='#16703B';}
function money(s,range){s.getRange(range).setNumberFormat(num);s.getRange(range).format.horizontalAlignment='right';}
const ledger=D.ledger;
const gl=setup('Grand livre','Écritures du grand livre fourni', ['Compte','Intitulé','Date comptable','Description','Source comptable','Journal','Débit ($)','Crédit ($)','Ligne source','', 'Source'],ledger.map(r=>[r.account,r.accountName,new Date(r.date+'T12:00:00Z'),r.description,r.sourceNo,r.journal,r.debit,r.credit,r.row,null,'GRAND-LIVRE-ORIGINAL-feuille-1.csv, ligne '+r.row]),[12,29,16,46,23,12,18,18,15,3,60]);
gl.getRange(`C6:C${ledger.length+5}`).setNumberFormat('yyyy-mm-dd');money(gl,`G6:H${ledger.length+5}`);
gl.getRange('A3').values=[['Extraction CSV de final.xls. Écritures datées avec journal J, sous-totaux exclus. Devise $ présumée CAD, à confirmer.']];
const ub=D.workbooks.find(w=>w.source.includes('Uber-Ventes'));
const dd=D.workbooks.find(w=>w.source.includes('Doordash-ventes'));
function sales(w,start,end){let cells=Object.fromEntries(w.sheets[0].rows.flat().map(c=>[c.cell,c.value]));return Array.from({length:end-start+1},(_,i)=>({month:cells['B'+(start+i)],value:round(cells['C'+(start+i)]),source:w.source,cell:'C'+(start+i)}));}
const us=sales(ub,7,16),ds=sales(dd,6,14);
const smonth=['Mars','Avril','Mai','Juin','Juillet','Aout','Septembre','Octobre','Novembre','Decembre'];
const vrows=Array.from({length:14},(_,i)=>{let m=3+i,y=m>12?2025:2024;m=m>12?m-12:m;let u=us[i],d=ds[i-1],lg=ledger.find(r=>r.account==='4200'&&r.description.startsWith(`${y}-${String(m).padStart(2,'0')}`));return [new Date(Date.UTC(y,m-1,1,12)),u?.value??null,d?.value??null,lg?.credit??null,null,u?'Uber, Ventes total 2024!'+u.cell:null,d?'DoorDash, Ventes total 2024!'+d.cell:null,lg?'Grand livre ligne '+lg.row:null];});
const vs=setup('Ventes','Ventes documentées par période',['Mois','Uber ($)','DoorDash ($)','Grand livre 4200 ($)','','Source Uber','Source DoorDash','Source grand livre'],vrows,[16,20,20,24,3,38,38,30]);
vs.getRange('A6:A19').setNumberFormat('mmm-yy');money(vs,'B6:D21');vs.getRange('A21').values=[['Total couvert']];for(const c of ['B','C','D'])f(vs,c+'21',`=SUM(${c}6:${c}19)`);
vs.getRange('A3').values=[['Périodes différentes et canaux non rapprochés. Ne pas additionner les plateformes au grand livre. Cellule vide = mois absent.']];
vs.getRange('A23').values=[['Pièces : Uber-Ventes-2024- final.xlsx et Doordash-ventes-2024-final.xlsx; original CSV du grand livre.']];
vs.getRange('A24').values=[['Les ventes ne sont pas des profits ni une perte d’exploitation. Taxes, enseignes et ventes en salle à rapprocher.']];
const hw=D.workbooks.find(w=>w.source.includes('22 avril'));
const hc=Object.fromEntries(hw.sheets[0].rows.flat().map(c=>[c.cell,c.value]));
const hn=[13,14,17,18,20,22,23,24,25,27,29,31,33,37,39,40,42,44,46,48,50,52,53,60];
let previous='',item='';
const hrows=hn.map(r=>{if(r===60)item='';if(hc['B'+r])previous=hc['B'+r];if(hc['A'+r]!=null)item=String(hc['A'+r]);return [r,item,previous,hc['D'+r]??'',hc['F'+r]??null,hc['G'+r]??null,hc['H'+r]??null,hc['I'+r]??null,hc['J'+r]??null,hc['K'+r]??null,hc['L'+r]??'',null,`Copie Hadmo 22 avril 2025, Feuil1, ligne ${r}`];});
const hs=setup('Hadmo avril','Assurance historique : copie du 22 avril 2025',['Ligne','Item','Description','Pièce','Réclamé ($)','Évalué ($)','Alloué ($)','3 juillet ($)','8 juillet ($)','Réserve ($)','Commentaire source','','Source'],hrows,[10,10,39,18,19,19,19,19,19,19,58,3,58]);
hs.getRange('A3').values=[['Transcription des colonnes source, pas une demande cumulable. Réparations et remplacements peuvent viser les mêmes biens.']];money(hs,'E6:J29');
const hmap=Object.fromEntries(hn.map((r,i)=>[r,i+6]));
const htot=32;hs.getRange('A32:D32').values=[['Sommaire de la copie','Réclamé','Évalué','Alloué']];hs.getRange('B33:D33').values=[[hc.F63,hc.G63,hc.H63]];hs.getRange('A33').values=[['Total affiché']];hs.getRange('A34').values=[['Franchise source']];hs.getRange('D34').values=[[hc.H65]];hs.getRange('A35').values=[['Après franchise']];f(hs,'D35','=SUM(D33:D34)');hs.getRange('A36').values=[['Provisoire no 1 inscrit']];hs.getRange('D36').values=[[hc.H69]];hs.getRange('A37').values=[['Provisoire no 2 inscrit']];hs.getRange('D37').values=[[hc.H71]];hs.getRange('A38').values=[['Indemnité no 3 calculée']];f(hs,'D38','=SUM(D35:D37)');money(hs,'B33:D38');
hs.getRange('F33').values=[['Source : Feuil1 F63:H73. Alloué et provisoire ne prouvent pas un crédit bancaire.']];
const inv=[];
function addInv(id,date,kind,group,label,ht,tps,tvq,total,status,file,note){inv.push({id,date,kind,group,label,ht,tps,tvq,total,status,source:arc+file,note,currency:file.startsWith('sources/Invoice')?'CAD':'$ présumé CAD'});}
for(const [id,dt,ht,tps,tvq,tt,file,st] of [
['CWIQUWOL-0001','2025-06-12',3915,195.75,390.52,4501.27,'Invoice-CWIQUWOL-0001 (4).pdf','Annulée par version ultérieure'],
['CWIQUWOL-0002','2025-06-12',4365,218.25,435.41,5018.66,'Invoice-CWIQUWOL-0002 (3).pdf','Annulée par version ultérieure'],
['CWIQUWOL-0003','2025-07-22',3200,160,319.2,3679.2,'Invoice-CWIQUWOL-0003 (4).pdf','Annulée par version 0004'],
['CWIQUWOL-0004','2025-08-15',4200,210,418.95,4828.95,'Invoice-CWIQUWOL-0004.pdf','Version remplacée à rapprocher'],
['CWIQUWOL-0005','2025-09-19',3915,195.75,390.52,4501.27,'Invoice-CWIQUWOL-0005 (1).pdf','Facture réclamée, paiement non vérifié']])addInv(id,dt,'Facture déménagement','HARMONY-12JUIN',id,ht,tps,tvq,tt,st,'sources/'+file,'Même prestation; versions à ne pas additionner. Dernière version du lot, dette/solde à confirmer.');
const photos=[
['A320','2024-10-03','Frigo sous-sol',1705,85.25,170.07,1960.32,'1000069199.jpg','Rapprocher Hadmo A320 daté juillet.'],
['A315','2024-09-22','Four à pizza',7900,395,788.03,9083.03,'1000069200.jpg','Four/étage à identifier; version photographiée une seule fois.'],
['A281','2024-07-17','Slush BUNN CDS2',2340,117,233.42,2690.42,'1000069201.jpg','A281/A290 : possible doublon à résoudre.'],
['A294','2024-07-29','Cocktail TAYLOR',3850,192.5,384.04,4426.54,'1000069202.jpg','Date et montant lus sur facture.'],
['A267','2024-07-13','Chambre froide',2960,148,295.26,3403.26,'1000069203.jpg','En-tête A290 en arrière-plan, facture principale A267.'],
['A290','2024-07-22','Slush BUNN',2340,117,233.42,2690.42,'1000069204.jpg','A281/A290 : possible doublon à résoudre.'],
['A245','2024-06-25','Installation climatisation',1145,57.25,114.21,1316.46,'1000069205.jpg','Avant sinistre juillet; ne pas attribuer au déménagement.'],
['A280','2024-07-15','Crème glacée',5990,299.5,597.5,6887,'1000069206.jpg','Hadmo avril mentionne un dédoublement.'],
['A266','2024-07-10','Chambre congélateur',8320,416,829.92,9565.92,'1000069207.jpg','À rapprocher devis 261 et grand livre.']];
for(const [id,dt,l,h,t,v,tt,file,note] of photos)addInv(id,dt,'Réparation historique',id==='A281'||id==='A290'?'BUNN-A281-A290':id,l,h,t,v,tt,'Facture lue, règlement non établi','photos-reparations-janvier2025/'+file,note);
addInv('N82145','2024-11-26','Estimation marquée payée','CKS-FOUR','Four PS360WB',6700.68,335.03,668.39,7704.10,'Tampon payé; banque non rapprochée','photos-reparations-janvier2025/1000069214.jpg','Dépôt 700 et payé 7 004,10 = 7 704,10. Recommandation de remplacement, livraison non établie.');
addInv('L-1027-A','2025-08-04','Facture entreposage','CONTENEUR-L1027','Location conteneur',200,10,19.95,229.95,'Montant payé sur facture, solde 0','pieces-facturation-oct2025/facture CQC_L-1027-A.pdf','Date 04/08/2025 transcrite au format jour/mois. Paiement banque non rapproché.');
for(const [id,h,t,v,tt,l,dt] of [[259,2615,130.75,260.85,3006.60,'Frigo IFI',7],[260,1485,74.25,148.13,1707.38,'Machine à café Curtis',7],[261,8205,410.25,818.45,9433.7,'Chambre de congélation',7],[262,1650,82.5,164.59,1897.09,'Frigo sous-sol',7],[263,4635,231.75,462.34,5329.09,'Four Tim Horton',7],[264,5990,299.5,597.5,6887,'Electro-freeze',7],[266,3390,169.5,338.15,3897.65,'Cocktail Taylor',12],[267,2340,117,233.42,2690.42,'Slush BUNN',12],[268,1700,85,169.58,1954.58,'Chambre froide',12]]){const src=D.pdfs.find(p=>p.source.includes('Devis')&&p.source.endsWith(` ${id}.pdf`));addInv('DEV-'+id,`2024-07-${String(dt).padStart(2,'0')}`,'Devis historique','DEV-'+id,l,h,t,v,tt,'Proposition; exécution non établie',src.source.slice(arc.length),'Ne pas additionner au remplacement/réparation du même bien.');}
const ir=inv.map(r=>[r.id,new Date(r.date+'T12:00:00Z'),r.kind,r.label,r.ht,r.tps,r.tvq,r.total,null,r.group,r.status,null,r.source.slice(arc.length),r.note]);
const ins=setup('Factures et devis','Registre des factures et devis vérifiés',['Pièce','Date','Nature','Objet','Hors taxes','TPS','TVQ','Total pièce','Écart taxes','Groupe / doublon','Statut','','Source dans archive','Point à rapprocher'],ir,[23,16,29,34,18,17,17,19,16,27,43,3,75,80]);
ins.getRange('B6:B'+(ir.length+5)).setNumberFormat('yyyy-mm-dd');money(ins,`E6:I${ir.length+5}`);for(let r=6;r<ir.length+6;r++)f(ins,'I'+r,`=ROUND(H${r}-SUM(E${r}:G${r}),2)`);
ins.getRange('A3').values=[['Montants des pièces, non cumulables en l’état. Taxes récupérables et affectations à chaque sinistre restent à établir.']];
const pay=[
['PAY-01','2025-04-22','Provisoire no 1 inscrit',24136.06,'Inscription au chiffrier',null,null,'Hadmo 22 avril 2025, H69','Référence bancaire et affectation manquantes'],
['PAY-02','2025-02-20','HSB demande no 2',37288.16,'Paiement demandé / inscrit',null,null,'Courriel 19e847d75c50497e; Hadmo H71','Même 37 288,16 dans courriel et chiffrier; une seule ligne'],
['PAY-03','2025-02-20','HSB complément demandé',1855.68,'Paiement demandé',null,null,'Courriel 19e847d75c50497e','Ensemble annoncé : 39 143,84 avec PAY-02, pas une 3e somme'],
['PAY-04','2025-04-22','Indemnité no 3 au calcul',18494.09,'Solde calculé du chiffrier',null,null,'Hadmo 22 avril 2025, H73','Ni chèque ni crédit bancaire établis ici'],
['PAY-05','2025-10-29','Chèque annoncé en octobre',31085.30,'Reçu déclaré le 6 novembre',null,null,'Courriel 19c3887029c39b3e, échanges 29 octobre / 6 novembre','Encaissement, annulation et ventilation à vérifier']];
const ps=setup('Indemnites','Indemnités historiques : suivi des preuves',['ID','Date repère','Objet','Montant mentionné','Statut de preuve','Encaissé confirmé','Référence bancaire','','Source','Affectation / contrôle'],pay.map(r=>[r[0],new Date(r[1]+'T12:00:00Z'),...r.slice(2,7),null,r[7],r[8]]),[15,16,32,23,39,23,32,3,70,75]);
ps.getRange('B6:B10').setNumberFormat('yyyy-mm-dd');money(ps,'D6:F13');ps.getRange('F6:G10').format.fill='#FFF2CE';ps.getRange('A3').values=[['Sinistre 2024 HSB. Aucune somme de ces mentions n’est présentée comme total encaissé.']];ps.getRange('A12').values=[['Encaissé documenté']];f(ps,'F12','=IF(COUNT(F6:F10)=0,"n.d.",SUM(F6:F10))');ps.getRange('A14').values=[['Les extraits bancaires doivent identifier montant, bénéficiaire, date, annulation et dommage couvert.']];
const erows=EQ.map(r=>[r['Repère rubrique'],r['Désignation source'],null,null,null,null,null,null,'À documenter',null,r['Description à vérifier'],null,'REGISTRE-EQUIPEMENTS.csv, '+r['Repère rubrique']]);
const es=setup('Pertes nouvelles','Dommages allégués liés au déménagement',['Rubrique','Bien / groupe','Méthode retenue','Coût justifié HT','Taxes non récup.','Recouvrement affecté','Valeur résiduelle','Perte nette','État du dossier','Pièce justificative','Vérification requise','','Source de départ'],erows,[17,44,24,23,23,25,23,24,30,45,75,3,50]);
es.getRange('A3').values=[['Une base par bien : réparation OU remplacement. Zéro doit être documenté; vide signifie information manquante.']];
es.getRange(`C6:G${EQ.length+5}`).format.fill='#FFF2CE';es.getRange(`C6:C${EQ.length+5}`).dataValidation={rule:{type:'list',values:['Réparation','Remplacement','Autre justifié']}};
for(let r=6;r<EQ.length+6;r++)f(es,'H'+r,`=IF(OR(C${r}="",COUNT(D${r}:G${r})<4,J${r}="",I${r}<>"Validé"),"n.d.",D${r}+E${r}-F${r}-G${r})`);
money(es,`D6:H${EQ.length+5}`);es.getRange(`I6:I${EQ.length+5}`).dataValidation={rule:{type:'list',values:['À documenter','Validé','Exclu']}};
const ex=setup('Exploitation','Perte d’exploitation : calcul à documenter',['Période','Ventes de référence','Ventes réalisées','Marge contributive','Frais supplémentaires','Recouvrements affectés','Pièces / méthode','Perte calculée'],[['Période à définir',null,null,null,null,null,null,null]],[24,25,25,25,27,29,55,25]);
ex.getRange('A3').values=[['Renseigner une période justifiée et une marge après charges variables évitées. Les ventes seules ne mesurent pas la perte.']];ex.getRange('B6:G6').format.fill='#FFF2CE';f(ex,'H6','=IF(OR(COUNT(B6:F6)<5,G6="",A6="Période à définir"),"n.d.",(B6-C6)*D6+E6-F6)');money(ex,'B6:C6');money(ex,'E6:F6');money(ex,'H6');ex.getRange('D6').setNumberFormat('0.0%');
const sy=setup('Synthese','6241 boulevard Léger — master comptable',['Mesure','Montant ($)','Portée'],[
['Ventes du grand livre',null,'Juillet 2024 à avril 2025. Mai et juin non renseignés.'],
['Réparations comptabilisées',null,'64 écritures au compte 5765; factures et banque à rapprocher.'],
['Primes d’assurance comptabilisées',null,'Charges du compte 5685; ce ne sont pas des indemnités.'],
['Uber : ventes couvertes',null,'Mars à décembre 2024. Définition et entité à confirmer.'],
['DoorDash : ventes couvertes',null,'Avril à décembre 2024. Ne pas ajouter au grand livre.'],
['Hadmo : réclamé, copie avril',null,'Sommaire historique; options et doublons à réconcilier.'],
['Hadmo : alloué, copie avril',null,'Avant franchise; ne prouve pas un encaissement.'],
['Indemnités encaissées documentées',null,'Aucun montant rapproché à un crédit bancaire dans ce master.'],
['Pertes nouvelles : total validé',null,'Indisponible tant que les 27 rubriques ne sont pas traitées.'],
['Perte d’exploitation calculée',null,'Période, marge, frais et recouvrements à documenter.']
],[48,24,95]);
sy.getRange('A3').values=[['État au 21 octobre 2026. Aucune addition globale des sources ni perte finale annoncée.']];
const ge=ledger.length+5;f(sy,'B6',`=SUMIFS('Grand livre'!H6:H${ge},'Grand livre'!A6:A${ge},"4200")`);f(sy,'B7',`=SUMIFS('Grand livre'!G6:G${ge},'Grand livre'!A6:A${ge},"5765")`);f(sy,'B8',`=SUMIFS('Grand livre'!G6:G${ge},'Grand livre'!A6:A${ge},"5685")`);f(sy,'B9',"='Ventes'!B21");f(sy,'B10',"='Ventes'!C21");f(sy,'B11',"='Hadmo avril'!B33");f(sy,'B12',"='Hadmo avril'!D33");f(sy,'B13',"='Indemnites'!F12");f(sy,'B14',`=IF(COUNT('Pertes nouvelles'!H6:H${EQ.length+5})=${EQ.length},SUM('Pertes nouvelles'!H6:H${EQ.length+5}),"n.d.")`);f(sy,'B15',"='Exploitation'!H6");money(sy,'B6:B15');sy.getRange('B6:B15').format.font.color='#17324D';sy.tabColor='#17324D';sy.freezePanes.unfreeze();
const checkRows=[
['Ventes GL : total des 10 écritures',null,77995.44,null,'Source CSV ligne 16'],['Réparations GL : total des 64 écritures',null,57842.60,null,'Compte 5765, extraction datée'],['Uber : somme des mois',null,round(us.reduce((a,r)=>a+r.value,0)),null,'Source Ventes total 2024!C17'],['DoorDash : somme des mois',null,round(ds.reduce((a,r)=>a+r.value,0)),null,'Source Ventes total 2024!C15'],['Hadmo : alloué moins franchise/provisoires',null,hc.H73,null,'Source Feuil1!H73'],['Taxes : somme des écarts au carré',null,0,null,'Total pièce moins HT, TPS et TVQ'],['Réserve Hadmo : plage affichée',null,hc.K55,null,'K55 = SUM(K20:K54); exclut K13 et K18'],['Réserve Hadmo : toutes lignes détaillées',null,null,null,'Total différent attendu; portée à expliquer, ne pas corriger source']];
const cs=setup('Controles','Contrôles et rapprochements',['Contrôle','Recalculé','Source / référence','Écart','Explication'],checkRows,[55,24,24,20,85]);f(cs,'B6',"='Synthese'!B6");f(cs,'B7',"='Synthese'!B7");f(cs,'B8',"='Ventes'!B21");f(cs,'B9',"='Ventes'!C21");f(cs,'B10',"='Hadmo avril'!D38");f(cs,'B11',`=SUMSQ('Factures et devis'!I6:I${inv.length+5})`);f(cs,'B12',`=SUM('Hadmo avril'!J${hmap[20]}:J${hmap[53]})`);f(cs,'B13',"=SUM('Hadmo avril'!J6:J29)");for(let r=6;r<=12;r++)f(cs,'D'+r,`=ROUND(B${r}-C${r},2)`);f(cs,'D13','=B13-B12');money(cs,'B6:D13');cs.getRange('D6:D13').conditionalFormats.add('cellIs',{operator:'notEqual',formula:0,format:{fill:'#FCE4D6',font:{color:'#A61C00',bold:true}}});
setup('Methode','Utilisation et limites du master',['Sujet','Règle'],[
['Devise','CAD explicite sur factures Harmony. Pour les autres sources en $, devise canadienne présumée à confirmer. Aucune conversion.'],
['Source grand livre','GRAND-LIVRE-ORIGINAL-feuille-1.csv, extraction de final.xls. Le binaire .xls est conservé; contrôle direct de ce format non exécuté ici.'],
['Traçabilité','Les chemins complets et SHA-256 des fichiers relus figurent dans comptabilite-synthese.json. Les cellules, lignes ou pièces sont indiquées dans chaque onglet source.'],
['Factures','Registre de pièces vérifiées, pas preuve automatique de paiement ni d’admissibilité. Versions et photos répétées ne créent pas une nouvelle dépense.'],
['Taxes','HT, TPS, TVQ et TTC conservés distinctement. Le droit aux crédits de taxes n’est pas établi; saisir uniquement les taxes non récupérables justifiées.'],
['Pertes nouvelles','Les 27 rubriques viennent du registre existant. Identifier les objets multiples, séries, état avant/après et preuve du lien au déménagement avant validation.'],
['Calcul par bien','Choisir une seule méthode. Coût HT + taxes non récupérables − recouvrement affecté − valeur résiduelle. Les quatre montants, une pièce et le statut Validé sont requis.'],
['Rubrique exclue','Pour une exclusion documentée, conserver le motif et saisir les montants à zéro avec statut Validé après validation du responsable. Ne jamais utiliser zéro pour une donnée absente.'],
['Recouvrements','Ne déduire que les sommes du même dommage et même événement. Un chèque remplacé et son virement ne sont pas deux paiements.'],
['Exploitation','Calcul de travail : (ventes de référence − ventes réalisées) × marge contributive + frais supplémentaires − recouvrements affectés. Méthode et période à établir.'],
['Limites de couverture','Les données locales examinées ne certifient ni exhaustivité des boîtes mail, ni bilan complet, ni montant judiciaire recouvrable.'],
['Historique des conversations','Les anciennes réponses d’assistant peuvent contenir montants ou dates transformés. Aucune translation de date (+1 an) n’est appliquée. Priorité aux dates imprimées et écritures originales.'],
['Mise à jour','Compléter les cellules jaunes sur copie de travail. Pour ajouter une nouvelle ligne, prolonger les formules et plages de synthèse, puis vérifier les contrôles.'],
['Documents photographiés','Dix photographies de factures/estimation ont été lues visuellement; les originaux restent inchangés. OCR généralisé et autres pièces se poursuivent dans le dossier documentaire.'],
['Date','Préparation le 21 octobre 2026. Données sources datées 2024–2026 selon les pièces.']
],[29,145]);sheets.Methode.getRange('B6:B20').format.wrapText=true;sheets.Methode.getRange('A6:B20').format.rowHeight=42;
cs.getRange('D6:D13').setNumberFormat('0.00;(0.00);0.00');
// Check the blank-versus-zero guard on a disposable row state, then restore.
const before=es.getRange('C6:G6').values;
es.getRange('C6:G6').values=[['Réparation',0,0,0,0]];
es.getRange('I6:J6').values=[['Validé','Test temporaire']];
W.recalculate();
const testZero=es.getRange('H6').values[0][0];
es.getRange('G6').values=[[null]];
W.recalculate();
const testMissing=es.getRange('H6').values[0][0];
if(testZero!==0||testMissing!=='n.d.')throw new Error(`Guard failed: ${testZero}/${testMissing}`);
es.getRange('C6:G6').values=before;es.getRange('I6:J6').values=[['À documenter',null]];
await fs.writeFile(path.join(tmp,'master-guard-check.json'),JSON.stringify({documentedZero:testZero,missingValue:testMissing,restored:true}));
W.recalculate();
const inspection=await W.inspect({kind:'table',range:'Synthese!A5:C15',include:'values,formulas',tableMaxRows:15,tableMaxCols:4,maxChars:6000});await fs.writeFile(path.join(tmp,'master-inspection.ndjson'),inspection.ndjson);
const errs=await W.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:50},summary:'Vérification erreurs'});await fs.writeFile(path.join(tmp,'master-errors.ndjson'),errs.ndjson);console.log(errs.ndjson);
await (await SpreadsheetFile.exportXlsx(W)).save(path.join(out,'Master_comptable_6241_Leger.xlsx'));
for(const [n,s] of Object.entries(sheets)){try{const b=await W.render({sheetName:n,range:n==='Synthese'?'A1:C16':n==='Methode'?'A1:B11':n==='Hadmo avril'?'A1:G13':n==='Factures et devis'?'A1:I12':n==='Pertes nouvelles'?'A1:I10':'A1:H12',scale:1,format:'png'});await fs.writeFile(path.join(tmp,'master-'+n.replaceAll(' ','-')+'.png'),new Uint8Array(await b.arrayBuffer()));}catch(e){console.log('RENDER',n,e.message)}}
const metrics=[
{id:'GL-VENTES',label:'Ventes comptabilisées',amount:round(ledger.filter(r=>r.account==='4200').reduce((a,r)=>a+r.credit,0)),type:'ventes historiques',status:'extrait CSV contrôlé',source:arc+'GRAND-LIVRE-ORIGINAL-feuille-1.csv',locator:'lignes 6–16',period:'2024-07 à 2025-04'},
{id:'GL-REPARATIONS',label:'Réparations comptabilisées',amount:round(ledger.filter(r=>r.account==='5765').reduce((a,r)=>a+r.debit,0)),type:'charges historiques',status:'64 écritures, rapprochement factures requis',source:arc+'GRAND-LIVRE-ORIGINAL-feuille-1.csv',locator:'compte 5765',period:'exercice 2024-07 à 2025-06'},
{id:'UBER',label:'Ventes Uber couvertes',amount:round(us.reduce((a,r)=>a+r.value,0)),type:'ventes de plateforme',status:'cellules originales relues',source:ub.source,locator:'Ventes total 2024!C7:C17',period:'2024-03 à 2024-12'},
{id:'DOORDASH',label:'Ventes DoorDash couvertes',amount:round(ds.reduce((a,r)=>a+r.value,0)),type:'ventes de plateforme',status:'cellules originales relues',source:dd.source,locator:'Ventes total 2024!C6:C15',period:'2024-04 à 2024-12'},
{id:'HADMO-RECLAME',label:'Réclamé dans Hadmo avril',amount:hc.F63,type:'réclamation assurance historique',status:'montant du sommaire, doublons et options non résolus',source:hw.source,locator:'Feuil1!F63'},
{id:'HADMO-ALLOUE',label:'Alloué dans Hadmo avril',amount:hc.H63,type:'allocation historique',status:'non assimilable à un encaissement',source:hw.source,locator:'Feuil1!H63'}].map(m=>({...m,currency:'$ présumé CAD',taxBasis:'selon source, non harmonisée',includedInNewLoss:false}));
const sourcePaths=new Set([...D.sources.map(s=>s.path),...inv.map(i=>i.source),arc+'REGISTRE-EQUIPEMENTS.csv','6241 Léger/03_Courriels/Analyse_consolidee/emails-index.json']);
const crypto=await import('node:crypto');const sources=[];for(const p of sourcePaths){try{const b=await fs.readFile(path.join(root,p));sources.push({path:p,sha256:crypto.createHash('sha256').update(b).digest('hex')});}catch{sources.push({path:p,status:'chemin à vérifier'})}}
const summary={schema_version:1,prepared_on:'2026-10-21',address:'6241 boulevard Léger, Montréal',scope:'Comptabilité et pertes du dossier avocat; corpus local examiné',new_loss_total:null,business_interruption_loss:null,confirmed_insurance_receipts:null,metrics,invoices:inv,payments:pay.map(r=>({id:r[0],date:r[1],label:r[2],amount:r[3],type:'indemnité historique mentionnée',status:r[4],confirmedReceived:null,source:r[7],note:r[8],currency:'$ présumé CAD'})),equipment:EQ.map(r=>({id:r['Repère rubrique'],label:r['Désignation source'],netLoss:null,status:'À documenter'})),sources,limitations:['Les ventes et charges ne sont pas des pertes indemnisables.','Versions de factures, devis et réparations des mêmes biens non additionnés.','Aucune preuve bancaire rapprochée des indemnités dans ce master.','Réserve Hadmo K55 exclut K13 et K18 : 82 400 affichés contre 96 600 pour toutes lignes.','Grand livre repris du CSV conservé; format binaire final.xls non relu directement.']};
await fs.writeFile(path.join(out,'comptabilite-synthese.json'),JSON.stringify(summary,null,2));
await fs.writeFile(path.join(out,'README.md'),'# Master comptable — 6241 boulevard Léger\n\nLe classeur sépare les pertes nouvelles à établir, les ventes, les écritures historiques, les factures/devis et les indemnités mentionnées. Les cellules jaunes sont à compléter sur une copie de travail. Les montants absents restent « n.d. »; ils ne sont pas ramenés à zéro.\n\nLes pièces vérifiées sont référencées par numéro, cellule, ligne ou page. Le JSON fournit leurs chemins et empreintes SHA-256. Aucun total final de pertes ni total bancaire encaissé n’est établi. Les cinq versions Harmony ne sont pas cinq factures cumulables.\n\nConsulter l’onglet Méthode avant mise à jour. Formules et plages de synthèse doivent être prolongées lors de tout ajout de ligne.\n');
console.log(JSON.stringify({xlsx:path.join(out,'Master_comptable_6241_Leger.xlsx'),ledgerRows:ledger.length,invoices:inv.length,equipment:EQ.length,metrics},null,2));



