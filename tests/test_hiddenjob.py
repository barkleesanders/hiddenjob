import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

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
