"""Exercise master publication boundaries with isolated local fixtures only."""
from pathlib import Path
import importlib.util,tempfile,unittest

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('master_publication',ROOT/'scripts/build_remote_site.py')
site=importlib.util.module_from_spec(spec);spec.loader.exec_module(site)

class MasterPublicationTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'scripts/site/.test-tmp';scratch.mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(prefix='master-',dir=scratch)
        assert Path(self.temp.name).resolve().is_relative_to(scratch.resolve())
        self.addCleanup(self.temp.cleanup);site.ROOT=Path(self.temp.name)
        for name in ('files','hashes','generated','routes'):getattr(site,name).clear()
        site.directories.clear()
        for name in ('warnings','exclusions','secret_findings','repairs','missing'):getattr(site,name).clear()
        for case in site.CASES:(site.ROOT/case).mkdir()
        self.put(site.RULE_PATH,site.RULE)
        self.put('scripts/site/site-reader.css','body { color: black; }')
        self.put('scripts/site/site-viewer.js','const routes=/*SITE_ROUTES*/;')
        self.launcher='<html><head></head><body><a href="'+site.MASTER_HOME+'">DOSSIER MAÎTRE</a></body></html>'
        self.put('OUVRIR-LES-DOSSIERS.html',self.launcher)
        self.home='<html><head><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'self\'"></head><body>'+site.RULE+'<script src="assets/app.js"></script></body></html>'
        self.put(site.MASTER_HOME,self.home)
        self.put(site.MASTER+'/assets/app.js','window.masterReady=true;')
        self.put(site.MASTER+'/assets/master.css','body { color: black; }')
        self.put(site.MASTER+'/06_Index_recherche/recherche-000.js','window.MASTER_CHUNKS=[];')
        for path in site.MASTER_LOCAL:self.put(path,'{"local":true}')

    def put(self,rel,text):
        p=site.ROOT/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')

    def test_master_assets_included_only_in_master_and_local_indexes_excluded(self):
        self.put(site.CASES[0]+'/untrusted.js','window.untrusted=true;')
        site.collect()
        self.assertIn(site.MASTER+'/assets/app.js',site.files)
        self.assertIn(site.MASTER+'/assets/master.css',site.files)
        self.assertIn(site.MASTER+'/06_Index_recherche/recherche-000.js',site.files)
        self.assertNotIn(site.CASES[0]+'/untrusted.js',site.files)
        self.assertFalse(set(site.files)&site.MASTER_LOCAL)
        self.assertTrue(site.MASTER_LOCAL.issubset({e['path'] for e in site.exclusions}))

    def test_master_and_launcher_bytes_preserved_and_audited(self):
        site.collect();site.build_generated();report=site.audit()
        self.assertEqual(site.generated[site.MASTER_HOME],self.home.encode())
        self.assertEqual(site.generated['index.html'],self.launcher.encode())
        self.assertEqual(site.generated['OUVRIR-LES-DOSSIERS.html'],self.launcher.encode())
        self.assertNotIn(site.MASTER_HOME+'.source.txt',site.generated)
        self.assertFalse(report['broken_generated_links'])
        # Pass-through pages still take part in the ordinary link audit.
        site.generated[site.MASTER_HOME]=b'<a href="absent.pdf">Missing</a>'
        self.assertTrue(any(e['target'].endswith('absent.pdf') for e in site.audit()['broken_generated_links']))

    def test_secret_scan_includes_master_javascript(self):
        self.put(site.MASTER+'/assets/app.js','const token="ghp_'+'A'*36+'";')
        with self.assertRaises(RuntimeError):site.collect()
        self.assertEqual(site.secret_findings,[{'path':site.MASTER+'/assets/app.js','kind':'github_token'}])

    def test_exact_master_link_recognizes_launcher_without_title_guessing(self):
        self.assertTrue(site.is_master_launcher(self.launcher))
        self.assertFalse(site.is_master_launcher('<h1>DOSSIER MAÎTRE</h1>'))
        self.assertFalse(site.is_master_launcher('<a href="https://example.org/'+site.MASTER_HOME+'">Master</a>'))

    def test_missing_master_home_fails_with_clear_error(self):
        (site.ROOT/site.MASTER_HOME).unlink()
        site.collect()
        with self.assertRaisesRegex(RuntimeError,'dossier maître absent'):site.build_generated()

    def test_remise_markdown_gets_reader_without_rewriting_master_html(self):
        rel=site.MASTER+'/04_Remise_et_suivis/Guide.md';self.put(rel,'# Guide\n')
        site.collect();site.build_generated()
        self.assertEqual(site.routes[rel],rel+'.html')
        self.assertIn('<h1',site.generated[rel+'.html'].decode())
        self.assertEqual(site.generated[site.MASTER_HOME],self.home.encode())

if __name__=='__main__':unittest.main()
