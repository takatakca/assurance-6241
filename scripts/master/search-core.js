/* Pure search functions, shared by the offline portal and its tests. */
(function (root) {
  'use strict';
  const normalize = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase().replace(/[^a-z0-9]+/g, ' ').trim();
  const compact = value => normalize(value).replace(/ /g, '');
  function terms(query) {
    return (String(query || '').match(/"[^"]+"|\S+/g) || []).map(t => normalize(t.replace(/^"|"$/g, ''))).filter(Boolean);
  }
  function prepare(doc) {
    doc._title = normalize([doc.title, doc.path, ...(doc.aliases || [])].join(' '));
    doc._pages = (doc.pages || []).map(p => ({ ...p, _text: normalize(p.text), _compact: compact(p.text) }));
    doc._body = doc._pages.map(p => p._text).join(' ');
    doc._compact = compact(doc._title + ' ' + doc._body);
    return doc;
  }
  function match(doc, ts) {
    const full = doc._title + ' ' + doc._body;
    if (!ts.every(t => full.includes(t) || (!t.includes(' ') && doc._compact.includes(t)))) return null;
    let best = null, bestScore = 0;
    for (const p of doc._pages) {
      const score = ts.reduce((sum, t) => sum + (p._text.includes(t) || (!t.includes(' ') && p._compact.includes(t)) ? 1 : 0), 0);
      if (score > bestScore) { best = p; bestScore = score; }
    }
    const score = ts.reduce((sum, t) => sum + (doc._title.includes(t) ? 8 : 0), 0) + bestScore;
    return { doc, page: best, score };
  }
  function snippet(page, ts, length = 300) {
    if (!page) return '';
    const text = page.text.replace(/\s+/g, ' ').trim();
    // Map normalized character positions back to the source, including spaced phone numbers.
    let flat = '', packed = ''; const map = [], packedMap = [];
    for (let i = 0; i < text.length; i++) {
      const chars = text[i].normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
      for (const ch of chars) {
        if (/[a-z0-9]/.test(ch)) { flat += ch; map.push(i); packed += ch; packedMap.push(i); }
        else if (!flat.endsWith(' ')) { flat += ' '; map.push(i); }
      }
    }
    let pos = -1;
    const candidates = [ts.join(' '), ...[...ts].sort((a,b) => b.length-a.length)].filter(Boolean);
    for (const term of candidates) { const n = flat.indexOf(term); if (n >= 0) { pos = map[n]; break; } }
    if (pos < 0) for (const term of ts) { const n = packed.indexOf(term.replace(/ /g,'')); if (n >= 0) { pos = packedMap[n]; break; } }
    const start = Math.max(0, pos - 85);
    return (start ? '…' : '') + text.slice(start, start + length) + (text.length > start + length ? '…' : '');
  }
  root.MasterSearch = { normalize, compact, terms, prepare, match, snippet };
  if (typeof module !== 'undefined') module.exports = root.MasterSearch;
})(typeof globalThis !== 'undefined' ? globalThis : this);
