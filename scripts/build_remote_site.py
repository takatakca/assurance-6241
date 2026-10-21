"""Build/audit a static, portable GitHub Pages copy. Never changes source dossiers.

Default: audit only. Run --build after source collection and local indexes stabilize.
No external dependency; all generated URLs work below a GitHub Pages repository path.
"""
from pathlib import Path, PurePosixPath
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, quote
from collections import Counter
from datetime import datetime, timezone
import argparse, base64, hashlib, html, json, posixpath, re, shutil, zipfile

ROOT=Path(__file__).resolve().parents[1]
CASES=['6241 Léger','6280 Somerled NDG','HARMONY MOVERS']
OUT=ROOT/'dist-site'
WORK=ROOT/'scripts/.build-livrables'
RULE='Les originaux, les déclarations et les analyses sont identifiés par leur provenance. Les doublons et les versions d’une facture ne s’additionnent pas. Une extraction OCR reste à contrôler sur la pièce originale. Les documents à obtenir et les vérifications ouvertes figurent dans les synthèses de chaque dossier.'
RULE_PATH='documentation/REGLES-COMMUNES.md'
ALLOWED={'.pdf','.png','.jpg','.jpeg','.webp','.gif','.xlsx','.xls','.docx','.doc','.pptx','.csv','.json','.txt','.md','.eml','.html','.zip'}
TEXT={'.csv','.json','.txt','.md','.eml','.html'}
MIMES={'.pdf':'application/pdf','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.gif':'image/gif','.html':'text/html; charset=utf-8','.md':'text/markdown; charset=utf-8','.txt':'text/plain; charset=utf-8','.json':'application/json','.csv':'text/csv; charset=utf-8','.eml':'message/rfc822','.xlsx':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet','.xls':'application/vnd.ms-excel','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.doc':'application/msword','.pptx':'application/vnd.openxmlformats-officedocument.presentationml.presentation'}
SECRET_PATTERNS={
    'private_key':rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
    'github_token':rb'\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{60,})\b',
    'openai_service_key':rb'\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{40,}\b',
    'google_access_token':rb'\bya29\.[A-Za-z0-9_-]{40,}',
    'aws_access_key':rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
}
SECRET_NAMES={'.env','.env.local','.env.production','credentials.json','service-account.json','cookies.json','id_rsa','id_ed25519'}
EXCLUDE_PARTS={'99_Travail_et_collecte','.git','.codex','.agents','node_modules','__pycache__','ocr-images','.build-livrables'}
MIMES['.zip']='application/zip'
warnings=[];exclusions=[];secret_findings=[];repairs=[];missing=[]
files={};hashes={};generated={};routes={};directories=set();links_checked=0

def digest(data):return hashlib.sha256(data).hexdigest()
def escaped_json(value):return json.dumps(value,ensure_ascii=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
def rel_url(target,source):
    return quote(posixpath.relpath(target,posixpath.dirname(source) or '.'),safe='/')
def add(rel,text):generated[rel]=text.encode('utf-8') if isinstance(text,str) else text
def audit_archive(path,rel):
    """Inspect documentary ZIP members without extracting or changing originals."""
    with zipfile.ZipFile(path) as archive:
        for member in archive.infolist():
            name=PurePosixPath(member.filename.replace('\\','/'))
            label=rel+'!/'+member.filename
            if name.is_absolute() or '..' in name.parts or ':' in member.filename:
                raise RuntimeError('Chemin non portable dans une archive : '+label)
            if member.is_dir():continue
            if (member.external_attr >> 16) & 0o170000 == 0o120000:
                raise RuntimeError('Lien symbolique dans une archive : '+label)
            if name.name.lower() in SECRET_NAMES or name.suffix.lower() in {'.pem','.key','.pfx','.p12'}:
                secret_findings.append({'path':label,'kind':'nom de fichier de secrets ou identifiants de service'});continue
            if name.suffix.lower() not in ALLOWED- {'.zip'} or any(part in EXCLUDE_PARTS for part in name.parts):
                raise RuntimeError('Pièce non documentaire ou archive imbriquée : '+label)
            if member.flag_bits & 1:
                raise RuntimeError('Archive chiffrée impossible à contrôler : '+label)
            if member.file_size>128*1024*1024:
                raise RuntimeError('Pièce d’archive supérieure au plafond de contrôle : '+label)
            if name.suffix.lower() in TEXT:
                raw=archive.read(member)
                for kind,pattern in SECRET_PATTERNS.items():
                    if re.search(pattern,raw):secret_findings.append({'path':label,'kind':kind})
def collect():
    for name in CASES:
        base=ROOT/name
        if not base.is_dir():raise RuntimeError('Dossier absent : '+name)
        for p in sorted(base.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(ROOT).as_posix();reason=None
            if any(part in EXCLUDE_PARTS for part in p.relative_to(ROOT).parts):reason='cache ou collecte technique'
            elif p.name.lower() in SECRET_NAMES or p.suffix.lower() in {'.pem','.key','.pfx','.p12'}:reason='fichier de secrets ou identifiants de service'
            elif p.suffix.lower() not in ALLOWED:reason='format non documentaire ou non pris en charge'
            elif not p.resolve().is_relative_to(ROOT.resolve()) or p.is_symlink():reason='lien de fichier hors périmètre'
            if reason:exclusions.append({'path':rel,'reason':reason,'bytes':p.stat().st_size});continue
            files[rel]=p
    for rel in ['OUVRIR-LES-DOSSIERS.html',RULE_PATH]:
        p=ROOT/rel
        if not p.is_file():raise RuntimeError('Source attendue absente : '+rel)
        files[rel]=p
    for rel,p in files.items():
        raw=p.read_bytes();hashes[rel]=digest(raw)
        if p.suffix.lower() in TEXT:
            for label,pattern in SECRET_PATTERNS.items():
                if re.search(pattern,raw):secret_findings.append({'path':rel,'kind':label})
        elif p.suffix.lower()=='.zip':audit_archive(p,rel)
        parent=posixpath.dirname(rel)
        while parent:
            directories.add(parent);parent=posixpath.dirname(parent)
        if p.suffix.lower()=='.md':routes[rel]=rel+'.html'
    if secret_findings:raise RuntimeError('Des identifiants de service possibles ont été détectés; aucun site copié. Consulter le rapport local sans valeurs de secrets.')

def resolve_link(value,source,image=False,raw=False):
    """Return URL only for an existing selected resource or safe external hyperlink."""
    global links_checked
    links_checked+=1
    value=html.unescape(value.strip())
    try:parts=urlsplit(value)
    except ValueError:parts=None
    if parts and parts.scheme in ('https','http','mailto'):
        if not image:return html.escape(value,quote=True)
        missing.append({'source':source,'target':value,'reason':'image distante non chargée automatiquement'});return None
    if not parts or parts.scheme or parts.netloc or '\x00' in value:
        missing.append({'source':source,'target':value,'reason':'protocole non autorisé'});return None
    if not parts.path:return '#'+quote(unquote(parts.fragment),safe='-_.~') if parts.fragment else '#'
    path=unquote(parts.path).replace('\\','/')
    if path.startswith('/'):
        missing.append({'source':source,'target':value,'reason':'chemin absolu non portable'});return None
    target=posixpath.normpath(posixpath.join(posixpath.dirname(source),path))
    if target in directories:target=target+'/index.html'
    known=set(files)|set(routes.values())|{p+'/index.html' for p in directories}|{'index.html','assets/site-reader.css','assets/site-viewer.js'}
    if target not in known:
        suffix=path
        while suffix.startswith('../') or suffix.startswith('./'):suffix=suffix.split('/',1)[1]
        candidates=[r for r in files if r.endswith('/'+suffix) or r==suffix]
        # Relink an archival reference only when all candidates are byte-identical.
        if candidates and len({hashes[r] for r in candidates})==1:
            preferred=sorted(candidates,key=lambda r:(not r.startswith(source.split('/')[0]+'/'),len(r),r))[0]
            repairs.append({'source':source,'from':value,'to':preferred,'basis':'suffixe correspondant et contenu SHA-256 identique entre candidats'})
            target=preferred
        else:
            missing.append({'source':source,'target':value,'reason':'pièce absente ou correspondance ambiguë'});return None
    if not raw:target=routes.get(target,target)
    result=rel_url(target,source)
    if parts.query:result+='?'+parts.query
    if parts.fragment:result+='#'+quote(unquote(parts.fragment),safe='-_.~/:')
    return html.escape(result,quote=True)

def inline(text,source):
    """Small safe Markdown renderer: raw HTML is always escaped."""
    tokens=[]
    def token(value):tokens.append(value);return f'\x00{len(tokens)-1}\x00'
    def code(m):return token('<code>'+html.escape(m[1])+'</code>')
    text=re.sub(r'`([^`]+)`',code,text)
    # Handles angle-bracket destinations and balanced parenthesis file names.
    pattern=r'(!?)\[([^\]]*)\]\((<[^>]*>|(?:[^()\n]|\([^()]*\))+?)\)'
    def link(m):
        destination=m[3].strip('<>')
        url=resolve_link(destination,source,image=bool(m[1]))
        label=html.escape(m[2])
        if not url:return token('<span class="missing" title="'+html.escape(destination,quote=True)+'">'+label+' [référence indisponible]</span>')
        if m[1]:return token('<img loading="lazy" src="'+url+'" alt="'+html.escape(m[2],quote=True)+'">')
        return token('<a href="'+url+'" rel="noopener noreferrer">'+label+'</a>')
    text=re.sub(pattern,link,text)
    text=html.escape(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'(?<!\*)\*([^*\n]+)\*(?!\*)',r'<em>\1</em>',text)
    return re.sub(r'\x00(\d+)\x00',lambda m:tokens[int(m[1])],text)

def markdown(text,source):
    lines=text.splitlines();out=[];i=0;anchors=Counter()
    def slug(value):
        raw=re.sub(r'[^\w\- ]','',value.lower()).replace(' ','-');n=anchors[raw];anchors[raw]+=1;return raw+('-'+str(n) if n else '')
    def cells(line):return re.split(r'(?<!\\)\|',line.strip().strip('|'))
    while i<len(lines):
        line=lines[i]
        if not line.strip():i+=1;continue
        if line.lstrip().startswith('```'):
            buf=[];i+=1
            while i<len(lines) and not lines[i].lstrip().startswith('```'):buf.append(lines[i]);i+=1
            out.append('<pre><code>'+html.escape('\n'.join(buf))+'</code></pre>');i+=1;continue
        heading=re.match(r'^(#{1,6})\s+(.*)',line)
        if heading:
            n=len(heading[1]);out.append(f'<h{n} id="{html.escape(slug(heading[2]),quote=True)}">'+inline(heading[2],source)+f'</h{n}>');i+=1;continue
        if i+1<len(lines) and '|' in line and re.match(r'^\s*\|?\s*:?-{3,}',lines[i+1]):
            header=cells(line);out.append('<div class="table-scroll"><table><thead><tr>'+''.join('<th>'+inline(c.strip(),source)+'</th>' for c in header)+'</tr></thead><tbody>');i+=2
            while i<len(lines) and '|' in lines[i] and lines[i].strip():
                out.append('<tr>'+''.join('<td>'+inline(c.strip(),source)+'</td>' for c in cells(lines[i]))+'</tr>');i+=1
            out.append('</tbody></table></div>');continue
        list_item=re.match(r'^\s*(?:([-*+])|\d+\.)\s+(.*)',line)
        if list_item:
            tag='ul' if list_item[1] else 'ol';out.append('<'+tag+'>')
            while i<len(lines):
                m=re.match(r'^\s*(?:([-*+])|\d+\.)\s+(.*)',lines[i])
                if not m or ('ul' if m[1] else 'ol')!=tag:break
                out.append('<li>'+inline(m[2],source)+'</li>');i+=1
            out.append('</'+tag+'>');continue
        if line.startswith('>'):
            buf=[]
            while i<len(lines) and lines[i].startswith('>'):buf.append(lines[i].lstrip('> '));i+=1
            out.append('<blockquote>'+inline(' '.join(buf),source)+'</blockquote>');continue
        if re.fullmatch(r'\s*[-*_]{3,}\s*',line):out.append('<hr>');i+=1;continue
        buf=[line];i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r'^(?:#{1,6}\s|```|>|\s*[-*+]\s|\s*\d+\.\s)',lines[i]):
            if i+1<len(lines) and '|' in lines[i] and re.match(r'^\s*\|?\s*:?-{3,}',lines[i+1]):break
            buf.append(lines[i]);i+=1
        out.append('<p>'+inline(' '.join(buf),source)+'</p>')
    return '\n'.join(out)

class ArchiveReader(HTMLParser):
    allowed={'h1','h2','h3','h4','h5','h6','p','div','section','ul','ol','li','table','thead','tbody','tr','th','td','strong','b','em','i','blockquote','pre','code','br','hr','a','img'}
    blocked={'script','style','iframe','object','embed','svg','head'}
    def __init__(self,source):super().__init__(convert_charrefs=True);self.source=source;self.out=[];self.depth=0;self.skipped_links=[]
    def handle_starttag(self,tag,attrs):
        if tag in self.blocked:self.depth+=1;return
        if self.depth or tag not in self.allowed:return
        a=dict(attrs)
        if tag=='a':
            href=resolve_link(a.get('href',''),self.source,raw='download' in a)
            self.skipped_links.append(not bool(href))
            if not href:self.out.append('<span class="missing">');return
            self.out.append('<a href="'+href+'" rel="noopener noreferrer"'+(' download' if 'download' in a else '')+'>');return
        if tag=='img':
            href=resolve_link(a.get('src',''),self.source,image=True)
            if href:self.out.append('<img loading="lazy" src="'+href+'" alt="'+html.escape(a.get('alt',''),quote=True)+'">')
            return
        self.out.append('<'+tag+'>')
    def handle_endtag(self,tag):
        if tag in self.blocked:
            self.depth=max(0,self.depth-1);return
        if self.depth or tag not in self.allowed or tag in {'br','hr','img'}:return
        if tag=='a':self.out.append('</span>' if self.skipped_links and self.skipped_links.pop() else '</a>')
        else:self.out.append('</'+tag+'>')
    def handle_data(self,data):
        if not self.depth:self.out.append(html.escape(data))

def rule_html(source):
    target=rel_url(RULE_PATH+'.html',source)
    return '<div class="site-rules" role="note"><strong>Règle commune aux trois dossiers</strong><p>'+RULE+'</p><a href="'+target+'">Lire les règles communes</a></div>'
def secure_html(text,source):
    # CSP hashes retain only the known generated inline scripts. No inline handlers.
    text=text.replace('onclick="window.print()"','data-print="true"')
    script_hashes=["'sha256-"+base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode()+"'" for s in re.findall(r'<script>([\s\S]*?)</script>',text)]
    csp="default-src 'none'; script-src 'self' "+' '.join(script_hashes)+"; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'"
    tag='<meta http-equiv="Content-Security-Policy" content="'+html.escape(csp,quote=True)+'"><meta name="referrer" content="no-referrer"><link rel="stylesheet" href="'+rel_url('assets/site-reader.css',source)+'">'
    text=text.replace('</head>',tag+'</head>',1)
    tail='<script src="'+rel_url('assets/site-viewer.js',source)+'" defer></script>'
    return text.replace('</body>',tail+'</body>',1)
def page(title,body,source,raw=None,note=None):
    nav='<a href="'+rel_url('index.html',source)+'">← Les trois dossiers</a>'
    if raw:
        nav+='<a data-raw="true" download href="'+rel_url(raw,source)+'">Télécharger la source</a>'
        nav+='<a href="https://github.com/takatakca/assurance-6241/blob/main/docs/'+quote(raw,safe='/')+'" rel="noopener noreferrer">Source dans GitHub</a>'
        if raw.endswith('.md'):
            nav+='<a href="https://github.com/takatakca/assurance-6241/edit/main/docs/'+quote(raw,safe='/')+'" rel="noopener noreferrer">Modifier la source</a>'
    nav+='<button data-print="true">Imprimer</button>'
    text='<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>'+html.escape(title)+'</title></head><body class="reader"><nav>'+nav+'</nav><main>'
    if note:text+='<p class="note">'+html.escape(note)+'</p>'
    if raw and raw.endswith('.md'):text+='<p class="source">Après une modification de la source dans GitHub, cette vue de lecture doit être régénérée lors de la prochaine publication.</p>'
    text+=body+'</main>'+rule_html(source)+'</body></html>'
    return secure_html(text,source)

def trusted_hub(text,source):
    match=re.search(r'const CASES=([\s\S]*?);\s*const \$=',text)
    if not match:raise RuntimeError('Structure du hub inconnue')
    cases=json.loads(match[1])
    for case in cases:
        case['files']=[f for f in case['files'] if f['path'] in files]
        case['guides']=[f for f in case['guides'] if f['path'] in files]
        case['distinct']=len({f['sha256'] for f in case['files']})
    text=text[:match.start(1)]+escaped_json(cases)+text[match.end(1):]
    text=text.replace('dans votre espace OneDrive.','dans cette copie du dossier accessible en ligne.')
    text=text.replace('Cet index ouvre les fichiers locaux. La synchronisation OneDrive et la publication GitHub sont des états distincts de ce classement.','Cette copie publiée ouvre les pièces du dossier. Les modifications des fichiers de travail nécessitent une nouvelle publication.')
    text=text.replace('/^[=+@-]/','/^[\\s\\u0000-\\u001f]*[=+@-]/')
    return secure_html(text.replace('</main>',rule_html(source)+'</main>',1),source)

def build_generated():
    for rel,p in files.items():
        if p.suffix.lower()=='.md':
            text=p.read_text(encoding='utf-8-sig',errors='replace')
            heading=re.search(r'^#\s+(.+)',text,re.M)
            add(rel+'.html',page(heading[1] if heading else p.stem,markdown(text,rel+'.html'),rel+'.html',raw=rel))
        elif p.suffix.lower()=='.html':
            text=p.read_text(encoding='utf-8-sig')
            if rel=='OUVRIR-LES-DOSSIERS.html':
                add(rel,trusted_hub(text,rel));add('index.html',trusted_hub(text,'index.html'))
            elif rel=='6241 Léger/00_Lire_en_premier/index.html':
                # All CASE_DATA insertion is already escaped by the local generator.
                match=re.search(r'const DATA=([\s\S]*?);\s*const \$=',text)
                if not match:raise RuntimeError('Structure du portail Léger inconnue')
                data=json.loads(match[1]);base=CASES[0]+'/'
                data['files']=[f for f in data['files'] if base+f['path'] in files]
                data['resource_paths']=[r for r in data['resource_paths'] if base+r in files]
                data['counts']['files']=len(data['files']);data['counts']['distinct_contents']=len({f['sha256'] for f in data['files']})
                text=text[:match.start(1)]+escaped_json(data)+text[match.end(1):]
                add(rel,secure_html(text.replace('</main>',rule_html(rel)+'</main>',1),rel))
            else:
                reader=ArchiveReader(rel);reader.feed(text)
                add(rel+'.source.txt',p.read_bytes())
                add(rel,page('Index documentaire archivé',''.join(reader.out),rel,raw=rel+'.source.txt',note='Index historique : les textes conservent leur contexte d’origine. Les liens ont été rapprochés des pièces présentes; les commandes interactives de l’archive ne sont pas exécutées.'))
    for directory in sorted(directories):
        rel=directory+'/index.html'
        if rel in files or rel in generated:continue
        direct=[r for r in files if posixpath.dirname(r)==directory]
        subdirs=[d for d in directories if posixpath.dirname(d)==directory]
        items=[]
        for d in sorted(subdirs):items.append('<li><a href="'+rel_url(d+'/index.html',rel)+'">'+html.escape(posixpath.basename(d))+'/</a></li>')
        for r in sorted(direct):items.append('<li><a href="'+rel_url(routes.get(r,r),rel)+'">'+html.escape(posixpath.basename(r))+'</a></li>')
        add(rel,page(posixpath.basename(directory),'<h1>'+html.escape(posixpath.basename(directory))+'</h1><ul>'+''.join(items)+'</ul>',rel))
    add('assets/site-reader.css',(ROOT/'scripts/site/site-reader.css').read_bytes())
    js=(ROOT/'scripts/site/site-viewer.js').read_text(encoding='utf-8').replace('/*SITE_ROUTES*/',escaped_json(routes))
    add('assets/site-viewer.js',js);add('.nojekyll','')

class LinkAudit(HTMLParser):
    def __init__(self,source,known):super().__init__();self.source=source;self.known=known;self.errors=[];self.count=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        for name in ['href','src']:
            if name not in a:continue
            parts=urlsplit(a[name])
            if parts.scheme or parts.netloc or not parts.path:continue
            self.count+=1
            target=posixpath.normpath(posixpath.join(posixpath.dirname(self.source),unquote(parts.path)))
            if target not in self.known:self.errors.append({'source':self.source,'url':a[name],'target':target})
        if any(k.lower().startswith('on') for k in a):self.errors.append({'source':self.source,'error':'inline event attribute'})

def audit():
    known=set(files)|set(generated);broken=[];checked=0
    for rel,value in generated.items():
        if not rel.endswith('.html'):continue
        checker=LinkAudit(rel,known);checker.feed(value.decode('utf-8'));broken+=checker.errors;checked+=checker.count
    sizes={r:(len(generated[r]) if r in generated else p.stat().st_size) for r,p in files.items()}
    sizes.update({r:len(v) for r,v in generated.items()})
    extensions=Counter(PurePosixPath(r).suffix.lower() for r in sizes)
    return {'as_of':datetime.now(timezone.utc).isoformat(),'mode':'audit','source_files':len(files),'published_files':len(sizes)+1,
      'bytes':sum(sizes.values()),'megabytes_decimal':round(sum(sizes.values())/1_000_000,2),
      'largest_files':[{'path':r,'bytes':n} for r,n in sorted(sizes.items(),key=lambda x:x[1],reverse=True)[:15]],
      'extension_counts':dict(extensions),'mime_expectations':{e:MIMES.get(e,'static asset') for e in extensions},
      'markdown_readers':len(routes),'static_links_checked':checked,'broken_generated_links':broken,
      'archival_links_repaired':repairs,'unavailable_source_references':missing,
      'exclusions':exclusions,'secret_findings':secret_findings,'warnings':warnings,
      'rules':RULE,'source_hashes':hashes,
      'limits_reference':'https://docs.github.com/fr/pages/getting-started-with-github-pages/github-pages-limits'}

def write_site(report):
    expected=(ROOT/'dist-site').resolve()
    if OUT.is_symlink() or OUT.resolve()!=expected or not expected.is_relative_to(ROOT.resolve()):raise RuntimeError('Destination non autorisée')
    marker=OUT/'.site-build.json';previous=set()
    if OUT.exists():
        existing={p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()}
        if existing:
            if not marker.is_file():raise RuntimeError('dist-site existe sans manifeste de génération; aucun fichier supprimé')
            prior=json.loads(marker.read_text(encoding='utf-8'));previous=set(prior['output_files'])
            unknown=existing-previous-{'.site-build.json'}
            if unknown:raise RuntimeError('Fichiers non gérés dans dist-site : '+', '.join(sorted(unknown)[:5]))
    desired=set(files)|set(generated)
    for rel in previous-desired:
        p=OUT/rel
        if '..' in PurePosixPath(rel).parts or not p.resolve().is_relative_to(expected):raise RuntimeError('Ancien chemin non autorisé')
        if p.is_file():p.unlink()
    OUT.mkdir(exist_ok=True)
    incremental={'copied_source_files':0,'written_generated_files':0,'unchanged_files':0,'written_bytes':0,'unchanged_bytes':0}
    for rel,source in files.items():
        if rel in generated:continue
        target=OUT/rel
        if target.is_file() and digest(target.read_bytes())==hashes[rel]:
            incremental['unchanged_files']+=1;incremental['unchanged_bytes']+=target.stat().st_size;continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        incremental['copied_source_files']+=1;incremental['written_bytes']+=target.stat().st_size
    for rel,value in generated.items():
        target=OUT/rel
        if target.is_file() and digest(target.read_bytes())==digest(value):
            incremental['unchanged_files']+=1;incremental['unchanged_bytes']+=len(value);continue
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(value)
        incremental['written_generated_files']+=1;incremental['written_bytes']+=len(value)
    # Detect concurrent source changes before calling this a complete build.
    changed=[r for r,p in files.items() if digest(p.read_bytes())!=hashes[r]]
    report['source_changes_during_build']=changed
    report['incremental']=incremental
    report['mode']='build';report['output_files']=sorted(desired)
    report['output_hashes']={r:digest((OUT/r).read_bytes()) for r in desired}
    marker.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    if changed:raise RuntimeError('Sources modifiées durant la génération; relancer après stabilisation')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--build',action='store_true');parser.add_argument('--audit-only',action='store_true');args=parser.parse_args()
    if args.build and args.audit_only:parser.error('Choisir --build ou --audit-only')
    WORK.mkdir(parents=True,exist_ok=True)
    try:
        collect();build_generated();report=audit()
        if report['broken_generated_links']:raise RuntimeError('Liens de sortie invalides : '+str(report['broken_generated_links'][:3]))
        if report['bytes']>1_000_000_000:raise RuntimeError('Volume supérieur à la limite GitHub Pages de 1 Go')
        if args.build:write_site(report)
        (WORK/'remote-site-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({k:report[k] for k in ['mode','source_files','published_files','megabytes_decimal','markdown_readers','static_links_checked']}|{'broken_links':len(report['broken_generated_links']),'repaired_links':len(repairs),'unavailable_references':len(missing),'secret_findings':len(secret_findings)},ensure_ascii=False))
    except Exception as exc:
        (WORK/'remote-site-failure.json').write_text(json.dumps({'error':str(exc),'secret_findings':secret_findings,'missing':missing,'warnings':warnings},ensure_ascii=False,indent=2),encoding='utf-8')
        raise

if __name__=='__main__':main()
