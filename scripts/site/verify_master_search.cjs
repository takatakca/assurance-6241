const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const root=path.resolve(__dirname,'../..');
const S=require('../master/search-core.js');
const ctx={window:{}};vm.createContext(ctx);
const dir=path.join(root,'00_DOSSIER_MAITRE/06_Index_recherche');
for(const file of fs.readdirSync(dir).filter(x=>/^recherche-\d+\.js$/.test(x)).sort())vm.runInContext(fs.readFileSync(path.join(dir,file),'utf8'),ctx);
const docs=ctx.window.MASTER_CHUNKS.flat().map(S.prepare);
const checks=[
 ['Daniel Simard','6241 Léger/03_Courriels/Analyse_consolidee/REPRISE-2026-10-21.md'],
 ['Frigospec A292','6241 Léger/10_Archive_avocat_2026-10-05/CATALOGUE-IMAGES.md'],
 ['31 085,30','6241 Léger/10_Archive_avocat_2026-10-05/ASSURANCE-HSB-OCTOBRE2025-CONTROLE.md'],
 ["trois mois d’installation",'6280 Somerled NDG/01_Synthese_et_chronologie/chronologie.md'],
 ['Chiqing Ma','6280 Somerled NDG/01_Synthese_et_chronologie/synthese.md'],
 ['fermeture anticipee','6280 Somerled NDG/01_Synthese_et_chronologie/synthese.md'],
 ['visite frigoriste','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Daniel_Simard/BILAN-DANIEL-SIMARD.md'],
 ['"Moving Globo Shoe Company"','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Ooeuf/ANALYSE-ET-PROVENANCE-OOEUF.md'],
 ['Signature manuscrite','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Autorisation_SPVM/AUTORISATION-SPVM-MTLEV2500487177-A-SIGNER.md'],
 ['5149964247','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/SUIVIS-ET-CONTACTS.md'],
 ['CN487','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Inventaire_Daniel_Simard/rapport.md'],
 ['reserve de droits','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Racine_Chamberland/CHRONOLOGIE-ASSURANCE-EXPERTS.md'],
 ['"Moving Globo Shoe Company"','HARMONY MOVERS/12_Remise_Dufourd_2026-10-21/REPONSES-AUX-25-DEMANDES.pdf'],
 ['CN487','HARMONY MOVERS/14_Recherche_complementaire_2026-10-24/Inventaire_Daniel_Simard/Originaux/INVENTAIRE RESTO.xlsx'],
 ['Dufourd','HARMONY MOVERS/03_Courriels/Originaux_ooeuf_2026-10-20/2026-10-20_1425_Quadro_reponse.eml'],
 ['"electricien licencie RBQ"','6280 Somerled NDG/03_Courriels/takatak.ca@gmail.com/19adac1b3dc27cc0.json'],
 ['"General Ledger Report" "2025-06-30"','6241 Léger/10_Archive_avocat_2026-10-05/comptabilite-ventes2024/final.xls'],
 ['"General Ledger Report" "2025-06-30"','HARMONY MOVERS/04_Factures_et_comptabilite/Collecte_Gmail_2026-10-21/19cb1ecd4a7964a1__quadro excel sort.xls'],
 ['"General Ledger Report" "2025-06-30"','HARMONY MOVERS/04_Factures_et_comptabilite/Collecte_Gmail_2026-10-21/19cb13a2879f146c__quadro excel sort.xls'],
 ['"FINANCIAL INFORMATION"','HARMONY MOVERS/13_Complements_Dufourd_2026-10-21/Recherche_Ooeuf/Scan2026-04-03_120155.pdf']
];
const result=[];
for(const [query,source] of checks){
 const doc=docs.find(d=>d.path===source||(d.aliases||[]).includes(source));assert(doc,'Missing source '+source);
 const match=S.match(doc,S.terms(query));assert(match && match.page,'Missing content match '+query);
 const snippet=S.snippet(match.page,S.terms(query));assert(snippet.length>0);
 result.push({query,source,page:match.page.page,snippet});
}
assert.strictEqual(docs.filter(d=>S.match(d,S.terms('zzyyxxAUCUNRESULTAT123456'))).length,0);
assert.strictEqual(new Set(docs.map(d=>d.sha256)).size,docs.length,'Duplicate hashes in search corpus');
console.log(JSON.stringify({queries_passed:result.length,no_result_query_passed:true,unique_hashes:true,documents:docs.length,checks:result}));
