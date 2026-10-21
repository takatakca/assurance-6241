/** Local structural and behavioural checks. No browser session or network access. */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
process.on('uncaughtException',error=>{console.error(String(error.message).slice(0,1600));process.exitCode=1});

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const caseRoot=path.join(root,'6241 Léger');
const home=path.join(caseRoot,'00_Lire_en_premier');
const html=fs.readFileSync(path.join(home,'index.html'),'utf8');
const data=JSON.parse(fs.readFileSync(path.join(home,'tableau-de-bord.json'),'utf8'));
const checks=[];
function check(name,fn){fn();checks.push(name)}
function caseFile(rel){return path.join(caseRoot,...rel.split('/'))}
check('Every inventoried file exists and matches its SHA256',()=>{
  for(const f of data.files){
    const stat=fs.statSync(caseFile(f.path));assert.ok(stat.isFile(),f.path);assert.equal(stat.size,f.bytes,f.path);
    assert.equal(crypto.createHash('sha256').update(fs.readFileSync(caseFile(f.path))).digest('hex'),f.sha256,f.path);
  }
});
check('Inventory counts and duplicates are consistent',()=>{
  const counts=new Map();data.files.forEach(f=>counts.set(f.sha256,(counts.get(f.sha256)||0)+1));
  assert.equal(data.counts.files,data.files.length);assert.equal(data.counts.distinct_contents,counts.size);
  data.files.forEach(f=>assert.equal(f.duplicate_count,counts.get(f.sha256)));
  assert.ok(data.files.some(f=>f.path.endsWith('Master_comptable_6241_Leger.xlsx')));
  assert.ok(data.files.some(f=>f.path.endsWith('Dossier_comptable_6241_Leger.pptx')));
});
check('All timeline source references point to actual files',()=>{
  for(const e of data.timeline){assert.ok(e.source_refs.length,e.id);for(const ref of e.source_refs){assert.equal(ref.exists,true,ref.original);assert.ok(fs.statSync(caseFile(ref.path)).isFile(),ref.path)}}
});
check('Both chronologies are represented without changing dates or evidence',()=>{
  assert.equal(data.timeline.length,data.events.length+data.mail_events.length);
  for(const e of data.events){const t=data.timeline.find(t=>t.family==='chat'&&t.id===e.id);assert.equal(t.date,e.date);assert.equal(t.status,e.status);assert.equal(t.message_date,e.date_message_locale);if(e.current_scope_note)assert.ok(t.notes.includes(e.current_scope_note))}
  for(const e of data.mail_events){const t=data.timeline.find(t=>t.family==='mail'&&t.id===e.id);assert.equal(t.date,e.event_date);assert.equal(t.message_date,e.envelope_date);assert.equal(t.source_kind,e.evidence_level);assert.equal(t.author,e.author);assert.equal(t.anchor,e.text_anchor||'')}
  const keys=data.timeline.map(e=>e.date||'9999');assert.deepEqual(keys,[...keys].sort());
});
check('Static links resolve locally and no external scripts are loaded',()=>{
  for(const [,href] of html.matchAll(/href="([^"]+)"/g))if(href.startsWith('../'))assert.ok(fs.existsSync(path.resolve(home,decodeURIComponent(href))),href);
  assert.equal([...html.matchAll(/<script\b/g)].length,1);
  assert.equal([...html.matchAll(/<\/script\s*>/g)].length,1);
  assert.ok(!/<script[^>]+src\s*=/i.test(html));
});
const code=html.match(/<script>([\s\S]*)<\/script>/)[1].trim();
const literal=code.match(/^const DATA=([\s\S]*?);\r?\nconst \$=/)[1];
check('Embedded source JSON cannot close the script tag',()=>{
  assert.ok(!literal.includes('<'));assert.deepEqual(JSON.parse(literal),data);
  const hostile=JSON.stringify({text:'</script><img src=x onerror=alert(1)>'}).replaceAll('<','\\u003c');
  assert.equal(vm.runInNewContext('('+hostile+')').text,'</script><img src=x onerror=alert(1)>');
});

// Minimal DOM models only APIs used by this portal. Any HTML insertion fails the test.
class Element{
  constructor(tag,id=''){this.tagName=tag;this.id=id;this.children=[];this.value='';this.dataset={};this.listeners={};this._text='';this.className='';this.classList={toggle:()=>{}}}
  set textContent(v){this._text=String(v??'');this.children=[]}
  get textContent(){return this._text+this.children.map(c=>c.textContent??String(c)).join('')}
  set innerHTML(v){throw new Error('Untrusted HTML insertion: '+v)}
  append(...v){this.children.push(...v)}
  prepend(...v){this.children.unshift(...v)}
  replaceChildren(...v){this.children=[...v];this._text=''}
  addEventListener(name,fn){this.listeners[name]=fn}
  showModal(){this.open=true}
  close(){this.open=false}
  removeAttribute(name){delete this[name]}
  click(){this.onclick?.()}
}
const ids=new Map([...html.matchAll(/id="([^"]+)"/g)].map(([,id])=>[id,new Element('div',id)]));
const nav=['overview','pieces','chronology','meeting'].map(t=>{const e=new Element('button');e.dataset.tab=t;return e});
const document={getElementById:id=>{assert.ok(ids.has(id),id);return ids.get(id)},createElement:tag=>new Element(tag),querySelectorAll:selector=>selector==='nav button'?nav:selector==='main>section'?nav.map(e=>ids.get(e.dataset.tab)):[]};
let exportedBlob;
class TestURL extends URL{static createObjectURL(blob){exportedBlob=blob;return 'blob:test'}static revokeObjectURL(){}}
const context=vm.createContext({document,window:{scrollTo(){},print(){}},Option:function(text,value){const e=new Element('option');e.textContent=text;e.value=value;return e},URL:TestURL,Blob,setTimeout:fn=>{fn();return 0}});
vm.runInContext(code,context,{timeout:15000});
const run=code=>vm.runInContext(code,context,{timeout:15000});
const descendants=e=>[e,...e.children.filter(c=>c instanceof Element).flatMap(descendants)];
check('Initial rendering shows every file and both event families',()=>{
  assert.equal(run('filtered.length'),data.files.length);assert.equal(ids.get('timeline').children.length,data.timeline.length);
  assert.ok(ids.get('timeline').textContent.includes('Courriel'));
  assert.ok(ids.get('timeline').textContent.includes('Conversation ChatGPT'));
  assert.ok(ids.get('timeline').textContent.includes('Date du message qui contient la citation'));
});
check('Every rendered local link resolves; known paths are encoded',()=>{
  for(const element of [...ids.values()].flatMap(descendants))if(element.href?.startsWith('../'))assert.ok(fs.existsSync(path.resolve(home,decodeURIComponent(element.href))),element.href);
  assert.ok(run("localHref(DATA.files[0].path)").startsWith('../'));
  for(const payload of ['../secret','javascript:alert(1)','https://example.com','/etc/passwd','C:\\secret'])assert.equal(run(`localHref(${JSON.stringify(payload)})`),null);
});
check('File search handles accents, category/format intersections and no results',()=>{
  ids.get('query').value='Léger';run('render()');const accented=run('filtered.length');
  ids.get('query').value='leger';run('render()');assert.equal(run('filtered.length'),accented);assert.ok(accented>0);
  ids.get('query').value='';ids.get('format').value='XLSX';ids.get('category').value='07_Dommages_et_pertes';run('render()');assert.ok(run('filtered.length')>0);assert.ok(run("filtered.every(f=>f.format==='XLSX'&&f.category==='07_Dommages_et_pertes')"));
  ids.get('query').value='__no_such_document_6241__';run('render()');assert.equal(run('filtered.length'),0);assert.ok(ids.get('files').textContent.includes('Aucun résultat'));
  ids.get('query').value='';ids.get('format').value='';ids.get('category').value='';run('render()');
});
check('Timeline source filters, author search, accents and empty results work',()=>{
  ids.get('timelinefamily').value='mail';run('renderTimeline()');assert.equal(ids.get('timeline').children.length,data.mail_events.length);
  ids.get('timelinefamily').value='chat';run('renderTimeline()');assert.equal(ids.get('timeline').children.length,data.events.length);
  ids.get('timelinefamily').value='mail';ids.get('timelinequery').value='Joey';run('renderTimeline()');assert.ok(ids.get('timeline').children.length>0);assert.ok(ids.get('timeline').children.length<data.mail_events.length);
  ids.get('timelinequery').value='équipements';run('renderTimeline()');const count=ids.get('timeline').children.length;
  ids.get('timelinequery').value='equipements';run('renderTimeline()');assert.equal(ids.get('timeline').children.length,count);
  ids.get('timelinequery').value='__no_such_event_6241__';run('renderTimeline()');assert.ok(ids.get('timeline').textContent.includes('Aucun événement'));
  ids.get('timelinequery').value='';ids.get('timelinefamily').value='';run('renderTimeline()');
});
check('Untrusted source strings remain text and external links are restricted',()=>{
  assert.equal(run(`el('p','<img src=x onerror=alert(1)>').textContent`),'<img src=x onerror=alert(1)>');
  for(const value of ['javascript:alert(1)','https://mail.google.com.evil.test/','https://attacker@mail.google.com/','http://mail.google.com/'])assert.equal(run(`safeMailUrl(${JSON.stringify(value)})`),null);
  assert.ok(run("safeMailUrl('https://mail.google.com/mail/u/0/#all/example')").startsWith('https://mail.google.com/'));
});
check('CSV export protects formula prefixes including whitespace and control characters',()=>{
  for(const v of ['=1+1',' +1','\t=1','\u0000@SUM(A1)','-1','@cmd'])assert.ok(run(`csvCell(${JSON.stringify(v)})`).startsWith('"\''),v);
  assert.equal(run(`csvCell('normal "quoted" value')`),'"normal ""quoted"" value"');
});
ids.get('export').onclick();const csv=await exportedBlob.text();
check('Selection export includes real inventory records',()=>{assert.ok(csv.includes('Empreinte SHA256'));assert.ok(csv.includes(data.files[0].sha256))});
const withText=data.files.find(f=>f.text);
const row=ids.get('files').children.find(row=>row.textContent.includes(withText.path));
const previewButton=descendants(row).find(e=>e.tagName==='button');previewButton.onclick();
check('Text preview opens and closes with the matching original source',()=>{assert.equal(ids.get('previewtext').textContent,withText.text);assert.equal(ids.get('preview').open,true);assert.ok(ids.get('previewlink').href.startsWith('../'));ids.get('close').onclick();assert.equal(ids.get('preview').open,false)});
const receipt={as_of:new Date().toISOString(),mode:'Node VM + filesystem; no browser visual inspection',passed:checks.length,checks,files:data.files.length,distinct_contents:data.counts.distinct_contents,timeline:data.timeline.length,chat_events:data.events.length,mail_events:data.mail_events.length,source_links:data.timeline.reduce((n,e)=>n+e.source_refs.length,0),warnings:data.warnings};
fs.mkdirSync(path.join(root,'scripts/.build-livrables'),{recursive:true});
fs.writeFileSync(path.join(root,'scripts/.build-livrables/portal-validation.json'),JSON.stringify(receipt,null,2));
console.log(JSON.stringify(receipt,null,2));

