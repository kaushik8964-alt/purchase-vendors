"""Download source files. Tries every candidate link on the page until one is a real Excel/CSV file."""
import re, sys, pathlib, requests, yaml
from urllib.parse import urljoin
from bs4 import BeautifulSoup
 
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
 
def candidates(page_url, pattern):
    r = requests.get(page_url, headers=HEADERS, timeout=60)
    print(f"  page status {r.status_code}, {len(r.text)} chars")
    r.raise_for_status()
    found, hits = [], []
    for a in BeautifulSoup(r.text, "lxml").find_all("a", href=True):
        url, text = urljoin(page_url, a["href"]), a.get_text(" ", strip=True)
        found.append((text, url))
        if re.search(pattern, f"{url} {text}", re.I):
            hits.append(url)
    if not hits:
        print("  no link matched. Links seen on page:")
        for t, u in found[:60]: print(f"    {t[:50]!r} -> {u}")
    return list(dict.fromkeys(hits))
 
def is_table_file(content):
    return content[:2] == b"PK" or content[:4] == b"\xd0\xcf\x11\xe0"   # xlsx(zip) or old xls
 
def main():
    ok = 0
    for s in yaml.safe_load(open("sources.yaml"))["sources"]:
        if not s.get("direct_url") and not s.get("page_url"): continue
        print(f"{s['name']}:")
        try:
            urls = [s["direct_url"]] if s.get("direct_url") else candidates(s["page_url"], s.get("link_regex", r"xlsx|excel"))
            if not urls: raise RuntimeError("no candidate links")
            done = False
            for url in urls[:8]:
                r = requests.get(url, headers=HEADERS, timeout=180)
                print(f"  try {url} -> {r.status_code}, {len(r.content)//1024} KB, type {r.headers.get('content-type','?')}")
                if r.ok and is_table_file(r.content):
                    p = pathlib.Path(s["file"]); p.parent.mkdir(parents=True, exist_ok=True)
                    p.write_bytes(r.content); ok += 1; done = True
                    print(f"OK   saved {p}"); break
            if not done: raise RuntimeError("none of the candidate links was an Excel file (blocked, or the list is a different format)")
        except Exception as e:
            print(f"FAIL {s['name']}: {e}", file=sys.stderr)
    print(f"{ok} source(s) downloaded")
 
if __name__ == "__main__":
    main()
 
