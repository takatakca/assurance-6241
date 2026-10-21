import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const build=path.join(root,'scripts/.build-livrables');
const out=path.join(root,'6241 Léger/08_Correspondance_et_procedures/Presentations');
const SKILL='C:/Users/fansh/.codex/plugins/cache/openai-primary-runtime/presentations/26.1020.11127/skills/presentations';
const PYTHON='C:/Users/fansh/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
process.env.RUNTIME_NODE_MODULES='C:/Users/fansh/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
await fs.mkdir(out,{recursive:true});
const data=JSON.parse(await fs.readFile(path.join(root,'6241 Léger/07_Dommages_et_pertes/Comptabilite/comptabilite-synthese.json'),'utf8'));
const p=Presentation.create({slideSize:{width:1280,height:720}});
p.theme.defaultFont='Arial';
const C={navy:'#17324D',ink:'#243542',muted:'#516374',paper:'#F8F7F4',gold:'#C9A96A'};
function text(s,t,x,y,w,h,size=28,color=C.ink,bold=false){const sh=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0,style:'solid'}});sh.text=t;sh.text.style={typeface:'Arial',fontSize:size,color,bold};return sh;}
function slide(title,subtitle=''){let s=p.slides.add();s.background.fill=C.paper;text(s,title,64,46,1152,66,44,C.navy,true);if(subtitle)text(s,subtitle,66,122,1148,60,23,C.muted);text(s,'6241 boulevard Léger  |  21 octobre 2026',64,676,1010,24,15,C.muted);text(s,String(p.slides.items.length).padStart(2,'0'),1165,672,50,28,18,C.muted);return s;}
function table(s,values,widths,{top=204,height=346,font=25}={}){let t=s.tables.add({rows:values.length,columns:values[0].length,left:64,top,width:1152,height,columnWidths:widths,values});for(let r=0;r<values.length;r++){t.rows[r].height=height/values.length;for(let c=0;c<values[r].length;c++){let cell=t.getCell(r,c);cell.text.style={typeface:'Arial',fontSize:font,color:r===0?'#FFFFFF':C.ink,bold:r===0};cell.fill=r===0?C.navy:(r%2===0?'#EAEFF3':'#FFFFFF');}}return t;}
function notes(s,t){s.speakerNotes.text=t;}
const arc='6241 Léger/10_Archive_avocat_2026-10-05/';
const m=id=>data.metrics.find(x=>x.id===id);
const fmt=n=>new Intl.NumberFormat('fr-CA',{minimumFractionDigits:2,maximumFractionDigits:2}).format(n)+' $';
let s=slide('Dossier comptable et pertes');
text(s,'6241 boulevard Léger',64,214,1135,85,58,C.navy,true);
text(s,'Quadro — assurance historique et déménagement',67,320,1110,75,30,C.ink);
text(s,'Pièces, montants, chronologie et points à établir',67,444,1060,55,29,C.muted);
text(s,'État du dossier au 21 octobre 2026',67,528,1050,40,24,C.muted);
notes(s,'Source : master comptable préparé à partir des documents locaux listés dans comptabilite-synthese.json. Les montants judiciairement réclamables et la perte finale ne sont pas établis. Cette présentation décrit les pièces et les rapprochements à accomplir.');
s=slide('Trois ensembles à rapprocher','Chaque montant conserve son événement, sa nature et sa source');
table(s,[['Ensemble','Ce que les pièces documentent','Point à établir'],['Assurance historique','Réparations 2024, copie Hadmo,\nannonces d’indemnités','Affectation et encaissement\nde chaque règlement'],['Déménagement 2025','Versions de factures Harmony,\n27 rubriques de biens','État avant/après et coût\ndu dommage nouveau'],['Exploitation','Ventes mensuelles et\nécritures comptables','Période touchée, marge\net charges évitées']],[260,450,442],{height:354,font:25});
text(s,'Un montant comptabilisé, réclamé, alloué ou payé correspond à une étape différente.',66,594,1120,52,24,C.navy);
notes(s,`Sources : ${arc}REGISTRE-EQUIPEMENTS.csv; GRAND-LIVRE-ORIGINAL-feuille-1.csv; copie Hadmo du 22 avril 2025; factures CWIQUWOL-0001 à 0005. Aucune combinaison automatique des trois ensembles.`);
s=slide('Ventes documentées','Les périodes couvertes et le traitement des canaux diffèrent');
table(s,[['Source','Période renseignée','Montant'],['Grand livre — compte 4200','Juillet 2024 à avril 2025',fmt(m('GL-VENTES').amount)],['Uber','Mars à décembre 2024',fmt(m('UBER').amount)],['DoorDash','Avril à décembre 2024',fmt(m('DOORDASH').amount)]],[410,420,322],{height:310,font:27});
text(s,'Mai et juin 2025 sont absents du détail des ventes du grand livre. Leur absence ne prouve pas des ventes nulles.',66,544,1118,66,25);
text(s,'Ces montants ne mesurent pas la perte d’exploitation.',66,616,1118,40,25,C.navy,true);
notes(s,data.metrics.filter(x=>['GL-VENTES','UBER','DOORDASH'].includes(x.id)).map(x=>`${x.source}, ${x.locator}. ${x.status}.`).join('\n')+'\nNe pas additionner les plateformes au grand livre. Devise $ présumée CAD.');
s=slide('Une prestation, plusieurs versions Harmony','Les versions ne doivent pas être additionnées');
table(s,[['Version','Date d’émission','Total TTC (CAD)','Repère documentaire'],['0001','12 juin 2025','4 501,27 $','Annulée dans la version 0002'],['0002','12 juin 2025','5 018,66 $','Ajout d’une nuitée'],['0003','22 juillet 2025','3 679,20 $','Crédit annoncé de 1 165 $ HT'],['0004','15 août 2025','4 828,95 $','Ajout de deux mois d’entreposage'],['0005','19 septembre 2025','4 501,27 $','Facture du lot à rapprocher au solde']],[160,250,244,498],{top:190,height:390,font:24});
text(s,'Le paiement, les annulations et le solde final doivent être rapprochés avec les pièces bancaires et les échanges.',66,603,1120,58,24);
notes(s,data.invoices.filter(x=>x.id.startsWith('CWI')).map(x=>x.source+', pages 1–2.').join('\n')+'\nLes factures 0002, 0003 et 0004 identifient les anciennes versions annulées. La présence de 0005 dans ce lot ne tranche pas une dette reconnue.');
s=slide('Assurance historique : copie Hadmo du 22 avril','Calcul du sommaire, sans assimilation à un encaissement bancaire');
table(s,[['Inscription dans le chiffrier','Montant ($)'],['Alloué au sommaire H63','80 918,31'],['Moins franchise H65','(1 000,00)'],['Moins provisoire no 1 inscrit H69','(24 136,06)'],['Moins provisoire no 2 inscrit H71','(37 288,16)'],['« Indemnité no 3 » calculée H73','18 494,09']],[830,322],{top:190,height:370,font:25});
text(s,'Réclamé dans la même copie : 191 615,88 $. Les réparations et remplacements peuvent viser les mêmes biens.',66,586,1115,68,25);
notes(s,`${m('HADMO-RECLAME').source}, Feuil1 F63, H63, H65, H69, H71, H73. Calcul relu et reproduit : 80 918,31 − 1 000 − 24 136,06 − 37 288,16 = 18 494,09. Réserve K55 = SUM(K20:K54) affiche 82 400; les cellules K13 et K18 valent 11 500 et 2 700 et sont hors de cette plage. Portée à expliquer. Le total réclamé source ne constitue pas un nouveau calcul de perte.`);
s=slide('Indemnités : annonces et preuves disponibles','Le rapprochement bancaire reste à compléter');
table(s,[['Date de l’échange','Montant mentionné','Ce qui est documenté'],['20 février 2025','39 143,84 $','HSB dit avoir demandé le paiement\n1 855,68 $ + 37 288,16 $'],['29 octobre 2025','31 085,30 $','Joey annonce l’envoi d’un chèque'],['6 novembre 2025','Même chèque','Le client déclare sa réception\net son intention d’encaisser']],[260,270,622],{height:332,font:26});
text(s,'À relier : autorisation, référence du chèque ou virement, dépôt, disponibilité finale et dommages couverts.',66,572,1125,77,27,C.navy);
notes(s,'Sources : 6241 Léger/03_Courriels/Analyse_consolidee/emails-index.json, messages 19e847d75c50497e (transfert du 1 juin 2026 contenant l’échange du 20 février 2025), 19c3887029c39b3e (transfert du 7 février 2026 contenant les échanges du 29 octobre et du 6 novembre 2025). Les reprises de la même chaîne ne sont pas de nouveaux paiements. Aucune somme globale encaissée déduite.');
s=slide('L’état des fours avant le déménagement','Deux pièces de 2024 demandent un rapprochement par appareil');
async function addImage(s,file,x,y,w,h){let b=await fs.readFile(path.join(root,file));s.images.add({blob:b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength),contentType:'image/jpeg',alt:path.basename(file),fit:'contain',position:{left:x,top:y,width:w,height:h}});}
await addImage(s,arc+'lectures-factures2024/1000069200.jpg',64,188,265,450);
await addImage(s,arc+'lectures-factures2024/1000069214.jpg',350,188,265,450);
text(s,'A315 — 22 septembre 2024',650,202,560,44,28,C.navy,true);
text(s,'9 083,03 $ TTC. La facture mentionne une mise en route et des ajustements.',650,255,555,104,28);
text(s,'CKS N82145 — 26 novembre 2024',650,384,560,65,28,C.navy,true);
text(s,'7 704,10 $ TTC, document marqué payé. Il recommande le remplacement du PS360WB.',650,458,555,109,28);
text(s,'Identifier le four, l’étage et les travaux achevés avant juin 2025.',650,586,555,68,25,C.navy);
notes(s,`${arc}photos-reparations-janvier2025/1000069200.jpg et 1000069214.jpg. Copies orientées de lecture utilisées pour présentation, originaux conservés. A315 : HT 7 900 + TPS 395 + TVQ 788,03. N82145 : HT 6 700,68 + TPS 335,03 + TVQ 668,39, dépôt 700 + payé 7 004,10, solde 0. Le tampon payé ne démontre pas une livraison de remplacement; identité et fin des travaux non établies ici.`);
s=slide('Chiffrer les dommages nouveaux','27 rubriques du registre existant à documenter, parfois plusieurs objets par rubrique');
text(s,'Coût justifié hors taxes',66,205,1100,58,35,C.navy,true);
text(s,'+ taxes non récupérables justifiées',66,273,1100,48,30);
text(s,'− recouvrements affectés au même dommage',66,333,1100,48,30);
text(s,'− valeur résiduelle retenue',66,393,1100,48,30);
text(s,'= perte nette à établir pour chaque bien',66,468,1100,58,35,C.navy,true);
text(s,'Choisir réparation ou remplacement. Documenter les valeurs nulles. Les données absentes restent « n.d. » dans le master.',66,562,1115,85,27);
notes(s,`${arc}REGISTRE-EQUIPEMENTS.csv, ANN-01 à ANN-27. Formule de travail du master, pas détermination juridique d’admissibilité. Les champs ne sont pas remplis par extrapolation des factures historiques. Les coûts, taxes, indemnités, valeur résiduelle, méthode, pièce et validation doivent être renseignés.`);
s=slide('Pièces nécessaires pour fermer les écarts');
const actions=[['01','Banque et indemnités','Références, dépôts, annulations et affectation par dommage.'],['02','Équipements','Séries, inventaire, photos avant/après et diagnostics datés.'],['03','Travaux','Factures finales, exécution, mise en route et état à la remise.'],['04','Exploitation','Période de perte, ventes comparables, marge et charges évitées.'],['05','Versions et sources','Facturation Harmony, réserve Hadmo, A281/A290 et dates originales.']];
actions.forEach(([n,t,b],i)=>{let y=164+i*94;text(s,n,66,y,70,42,28,C.muted);text(s,t,158,y,1030,40,29,C.navy,true);text(s,b,158,y+42,1040,42,25);});
notes(s,'Points tirés des écarts documentés dans le master, des originaux des factures, du registre équipements et des échanges HSB. Les anciennes réponses d’assistant ne remplacent pas les originaux. Aucune correction systématique de dates de +1 an n’a été appliquée. Les valeurs incertaines demeurent explicitement non établies.');
const candidate=path.join(build,'dossier-financier-draft.pptx');
await (await PresentationFile.exportPptx(p)).save(candidate);
for(const [i,s] of p.slides.items.entries()){let b=await p.export({slide:s,format:'png',scale:1});await fs.writeFile(path.join(build,`presentation-${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));}
const {finalizePresentation}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const final=path.join(out,'Dossier_comptable_6241_Leger.pptx');
const result=await finalizePresentation({workspaceDir:root,candidatePath:candidate,finalPath:final,pythonExecutable:PYTHON,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit',...[2,3,4,5,6].flatMap(n=>['--require-native-table-slide',String(n)])],requiredNativeTableOwnerSlides:[2,3,4,5,6],fontPolicy:{basis:'design',families:['Arial']},verifyArtifactToolImport:true,receiptPath:path.join(build,'presentation-validation.json')});
console.log(JSON.stringify({final,result}));


