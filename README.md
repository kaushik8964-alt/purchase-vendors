# Pharma Raw Material Vendor Finder (India)

Merges public regulatory lists of API/excipient suppliers into one searchable app.

## Public sources to download into `data/raw/`
| Source | What you get | Where |
|---|---|---|
| USFDA Drug Master Files list | DMF holders per substance | fda.gov (DMF list, Excel) |
| EDQM Certificates of Suitability (CEP) | Ph.Eur. certified API makers | extranet.edqm.eu (certification database, export) |
| WHO Prequalification – APIs | WHO-PQ'd API manufacturers | extranet.who.int/prequal |
| CDSCO | Form 41 import registrations, Written Confirmations (WC) list | cdsco.gov.in |
| EudraGMDP | EU GMP certificates, manufacturer addresses | eudragmdp.ema.europa.eu |
| Pharmexcil (member directory) | Indian exporters/suppliers | pharmexcil.com |
| Your own approved vendor list | Emails, phones, GMP status | `my_vendors.csv` (keep private) |

## Run
    pip install -r requirements.txt
    python ingest.py
    streamlit run app.py

Edit `sources.yaml` so column names match the files you download.

## Rules
- Only use sources whose terms allow it. Do NOT scrape IndiaMART/TradeIndia/Alibaba (ToS).
- Contacts come from company websites or your own records. Verify before RFQ.
- A vendor listed in 2+ independent sources is a stronger lead. Always still audit and qualify per your QA SOP.
- CDSCO registration is required for importing APIs into India. Check the vendor's current Form 41 before ordering.

## Fully automatic mode (GitHub does the work)
1. Push this repo to GitHub. In **Actions**, run **Refresh vendor DB** once (workflow_dispatch). It runs `fetch.py` (downloads sources that have a URL in `sources.yaml`), then `ingest.py`, and commits `vendors.db`. It repeats every Monday.
2. Open the run log. `OK` = downloaded, `FAIL` = fix that source (URL or column names).
3. Deploy the dashboard free: https://share.streamlit.io -> New app -> pick this repo -> main file `app.py`. You get a URL; search any raw material there.
4. For sources without a public download (EDQM, CDSCO PDFs), export manually and commit the file to `data/raw/`; the weekly job merges it.
