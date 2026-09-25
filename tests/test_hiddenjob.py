import argparse
import importlib.util
import json
import sqlite3
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("hiddenjob", Path(__file__).parents[1] / "hiddenjob.py")
hiddenjob = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hiddenjob)


class HiddenjobTests(unittest.TestCase):
    def test_perm_like_marker_classification(self):
        result = hiddenjob.classify("Minimum Requirements. Foreign equivalent accepted. Please send resumes. Job duties include system design.")
        self.assertEqual(result["classification"], "perm-like")
        self.assertGreaterEqual(result["perm_score"], 5)


    def test_normal_job_is_not_visa_classified(self):
        result = hiddenjob.classify("Build reliable services with a collaborative engineering team.")
        self.assertEqual(result["classification"], "unclassified")


    def test_sitemap_leaf_and_index_parsing(self):
        children, leaves = hiddenjob.sitemap_entries("<sitemapindex><sitemap><loc>https://example.test/jobs.xml</loc></sitemap></sitemapindex>")
        self.assertEqual(children, ["https://example.test/jobs.xml"]); self.assertFalse(leaves)
        children, leaves = hiddenjob.sitemap_entries("<urlset><url><loc>https://example.test/jobs/1</loc></url></urlset>")
        self.assertFalse(children); self.assertEqual(leaves, ["https://example.test/jobs/1"])

    def test_ordinary_captcha_word_is_not_a_challenge(self):
        self.assertFalse(hiddenjob.is_challenge_page("This job describes a CAPTCHA accessibility option.".lower()))
        self.assertTrue(hiddenjob.is_challenge_page("<title>Just a moment...</title> cf-chl-xyz".lower()))

    def test_jobsnow_job_path_excludes_non_posting_page(self):
        pattern = r"^/jobs/\d+(?:[-/]|$)"
        self.assertIsNotNone(hiddenjob.re.search(pattern, "/jobs/640082644-software-engineer"))
        self.assertIsNone(hiddenjob.re.search(pattern, "/jobs/apply-by-mail"))

    def test_ats_dry_run_uses_private_profile_without_browser(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); profile = root / "profile.json"
            profile.write_text(json.dumps({"full_name":"Example Name","email":"example@example.test","phone":"+1-555-555-0100","resume_path":"/tmp/example.pdf"}))
            result = subprocess.run(["python3", str(Path(__file__).parents[1] / "ats_prefill.py"), "--url", "https://example.test/jobs/1", "--profile", str(profile), "--evidence-dir", str(root / "evidence"), "--dry-run"], text=True, capture_output=True, check=True)
            self.assertEqual(json.loads(result.stdout)["outcome"], "planned")

    def test_read_url_list_accepts_hiddenjobs_jsonl_and_discards_other_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "hiddenjobs-urls.jsonl"
            path.write_text('{"url":"https://example.test/jobs/1","email":"private@example.test"}\n{"url":"https://example.test/jobs/2","description":"private text"}\n')
            self.assertEqual(hiddenjob.read_url_list(path), ["https://example.test/jobs/1", "https://example.test/jobs/2"])

    def test_sync_combines_inline_and_file_urls_without_duplicates(self):
        page = '<script type="application/ld+json">{"@type":"JobPosting","title":"Engineer","description":"Build services"}</script>'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "config").mkdir(); config = root / "config" / "targets.json"; imports = root / "config" / "urls.jsonl"
            imports.write_text('{"url":"https://example.test/jobs/2","email":"private@example.test"}\n')
            config.write_text(json.dumps({"data_dir":"ledger", "sources":[{"name":"import", "urls":["https://example.test/jobs/1", "https://example.test/jobs/2"], "url_list_file":"urls.jsonl"}]}))
            args = argparse.Namespace(config=str(config), limit=10, max_sitemap_urls=10)
            with mock.patch.object(hiddenjob, "fetch", side_effect=lambda url: (page, url)) as fetch:
                self.assertEqual(hiddenjob.cmd_sync(args), 0)
            self.assertEqual(fetch.call_count, 2)
            con = sqlite3.connect(root / "ledger" / "hiddenjob.sqlite3")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0], 2)

    def test_sync_skips_source_when_all_seeds_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "config").mkdir(); config = root / "config" / "targets.json"
            config.write_text(json.dumps({"data_dir": "ledger", "sources": [
                {"name": "flaky", "robots_url": "https://example.test/robots.txt",
                 "sitemap_fallback": "https://example.test/sitemap.xml", "job_url_pattern": "/jobs/"},
                {"name": "steady", "urls": ["https://example.test/jobs/9"]},
            ]}))
            page = '<h1>Engineer</h1><p>Build services</p>'
            args = argparse.Namespace(config=str(config), limit=10, max_sitemap_urls=10)
            def fake_fetch(url):
                if "robots.txt" in url:
                    raise hiddenjob.FetchBlocked("https://example.test/robots.txt: timed out")
                return (page, url)
            with mock.patch.object(hiddenjob, "fetch", side_effect=fake_fetch):
                self.assertEqual(hiddenjob.cmd_sync(args), 0)
            con = sqlite3.connect(root / "ledger" / "hiddenjob.sqlite3")
            self.assertEqual(con.execute("SELECT url FROM jobs").fetchone()[0], "https://example.test/jobs/9")

    def test_sync_uses_explicit_sitemap_urls_without_robots(self):
        sitemap = '<urlset><url><loc>https://example.test/jobs/1</loc></url><url><loc>https://example.test/about</loc></url></urlset>'
        page = '<h1>Engineer</h1><p>Build services</p>'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "config").mkdir(); config = root / "config" / "targets.json"
            config.write_text(json.dumps({"data_dir":"ledger", "sources":[{"name":"sitemap-import", "sitemap_urls":["https://example.test/jobs.xml"], "job_url_pattern":"/jobs/"}]}))
            args = argparse.Namespace(config=str(config), limit=10, max_sitemap_urls=10)
            with mock.patch.object(hiddenjob, "fetch", side_effect=lambda url: (sitemap, url) if url.endswith(".xml") else (page, url)):
                self.assertEqual(hiddenjob.cmd_sync(args), 0)
            con = sqlite3.connect(root / "ledger" / "hiddenjob.sqlite3")
            self.assertEqual(con.execute("SELECT url FROM jobs").fetchone()[0], "https://example.test/jobs/1")

    def test_sync_still_rejects_source_with_no_urls_configured(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "config").mkdir(); config = root / "config" / "targets.json"
            config.write_text(json.dumps({"data_dir": "ledger", "sources": [{"name": "empty"}]}))
            args = argparse.Namespace(config=str(config), limit=10, max_sitemap_urls=10)
            with self.assertRaises(SystemExit):
                hiddenjob.cmd_sync(args)

    def test_ats_greenhouse_normalizes_postings(self):
        payload = {"jobs": [{"absolute_url": "https://job-boards.greenhouse.io/acme/jobs/1", "title": "Product Manager",
                             "updated_at": "2026-09-20T00:00:00Z", "content": "<p>Own the roadmap.</p>"}]}
        with mock.patch.object(hiddenjob, "fetch_json", return_value=payload):
            postings = hiddenjob.ats_board_postings("greenhouse", "acme", "Acme")
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings[0]["url"], "https://job-boards.greenhouse.io/acme/jobs/1")
        self.assertEqual(postings[0]["title"], "Product Manager")
        self.assertEqual(postings[0]["company"], "Acme")
        self.assertIn("Own the roadmap.", postings[0]["description"])

    def test_ats_ashby_normalizes_postings(self):
        payload = {"jobs": [{"id": "abc", "jobUrl": "https://jobs.ashbyhq.com/acme/abc", "title": "IT Support Engineer",
                             "publishedAt": "2026-09-19T00:00:00Z", "descriptionHtml": "<p>Help users.</p>"}]}
        with mock.patch.object(hiddenjob, "fetch_json", return_value=payload):
            postings = hiddenjob.ats_board_postings("ashby", "acme", "Acme")
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings[0]["url"], "https://jobs.ashbyhq.com/acme/abc")
        self.assertIn("Help users.", postings[0]["description"])

    def test_ats_lever_normalizes_postings(self):
        payload = [{"hostedUrl": "https://jobs.lever.co/acme/xyz", "text": "Forward Deployed Engineer",
                    "createdAt": 1758758400000, "description": "<p>Work with customers.</p>"}]
        with mock.patch.object(hiddenjob, "fetch_json", return_value=payload):
            postings = hiddenjob.ats_board_postings("lever", "acme", "Acme")
        self.assertEqual(len(postings), 1)
        self.assertEqual(postings[0]["title"], "Forward Deployed Engineer")
        self.assertTrue(postings[0]["date_posted"].startswith("2025-09-25"))

    def test_ats_unsupported_kind_is_refused(self):
        with self.assertRaises(hiddenjob.FetchBlocked):
            hiddenjob.ats_board_postings("linkedin", "1337", "LinkedIn")

    def test_ats_timeout_passes_through_to_fetch(self):
        payload = {"jobs": []}
        with mock.patch.object(hiddenjob, "fetch_json", return_value=payload) as fetch:
            hiddenjob.ats_board_postings("greenhouse", "acme", "Acme", timeout=7)
        fetch.assert_called_once()
        self.assertEqual(fetch.call_args.kwargs.get("timeout"), 7)

    def test_host_sources_only_enables_explicit_hosts(self):
        cfg = {"company_hosts": [{"company": "On", "host": "careers.on.test", "enabled": True},
                                 {"company": "Off", "host": "careers.off.test", "enabled": False},
                                 {"company": "Default", "host": "careers.default.test"}]}
        sources = hiddenjob.host_sources(cfg)
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0]["name"], "host:careers.on.test")
        self.assertEqual(sources[0]["robots_url"], "https://careers.on.test/robots.txt")
        self.assertIn("job_url_regex", sources[0])

    def test_sync_pulls_ats_targets_and_skips_unsupported(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); (root / "config").mkdir()
            config = root / "config" / "targets.json"
            registry = root / "config" / "targets-local.json"
            registry.write_text(json.dumps({"targets": [
                {"company": "Acme", "ats": {"kind": "ashby", "board": "acme"}},
                {"company": "Stale", "ats": {"kind": "ashby", "board": "stale"}, "enabled": False},
                {"company": "Nope", "ats": {"kind": "linkedin", "board": "1337"}},
            ]}))
            config.write_text(json.dumps({"data_dir": "ledger", "sources": [], "ats_targets_file": "targets-local.json"}))
            postings = [{"url": "https://jobs.ashbyhq.com/acme/1", "title": "Engineer", "company": "Acme",
                         "date_posted": "", "description": "Build services", "evidence_text": "{}"}]
            args = argparse.Namespace(config=str(config), limit=10, max_sitemap_urls=10)
            def fake_boards(kind, board, company, timeout=15):
                if kind == "linkedin":
                    raise hiddenjob.FetchBlocked("unsupported ATS board kind: linkedin")
                return postings
            with mock.patch.object(hiddenjob, "ats_board_postings", side_effect=fake_boards):
                self.assertEqual(hiddenjob.cmd_sync(args), 0)
            rows = sqlite3.connect(root / "ledger" / "hiddenjob.sqlite3").execute("SELECT url, source FROM jobs").fetchall()
            self.assertEqual(len(rows), 1)
            row = rows[0]
            self.assertEqual(row[0], "https://jobs.ashbyhq.com/acme/1")
            self.assertEqual(row[1], "ats:ashby:acme")
            con = sqlite3.connect(root / "ledger" / "hiddenjob.sqlite3")
            self.assertTrue(con.execute("SELECT evidence_path FROM jobs").fetchone()[0].endswith(".json"))
