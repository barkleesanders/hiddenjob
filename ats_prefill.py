#!/usr/bin/env python3
"""Optional local ATS prefill adapter for a staged Hiddenjob record.

Requires a user-installed ``fcdp`` command. It opens one tab, fills only fields
matched to keys in a gitignored profile, attaches a local resume when a visible
file input exists, saves a screenshot/result, and stops for review. Submission
needs both --submit and HIDDENJOB_AUTOSUBMIT=1 and is only recorded after a
post-click confirmation phrase is present.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

FIELD_PATTERNS = [
    (r"first.?name|given.?name|^fname$", "first_name"),
    (r"last.?name|family.?name|surname|^lname$", "last_name"),
    (r"^(full.?)?name$|candidate name", "full_name"),
    (r"e-?mail", "email"), (r"phone|mobile|tel\\b", "phone"),
    (r"linkedin", "linkedin"), (r"^city$|city\\b", "city"),
    (r"state/province|region|^state$", "state"), (r"country", "country"),
]


def call(binary: str, *args: str, timeout: int = 60) -> str:
    result = subprocess.run([binary, *args], text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"browser adapter failed: {result.stderr.strip()[-300:]}")
    return result.stdout.strip()


def open_tab(binary: str, url: str) -> str:
    output = call(binary, "open", url)
    match = re.search(r"\\b(\\d{5,})\\b", output)
    if not match:
        raise RuntimeError("could not determine browser tab id")
    return match.group(1)


def page_state(binary: str, tab: str) -> dict:
    code = r'''(() => {
      const visible = e => { const r=e.getBoundingClientRect(); return e.type !== 'hidden' && r.width>0 && r.height>0; };
      const label = e => e.labels && e.labels[0] ? e.labels[0].innerText : '';
      const fields = [...document.querySelectorAll('input,textarea,select')].filter(visible);
      return JSON.stringify({
        url: location.href, title: document.title,
        text: (document.body?.innerText || '').slice(0,12000),
        captcha: /recaptcha|hcaptcha|captcha/i.test(document.documentElement.outerHTML.slice(0,300000)),
        password: !!document.querySelector('input[type=password]'),
        fields: fields.map((e,i) => ({i,tag:e.tagName,type:e.type||'',name:e.name||'',id:e.id||'',placeholder:e.placeholder||'',aria:e.getAttribute('aria-label')||'',label:label(e),value:e.value||''}))
      });
    })()'''
    raw = call(binary, "js", tab, code)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return json.loads(json.loads(raw))


def set_value(binary: str, tab: str, index: int, value: str) -> None:
    payload = json.dumps(value)
    code = f'''(() => {{
      const visible=e=>{{const r=e.getBoundingClientRect();return e.type!=='hidden'&&r.width>0&&r.height>0}};
      const e=[...document.querySelectorAll('input,textarea,select')].filter(visible)[{index}]; if(!e)return 'missing';
      if(e.tagName==='SELECT'){{const o=[...e.options].find(x=>x.text.trim().toLowerCase()==={payload}.toLowerCase());if(!o)return 'no-option';e.value=o.value}}
      else{{const p=e.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(p,'value').set.call(e,{payload})}}
      e.dispatchEvent(new Event('input',{{bubbles:true}}));e.dispatchEvent(new Event('change',{{bubbles:true}}));return 'ok';
    }})()'''
    call(binary, "js", tab, code)


def attach_resume(binary: str, tab: str, resume: Path) -> str:
    if not resume.exists() or not resume.is_file():
        return "resume path is missing"
    doc = json.loads(call(binary, "raw", tab, "DOM.getDocument", '{"depth":0}'))["result"]["root"]["nodeId"]
    query = json.dumps({"nodeId": doc, "selector": "input[type=file]"})
    node = json.loads(call(binary, "raw", tab, "DOM.querySelector", query))["result"].get("nodeId")
    if not node:
        return "no visible file input"
    call(binary, "raw", tab, "DOM.setFileInputFiles", json.dumps({"nodeId": node, "files": [str(resume)]}))
    return "attached resume"


def click_submit(binary: str, tab: str) -> str:
    code = r'''(() => { const e=[...document.querySelectorAll('button,input[type=submit]')].find(x=>/submit|send application|apply now|finish/i.test(x.innerText||x.value||'')&&x.getBoundingClientRect().width>0);if(!e)return 'none';e.scrollIntoView();e.click();return 'clicked'; })()'''
    return call(binary, "js", tab, code)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--url", required=True); p.add_argument("--profile", required=True)
    p.add_argument("--evidence-dir", required=True); p.add_argument("--submit", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    profile = json.loads(Path(args.profile).read_text())
    required = ("full_name", "email", "phone", "resume_path")
    missing = [key for key in required if not str(profile.get(key, "")).strip()]
    if missing:
        raise SystemExit(f"profile missing required keys: {', '.join(missing)}")
    if args.submit and os.environ.get("HIDDENJOB_AUTOSUBMIT") != "1":
        raise SystemExit("--submit requires HIDDENJOB_AUTOSUBMIT=1")
    output = Path(args.evidence_dir); output.mkdir(parents=True, exist_ok=True)
    result = {"url": args.url, "captured_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "outcome": "planned", "filled": [], "needs_human": []}
    if args.dry_run:
        result["planned_action"] = "submit" if args.submit else "prefill"
        print(json.dumps(result, indent=2)); return 0
    binary = os.environ.get("HIDDENJOB_FCDP", "fcdp")
    if not shutil.which(binary):
        raise SystemExit("fcdp is not installed or not on PATH; use --dry-run or install a compatible local browser bridge.")
    tab = open_tab(binary, args.url); result["tab"] = tab
    time.sleep(2)
    state = page_state(binary, tab); result["page"] = {key: state.get(key) for key in ("url", "title", "captcha", "password")}
    if state.get("captcha"):
        result["needs_human"].append("CAPTCHA present; never solved by this tool")
    if state.get("password"):
        result["needs_human"].append("login/account wall present; password entry and account creation are human-only")
    for field in state.get("fields", []):
        if field.get("type") in {"file", "checkbox", "radio", "submit", "button"} or field.get("value"):
            continue
        label = " ".join(str(field.get(k, "")) for k in ("name", "id", "placeholder", "aria", "label")).lower()
        for pattern, key in FIELD_PATTERNS:
            if re.search(pattern, label) and profile.get(key):
                set_value(binary, tab, int(field["i"]), str(profile[key])); result["filled"].append(key); break
    result["resume"] = attach_resume(binary, tab, Path(profile["resume_path"]).expanduser())
    try:
        call(binary, "shot", tab, str(output / "prefilled.png")); result["screenshot"] = str(output / "prefilled.png")
    except RuntimeError as exc:
        result["screenshot_error"] = str(exc)
    if args.submit and not result["needs_human"]:
        result["submit_click"] = click_submit(binary, tab); time.sleep(3)
        after = page_state(binary, tab)
        result["confirmation_text"] = after.get("text", "")[:800]
        result["outcome"] = "submitted" if result["submit_click"] == "clicked" and re.search(r"thank you|application received|submission received", after.get("text", ""), re.I) else "submit-unverified"
    else:
        result["outcome"] = "needs_human" if result["needs_human"] else "prefilled"
    (output / "prefill-result.json").write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    return 0 if result["outcome"] in {"prefilled", "submitted"} else 2


if __name__ == "__main__":
    raise SystemExit(main())

