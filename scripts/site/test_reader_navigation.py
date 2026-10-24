"""Navigation regression tests; temporary fixtures only, never writes dist-site."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote,urlsplit
import importlib.util,json,os,posixpath,re,subprocess,tempfile,unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('remote_site_navigation',ROOT/'scripts/build_remote_site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)
NODE=Path.home()/'.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'

class Tags(HTMLParser):
    def __init__(self,text):super().__init__();self.tags=[];self.feed(text)
    def handle_starttag(self,tag,attrs):self.tags.append((tag,dict(attrs)))

class NavigationTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'scripts/site/.test-tmp';scratch.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='reader-',dir=scratch)
        assert Path(self.temp.name).resolve().is_relative_to(scratch.resolve())
        self.addCleanup(self.temp.cleanup)
        site.ROOT=Path(self.temp.name)
        for name in ['files','hashes','generated','routes']:getattr(site,name).clear()
        site.directories.clear()
        for name in ['warnings','exclusions','secret_findings','repairs','missing']:getattr(site,name).clear()
        self.doc='HARMONY MOVERS/12_Remise/Guide été.md'
        self.source='HARMONY MOVERS/12_Remise/index.html'
        self.register(self.doc,b'# Guide\n\n## Pieces\n')
        self.register('HARMONY MOVERS/12_Remise/Pièce (1).pdf',b'pdf test')
        self.register('HARMONY MOVERS/12_Remise/image.png',b'image test')
        site.routes[self.doc]=self.doc+'.html'

    def register(self,rel,data):
        p=site.ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        site.files[rel]=p;site.hashes[rel]=site.digest(data)
        parent=posixpath.dirname(rel)
        while parent:site.directories.add(parent);parent=posixpath.dirname(parent)

    def target(self,url):
        return posixpath.normpath(posixpath.join(posixpath.dirname(self.source),unquote(urlsplit(url).path)))

    def test_markdown_opens_reader_with_query_and_anchor(self):
        link=site.resolve_link('Guide%20%C3%A9t%C3%A9.md?mode=lecture#pièces',self.source)
        self.assertEqual(self.target(link),self.doc+'.html')
        self.assertIn('?mode=lecture#pi%C3%A8ces',link)

    def test_download_keeps_original(self):
        self.assertEqual(self.target(site.resolve_link('Guide été.md',self.source,raw=True)),self.doc)

    def test_workspace_file_uri_is_portable(self):
        link=site.resolve_link((site.ROOT/self.doc).as_uri()+'#pièces',self.source)
        self.assertEqual(self.target(link),self.doc+'.html')
        self.assertNotIn('file:',link)

    @unittest.skipUnless(os.name=='nt','Windows drive path behavior')
    def test_windows_path_preserves_fragment(self):
        link=site.resolve_link(str(site.ROOT/self.doc)+'#pièces',self.source)
        self.assertEqual(self.target(link),self.doc+'.html')
        self.assertTrue(link.endswith('#pi%C3%A8ces'))

    def test_outside_workspace_never_suffix_matched(self):
        self.assertIsNone(site.resolve_link((site.ROOT.parent/'Guide été.md').as_uri(),self.source))

    def test_existing_public_markdown_url_becomes_portable_reader(self):
        value='https://takatakca.github.io/assurance-6241/'+self.doc+'?mode=1#pièces'
        link=site.resolve_link(value,self.source)
        self.assertEqual(self.target(link),self.doc+'.html')
        self.assertNotIn('https:',link)
        self.assertIn('?mode=1#pi%C3%A8ces',link)

    def test_other_repository_and_remote_citations_unchanged(self):
        for value in ['https://takatakca.github.io/other/Guide.md','https://example.org/Guide.md','mailto:avocat@example.org']:
            self.assertEqual(site.resolve_link(value,self.source),value)

    def test_repository_and_root_relative_resources(self):
        for value in ['/assurance-6241/'+self.doc,'/'+self.doc]:
            self.assertEqual(self.target(site.resolve_link(value,self.source)),self.doc+'.html')

    def test_missing_explicit_path_not_guessed_from_same_filename(self):
        self.assertIsNone(site.resolve_link('https://takatakca.github.io/assurance-6241/ancien/Guide été.md',self.source))
        self.assertIsNone(site.resolve_link('/absent/Guide été.md',self.source))

    def test_unsafe_urls_and_foreign_file_hosts_still_blocked(self):
        for value in ['javascript:alert(1)','data:text/html,x','file://remote-host/share/Guide.md','//evil.example/x','bad\x00name']:
            self.assertIsNone(site.resolve_link(value,self.source))

    def test_archive_keeps_ids_named_anchors_and_table_span(self):
        reader=site.ArchiveReader(self.source)
        reader.feed('<a href="#factures">Table</a><h2 id="factures">Factures</h2><a name="annexe"></a><span id="note">Note</span><table><tr><td colspan="2" onclick="evil()">Somme</td></tr></table>')
        tags=Tags(''.join(reader.out)).tags
        self.assertIn(('h2',{'id':'factures'}),tags)
        self.assertIn(('span',{'id':'annexe'}),tags)
        self.assertIn(('span',{'id':'note'}),tags)
        self.assertIn(('td',{'colspan':'2'}),tags)
        ids={a['id'] for _,a in tags if 'id' in a}
        self.assertTrue(all(unquote(a['href'][1:]) in ids for _,a in tags if a.get('href','').startswith('#')))
        self.assertNotIn('onclick',''.join(reader.out))

    def test_archived_links_choose_reader_or_explicit_download(self):
        reader=site.ArchiveReader(self.source)
        reader.feed('<a href="Guide été.md">Lire</a><a download href="Guide été.md">Source</a><img id="photo" src="image.png" alt="Vue">')
        tags=Tags(''.join(reader.out)).tags
        links=[a for tag,a in tags if tag=='a']
        self.assertEqual(self.target(links[0]['href']),self.doc+'.html')
        self.assertEqual(self.target(links[1]['href']),self.doc)
        self.assertIn('download',links[1])
        self.assertTrue(any(a.get('id')=='photo' for tag,a in tags if tag=='img'))

    def test_ambiguous_archival_annex_is_not_relinked(self):
        self.register('HARMONY MOVERS/a/annexe.pdf',b'version a')
        self.register('HARMONY MOVERS/b/annexe.pdf',b'version b')
        self.assertIsNone(site.resolve_link('annexe.pdf',self.source))

    def test_identical_archival_annex_can_be_relinked(self):
        self.register('HARMONY MOVERS/a/annexe.pdf',b'meme original')
        self.register('HARMONY MOVERS/b/annexe.pdf',b'meme original')
        link=site.resolve_link('annexe.pdf',self.source)
        self.assertIn(self.target(link),{'HARMONY MOVERS/a/annexe.pdf','HARMONY MOVERS/b/annexe.pdf'})

    def test_markdown_parentheses_spaces_and_unicode_filename(self):
        result=site.inline('[Original](<Pièce (1).pdf>) [Guide](Guide été.md)',self.source)
        links=[a['href'] for t,a in Tags(result).tags if t=='a']
        self.assertEqual(len(links),2)
        self.assertEqual(self.target(links[0]),'HARMONY MOVERS/12_Remise/Pièce (1).pdf')
        self.assertEqual(self.target(links[1]),self.doc+'.html')

    def test_static_portal_link_upgraded_without_touching_script_text(self):
        script='<script>const example=\'<a href="Guide été.md">example</a>\';</script>'
        result=site.rewrite_reading_links(script+'<a href="Guide été.md">Lire</a><a download href="Guide été.md">Source</a>',self.source)
        self.assertTrue(result.startswith(script))
        links=[a for tag,a in Tags(result).tags if tag=='a']
        self.assertEqual(self.target(links[0]['href']),self.doc+'.html')
        self.assertEqual(self.target(links[1]['href']),self.doc)

    @unittest.skipUnless(NODE.is_file(),'Bundled Node required for live navigation evaluation')
    def test_hub_links_use_reader_before_viewer_enhancement(self):
        cases=[{'name':'Harmony','files':[{'path':self.doc,'sha256':'x'}],'guides':[{'path':self.doc}]}]
        text='<html><head></head><body><main></main><script>const CASES='+json.dumps(cases)+'; const $=id=>id;const href=p=>p.split(\'/\').map(encodeURIComponent).join(\'/\');</script></body></html>'
        output=site.trusted_hub(text,'index.html')
        function=re.search(r'const readingRoutes=.*?const href=.*?;',output).group(0)
        result=subprocess.run([str(NODE),'-e',function+'process.stdout.write(JSON.stringify(href('+json.dumps(self.doc)+')));'],check=True,capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(unquote(json.loads(result.stdout)),self.doc+'.html')
        # Metadata still records the exact source path, not a generated reader.
        saved=json.loads(re.search(r'const CASES=(.*?);\s*const \$=',output,re.S)[1])
        self.assertEqual(saved[0]['files'][0]['path'],self.doc)

if __name__=='__main__':unittest.main(verbosity=2)
