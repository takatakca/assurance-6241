import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
let code=fs.readFileSync(path.join(here,'site-viewer.js'),'utf8');
const relative='6241 Léger/00_Lire_en_premier/LIRE-EN-PREMIER.md';
code=code.replace('/*SITE_ROUTES*/',JSON.stringify({[relative]:relative+'.html'}));
const base='https://example.github.io/assurance-6241/';
class Element{
  constructor(href,attrs={}){this._href=href;this.attrs=attrs;this.dataset=attrs.raw?{raw:'true'}:{};this.children=[]}
  get href(){return new URL(this._href,base).href}set href(value){this._href=value}
  hasAttribute(name){return name in this.attrs}
  matches(selector){return selector==='a[href]'}
  querySelectorAll(){return this.children}
  closest(){return this}
}
const normal=new Element(relative+'#règles');
const download=new Element(relative,{download:''});
const raw=new Element(relative,{raw:true});
const outside=new Element('https://elsewhere.example/'+relative);
const otherRepository=new Element('https://example.github.io/another/'+relative);
const links=[normal,download,raw,outside,otherRepository];
const listeners={};let onMutate;
const document={currentScript:{src:base+'assets/site-viewer.js'},baseURI:base+'index.html',body:{},querySelectorAll:()=>links,addEventListener:(name,fn)=>{(listeners[name]??=[]).push(fn)}};
const context=vm.createContext({document,URL,Element,window:{print(){}},MutationObserver:class{constructor(fn){onMutate=fn}observe(){}}});
vm.runInContext(code,context);
assert.ok(normal.href.includes('LIRE-EN-PREMIER.md.html#r%C3%A8gles'));
assert.ok(download.href.endsWith('.md'));
assert.ok(raw.href.endsWith('.md'));
assert.ok(outside.href.startsWith('https://elsewhere.example/'));
assert.ok(otherRepository.href.includes('/another/'));
const later=new Element(relative);
onMutate([{addedNodes:[later]}]);assert.ok(later.href.endsWith('.md.html'));
const encoded=new Element(encodeURI(relative));listeners.click.at(-1)({target:encoded});assert.ok(encoded.href.endsWith('.md.html'));
console.log(JSON.stringify({passed:7,checks:['Repository-prefix URL resolution','Unicode path and fragment','Download source preserved','Raw source preserved','External links preserved','Other repository unchanged','Dynamic/search-generated links upgraded']},null,2));
