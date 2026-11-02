"""Merge public vendor lists into one SQLite DB. Run: python ingest.py"""
import sqlite3, re, pathlib, yaml, pandas as pd

FIELDS = ["vendor","product","country","state","vendor_type","licence_no","email","phone","website","reference_id","status","certification"]

def norm(name):
    n = re.sub(r"[^a-z0-9 ]", " ", str(name).lower())
    n = re.sub(r"\b(pvt|private|ltd|limited|co|inc|llc|gmbh|corp|corporation|company)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()

def load(src):
    p = pathlib.Path(src["file"])
    if not p.exists():
        print(f"skip {src['name']}: {p} not found"); return None
    magic = p.read_bytes()[:4]
    if p.suffix == ".csv": raw = pd.read_csv(p, header=None, dtype=str)
    else: raw = pd.read_excel(p, header=None, dtype=str, engine="xlrd" if magic == b"\xd0\xcf\x11\xe0" else "openpyxl")
    want = str(src["columns"]["vendor"]).strip().lower()
    hdr = next((i for i in range(min(30, len(raw))) if want in [str(v).strip().lower() for v in raw.iloc[i]]), None)
    if hdr is None:
        print(f"skip {src['name']}: vendor column '{want}' not found - fix sources.yaml. First rows seen:")
        print(raw.head(5).to_string()); return None
    df = raw.iloc[hdr + 1:].copy(); df.columns = [str(c).strip().lower() for c in raw.iloc[hdr]]
    cols = {k: str(v).strip().lower() for k, v in src["columns"].items()}
    out = pd.DataFrame({f: df[cols[f]] if f in cols and cols[f] in df else "" for f in FIELDS})
    if not (out["vendor_type"] != "").any(): out["vendor_type"] = src.get("default_type", "")
    out["source"] = src["name"]
    return out.fillna("").astype(str)

def main():
    cfg = yaml.safe_load(open("sources.yaml"))
    frames = [f for f in (load(s) for s in cfg["sources"]) if f is not None]
    if not frames: raise SystemExit("No source files found in data/raw/")
    df = pd.concat(frames, ignore_index=True)
    df["vendor_key"] = df["vendor"].map(norm)
    df["product"] = df["product"].str.strip().str.title()
    df = df[df.vendor_key != ""].drop_duplicates(["vendor_key","product","source","reference_id"])
    df["updated"] = pd.Timestamp.now().strftime("%Y-%m-%d")
    with sqlite3.connect("vendors.db") as c:
        df.to_sql("vendors", c, if_exists="replace", index=False)
    print(f"{len(df)} rows, {df.vendor_key.nunique()} unique vendors")

if __name__ == "__main__":
    main()
