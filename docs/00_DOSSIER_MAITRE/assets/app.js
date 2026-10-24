(function () {
  'use strict';
  const $ = id => document.getElementById(id);
  const root = document.body.dataset.workspaceRoot;
  const meta = window.MASTER_META;
  const docs = (window.MASTER_CHUNKS || []).flat().map(MasterSearch.prepare);
  if (!meta || docs.length !== meta.stats.documents_unique || new Set(docs.map(d => d.sha256)).size !== docs.length) {
    $('index-status').textContent = 'Index incomplet — recherche désactivée';
    $('loading').textContent = 'Tous les fichiers de recherche n’ont pas été chargés. Vérifier que le dossier complet est disponible dans OneDrive, ou recharger le site. La table des matières reste accessible.';
    return;
  }
  const url = path => root + path.split('/').map(encodeURIComponent).join('/');
  const create = (tag, text, cls) => { const el = document.createElement(tag); if (text) el.textContent = text; if (cls) el.className = cls; return el; };
  const link = (label, path, cls) => { const el = create('a', label, cls); el.href = url(path); return el; };
  let matches = [], shown = 0, ts = [];
  const pageLabel = (p, doc) => !p ? 'Texte' : doc.format === 'pdf' ? 'Page ' + p.page : ['xlsx','xls'].includes(doc.format) ? 'Feuille ' + (p.label || p.page) : doc.format === 'json' ? (p.label || 'Courriel '+p.page) : ['png','jpg','jpeg','webp'].includes(doc.format) ? 'Image' : ['docx','pptx'].includes(doc.format) ? 'Partie ' + (p.label || p.page) : 'Texte';
  function renderMore() {
    const fragment = document.createDocumentFragment();
    for (const item of matches.slice(shown, shown + 30)) {
      const { doc, page } = item;
      const card = create('article', '', 'result');
      card.append(create('p', doc.number + ' · ' + ((doc.cases || []).length > 1 ? 'Pièce commune : ' + doc.cases.join(' / ') : doc.case) + ' · ' + doc.format.toUpperCase(), 'eyebrow'));
      const heading = create('h3');
      const primary = link(doc.title, doc.reader || doc.path);
      if (page?.page && doc.format === 'pdf') primary.hash = 'page=' + page.page;
      else if (page?.page && doc.reader) primary.hash = 'page-' + page.page;
      heading.append(primary); card.append(heading);
      const excerpt = MasterSearch.snippet(page, ts);
      card.append(create('p', excerpt || (ts.length ? 'Correspondance dans le titre ou le chemin. Aucun passage textuel correspondant dans cette extraction.' : 'Ouvrir la lecture ou la pièce source pour consulter ce document.'), 'excerpt'));
      card.append(create('p', [doc.nature, page ? pageLabel(page, doc) + ' · ' + page.method : doc.extraction_status].filter(Boolean).join(' — '), 'muted'));
      const actions = create('div', '', 'actions');
      const open = link(doc.reader ? 'Ouvrir la lecture' : 'Ouvrir la pièce', doc.reader || doc.path, 'button secondary');
      open.href = primary.href;
      const original = link('Télécharger la source', doc.path, 'source-link'); original.setAttribute('download', '');
      actions.append(open, original); card.append(actions);
      const details = create('details', '', 'provenance');
      details.append(create('summary', 'Provenance et emplacements (' + (1 + (doc.aliases || []).length) + ')'));
      details.append(create('p', doc.path));
      details.append(create('p', 'SHA-256 : ' + doc.sha256, 'hash'));
      if (doc.aliases?.length) { const list = create('ul'); for (const alias of doc.aliases) { const li = create('li'); const copy = link(alias, alias); copy.setAttribute('download', ''); copy.title = 'Télécharger cette copie source'; li.append(copy); list.append(li); } details.append(list); }
      card.append(details); fragment.append(card);
    }
    $('results').append(fragment); shown = Math.min(shown + 30, matches.length);
    $('more').hidden = shown >= matches.length;
    $('more').textContent = 'Afficher les 30 résultats suivants (' + shown + ' / ' + matches.length + ')';
  }
  function search(updateUrl = true) {
    ts = MasterSearch.terms($('query').value);
    const dossier = $('case-filter').value, format = $('format-filter').value;
    matches = [];
    for (const doc of docs) {
      if (dossier && !(doc.cases || [doc.case]).includes(dossier) || format && doc.format !== format) continue;
      const m = MasterSearch.match(doc, ts); if (m) matches.push(m);
    }
    matches.sort((a, b) => b.score - a.score || a.doc.sort - b.doc.sort);
    $('results').replaceChildren(); shown = 0; renderMore();
    $('result-count').textContent = matches.length.toLocaleString('fr-CA') + ' documents distincts' + (ts.length ? ' trouvés' : ' dans cette sélection');
    $('empty').hidden = matches.length !== 0;
    if (updateUrl) {
      const params = new URLSearchParams(); if ($('query').value) params.set('q', $('query').value); if (dossier) params.set('dossier', dossier); if (format) params.set('format', format);
      try { history.replaceState(null, '', location.pathname + (params.size ? '?' + params : '') + '#recherche'); } catch (_) { /* file:// may restrict history, search still works. */ }
    }
  }
  for (const value of meta.cases) { const option = create('option', value); option.value = value; $('case-filter').append(option); }
  for (const value of [...new Set(docs.map(d => d.format))].sort()) { const option = create('option', value.toUpperCase()); option.value = value; $('format-filter').append(option); }
  const params = new URLSearchParams(location.search); $('query').value = params.get('q') || ''; $('case-filter').value = params.get('dossier') || ''; $('format-filter').value = params.get('format') || '';
  let timer; $('query').addEventListener('input', () => { clearTimeout(timer); timer = setTimeout(search, 220); });
  $('search-form').addEventListener('submit', e => { e.preventDefault(); clearTimeout(timer); search(); });
  $('case-filter').addEventListener('change', () => search()); $('format-filter').addEventListener('change', () => search());
  $('clear').addEventListener('click', () => { $('query').value = ''; $('case-filter').value = ''; $('format-filter').value = ''; search(); $('query').focus(); });
  $('more').addEventListener('click', renderMore);
  for (const button of document.querySelectorAll('[data-query]')) button.addEventListener('click', () => { $('query').value = button.dataset.query; search(); $('query').focus(); });
  $('loading').hidden = true; $('search-form').hidden = false;
  $('index-status').textContent = docs.length.toLocaleString('fr-CA') + ' documents distincts · index du ' + meta.generated_at.slice(0, 10);
  search(false);
})();
