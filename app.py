import sqlite3, pandas as pd, streamlit as st
st.set_page_config(page_title="Pharma RM Vendor Finder", layout="wide")
st.title("Pharma raw material vendor finder (India procurement)")

@st.cache_data
def load():
    return pd.read_sql("select * from vendors", sqlite3.connect("vendors.db"))
df = load()

q = st.sidebar.text_input("Material / API name (e.g. paracetamol)")
country = st.sidebar.multiselect("Country", sorted(df.country[df.country != ""].unique()))
src = st.sidebar.multiselect("Source / certification", sorted(df.source.unique()))
if q: df = df[df["product"].str.contains(q, case=False, na=False)]
if country: df = df[df.country.isin(country)]
if src: df = df[df.source.isin(src)]

# One row per vendor, showing how many independent sources list them (more sources = more trust)
g = (df.groupby("vendor_key").agg(vendor=("vendor","first"), country=("country","first"),
     products=("product", lambda s: ", ".join(sorted(set(s))[:8])),
     sources=("source", lambda s: ", ".join(sorted(set(s)))),
     n_sources=("source","nunique"), email=("email","max"), phone=("phone","max"), website=("website","max"))
     .sort_values("n_sources", ascending=False).reset_index(drop=True))
st.caption(f"{len(g)} vendors | data updated {df.updated.max() if len(df) else '-'}")
st.dataframe(g.drop(columns="vendor_key", errors="ignore"), use_container_width=True)
st.download_button("Download CSV (for RFQ)", g.to_csv(index=False), "vendors.csv")
