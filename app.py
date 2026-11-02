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
src = st.sidebar.multiselect("Source / certification", sorted(df.source.unique()))
if q: df = df[df["product"].str.contains(q, case=False, na=False)]
if country: df = df[df.country.isin(country)]
if src: df = df[df.source.isin(src)]

g = (df.groupby("vendor_key").agg(vendor=("vendor","first"), country=("country","first"),
     products=("product", lambda s: ", ".join(sorted(set(s))[:8])),
     sources=("source", lambda s: ", ".join(sorted(set(s)))),
     n_sources=("source","nunique"), email=("email","max"), phone=("phone","max"), website=("website","max"))
     .sort_values("n_sources", ascending=False).reset_index(drop=True))
st.caption(f"{len(g)} vendors | data updated {df.updated.max() if len(df) else '-'}")
st.dataframe(g, use_container_width=True)
st.download_button("Download CSV (for RFQ)", g.to_csv(index=False), "vendors.csv")
