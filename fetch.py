"""Download source files. Run by GitHub Actions weekly. Never fails the whole run if one source fails."""
import re, sys, pathlib, requests, yaml
from urllib.parse import urljoin
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; vendor-finder/1.0; procurement research)"}

def find_link(page_url, pattern):
    html = requests.get(page_url, headers=HEADERS, timeout=60).text
    links = [urljoin(page_url, a["href"]) for a in BeautifulSoup(html, "lxml").find_all("a", href=True)]
    hits = [l for l in links if re.search(pattern, l.split("?")[0], re.I)]
    return hits[0] if hits else None

def main():
    ok = 0
    for s in yaml.safe_load(open("sources.yaml"))["sources"]:
        url = s.get("direct_url") or (s.get("page_url") and find_link(s["page_url"], s.get("link_regex", r"\.xlsx$")))
        if not s.get("direct_url") and not s.get("page_url"): continue
        try:
            if not url: raise RuntimeError("no matching file link found on page")
            r = requests.get(url, headers=HEADERS, timeout=180); r.raise_for_status()
            p = pathlib.Path(s["file"]); p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(r.content); ok += 1
            print(f"OK   {s['name']}: {url} ({len(r.content)//1024} KB)")
        except Exception as e:
            print(f"FAIL {s['name']}: {e}", file=sys.stderr)
    print(f"{ok} source(s) downloaded")

if __name__ == "__main__":
    main()
