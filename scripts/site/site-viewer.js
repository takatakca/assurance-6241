/* Static navigation enhancement; does not fetch files or send data. */
(()=>{'use strict';
const routes=/*SITE_ROUTES*/;
const script=document.currentScript;
const root=new URL('../',script.src);
const routeMap=new Map(Object.entries(routes));
function readableUrl(value){
  try{
    const u=new URL(value,document.baseURI);
    if(u.origin!==root.origin||!u.pathname.startsWith(root.pathname))return null;
    const relative=decodeURIComponent(u.pathname.slice(root.pathname.length));
    const mapped=routeMap.get(relative);
    if(!mapped)return null;
    const result=new URL(mapped.split('/').map(encodeURIComponent).join('/'),root);
    result.hash=u.hash;return result.href;
  }catch{return null}
}
function updateLinks(node){
  if(!(node instanceof Element)&&node!==document)return;
  const links=node.matches?.('a[href]')?[node]:Array.from(node.querySelectorAll('a[href]'));
  for(const a of links){
    if(a.hasAttribute('download')||a.dataset.raw==='true')continue;
    const next=readableUrl(a.href);if(next&&next!==a.href)a.href=next;
  }
}
updateLinks(document);
new MutationObserver(records=>{for(const r of records)for(const n of r.addedNodes)updateLinks(n)}).observe(document.body,{childList:true,subtree:true});
document.addEventListener('click',event=>{const button=event.target.closest?.('[data-print]');if(button)window.print()});
// Honour raw-document links and downloads, including the context menu.
document.addEventListener('click',event=>{const a=event.target.closest?.('a[href]');if(a)updateLinks(a)},true);
})();
