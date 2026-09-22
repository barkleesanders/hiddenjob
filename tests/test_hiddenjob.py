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
