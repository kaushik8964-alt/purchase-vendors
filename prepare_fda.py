"""Run on YOUR computer once per quarter.
Usage:  python prepare_fda.py path/to/downloaded_FDA_file.xls
Shrinks the big FDA DMF list to active drug-substance (Type II) entries -> fda_dmf.csv
(small enough to upload through the GitHub website).
Needs:  pip install pandas xlrd openpyxl
"""
import sys, pandas as pd

src = sys.argv[1]
magic = open(src, "rb").read(4)
raw = pd.read_excel(src, header=None, dtype=str, engine="xlrd" if magic == b"\xd0\xcf\x11\xe0" else "openpyxl")
hdr = next((i for i in range(min(30, len(raw))) if "holder" in [str(v).strip().lower() for v in raw.iloc[i]]), None)
if hdr is None:
    print("Could not find a HOLDER column. First rows of the file:"); print(raw.head(8).to_string()); sys.exit(1)
df = raw.iloc[hdr + 1:].copy()
df.columns = [str(c).strip().upper() for c in raw.iloc[hdr]]
print("Columns found:", list(df.columns), "| rows:", len(df))
if "STATUS" in df: df = df[df["STATUS"].astype(str).str.strip().str.upper() == "A"]
if "TYPE" in df:   df = df[df["TYPE"].astype(str).str.strip().str.upper() == "II"]
df = df.dropna(subset=["HOLDER"])
df.to_csv("fda_dmf.csv", index=False)
print(f"Saved fda_dmf.csv with {len(df)} active Type II DMFs. Upload it to GitHub in data/raw/")
