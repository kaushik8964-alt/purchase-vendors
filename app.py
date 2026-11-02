import os, sqlite3, pandas as pd, streamlit as st
st.set_page_config(page_title="Pharma RM Vendor Finder", layout="wide")
st.title("Pharma raw material vendor finder (India procurement)")

def has_data():
    if not os.path.exists("vendors.db"): return False
    try:
        with sqlite3.connect("vendors.db") as c:
            return c.execute("select count(*) from vendors").fetchone()[0] > 0
    except sqlite3.Error:
        return False

if not has_data():
    st.warning("No vendor data yet. Click the button to download the public lists and build the database "
               "(takes about a minute). If it fails, the message below says which source failed.")
    up = st.file_uploader("Or upload a source file here (e.g. the FDA DMF .xls/.xlsx you downloaded)", type=["xls","xlsx"])
    if up is not None and st.button("Use uploaded file"):
        import ingest, pathlib
        pathlib.Path("data/raw").mkdir(parents=True, exist_ok=True)
        pathlib.Path("data/raw/fda_dmf.xls").write_bytes(up.getvalue())   # ingest detects xls vs xlsx by content
        st.info("Merging... this can take a minute for the big FDA file.")
        try:
            ingest.main(); st.cache_data.clear(); st.rerun()
        except BaseException as e:
            st.error(f"Could not read the file: {e}. Column names in sources.yaml may not match this file.")
    if st.button("Build data now"):
        import fetch, ingest
        with st.spinner("Downloading and merging..."):
            try:
                fetch.main(); ingest.main()
                st.cache_data.clear(); st.rerun()
            except BaseException as e:   # ingest exits via SystemExit when no files exist
                st.error(f"Build failed: {e}. Check that data/raw/ has files, or that sources.yaml URLs/columns are right.")
    st.stop()

@st.cache_data
def load():
    with sqlite3.connect("vendors.db") as c:
        return pd.read_sql("select * from vendors", c)
df = load()

q = st.sidebar.text_input("Material / API name (e.g. paracetamol)")
country = st.sidebar.multiselect("Country", sorted(df.country[df.country != ""].unique()))
vtype = st.sidebar.multiselect("Type (manufacturer / distributor...)", sorted(df.vendor_type[df.vendor_type != ""].unique()))
state = st.sidebar.multiselect("Indian state", sorted(df.state[df.state != ""].unique()))
src = st.sidebar.multiselect("Source / certification", sorted(df.source.unique()))
if q: df = df[df["product"].str.contains(q, case=False, na=False)]
if country: df = df[df.country.isin(country)]
if vtype: df = df[df.vendor_type.isin(vtype)]
if state: df = df[df.state.isin(state)]
if src: df = df[df.source.isin(src)]

g = (df.groupby("vendor_key").agg(vendor=("vendor","first"), country=("country","first"), state=("state","max"),
     type=("vendor_type", lambda s: ", ".join(sorted(set(x for x in s if x)))), licence_no=("licence_no","max"),
     products=("product", lambda s: ", ".join(sorted(set(s))[:8])),
     sources=("source", lambda s: ", ".join(sorted(set(s)))),
     n_sources=("source","nunique"), email=("email","max"), phone=("phone","max"), website=("website","max"))
     .sort_values("n_sources", ascending=False).reset_index(drop=True))
st.caption(f"{len(g)} vendors | data updated {df.updated.max() if len(df) else '-'}")
st.dataframe(g, use_container_width=True)
st.download_button("Download CSV (for RFQ)", g.to_csv(index=False), "vendors.csv")
