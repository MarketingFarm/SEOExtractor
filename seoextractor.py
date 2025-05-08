import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse

st.set_page_config(
    page_title="Multi-Tool Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nascondi label vuoti e colora la progress bar
st.markdown("""
<style>
  label[data-testid="stWidgetLabel"] { display: none !important; }
  .stProgress > div > div > div { background-color: #f63366 !important; }
</style>
""", unsafe_allow_html=True)

# Sidebar: logo e menu raggruppato
st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:20px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40"/>'
    '</div>',
    unsafe_allow_html=True
)

# Definizione delle sezioni e dei tool
menu = {
    "On-Page SEO": {
        "🔍 SEO Extractor": "seo",
        "🛠️ Altro Tool": "tool1"
    },
    "Technical SEO": {
        "🛠️ Tool A": "tool2",
        "🛠️ Tool B": "tool3"
    },
    "Off-Page SEO": {
        "🛠️ Tool C": "tool4",
        "🛠️ Tool D": "tool5"
    }
}

section = st.sidebar.selectbox("Sezione", list(menu.keys()))
tool_key = st.sidebar.selectbox("Tool", list(menu[section].keys()))
selected = menu[section][tool_key]

# Funzioni dei tool
BASE_HEADERS = {"User-Agent": "Mozilla/5.0"}
def estrai_info(url):
    resp = requests.get(url, headers=BASE_HEADERS, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    h1 = soup.find("h1")
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]
    title = soup.title
    desc = soup.find("meta", {"name":"description"})
    canonical = soup.find("link", rel="canonical")
    robots = soup.find("meta", {"name":"robots"})
    return {
        "H1": h1.get_text(strip=True) if h1 else "",
        "H2": " | ".join(h2s),
        "Meta title": title.get_text(strip=True) if title else "",
        "Meta title length": len(title.get_text(strip=True)) if title else 0,
        "Meta description": desc["content"].strip() if desc and desc.has_attr("content") else "",
        "Meta description length": len(desc["content"].strip()) if desc and desc.has_attr("content") else 0,
        "Canonical": canonical["href"].strip() if canonical and canonical.has_attr("href") else "",
        "Meta robots": robots["content"].strip() if robots and robots.has_attr("content") else ""
    }

def run_seo_extractor():
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai H1, H2, Meta title/length, Meta description/length, Canonical e Meta robots.")
    st.divider()
    col1, col2 = st.columns([2,1], gap="large")
    with col1:
        urls = st.text_area("Incolla URL (una per riga)", height=200, placeholder="https://esempio.com/p1\nhttps://esempio.com/p2")
    with col2:
        fields = st.pills("Campi da estrarre", list(estrai_info("https://www.example.com").keys()), selection_mode="multi", default=[])
    if st.button("🚀 Avvia Estrazione"):
        if not fields:
            st.error("Seleziona almeno un campo.")
            return
        url_list = [u.strip() for u in urls.splitlines() if u.strip()]
        if not url_list:
            st.error("Inserisci almeno un URL valido.")
            return
        prog = st.progress(0)
        results = []
        with st.spinner("Analisi in corso…"):
            for i,u in enumerate(url_list,1):
                info = estrai_info(u)
                row = {"URL": u}
                for f in fields:
                    row[f] = info[f]
                results.append(row)
                prog.progress(int(i/len(url_list)*100))
        st.success(f"Analizzati {len(url_list)} URL.")
        st.balloons()
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Download XLSX", data=buf, file_name="estrazione_seo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def run_placeholder():
    st.title("🛠️ Altro Tool")
    st.info("Contenuto placeholder.")

# Router
if selected == "seo":
    run_seo_extractor()
else:
    run_placeholder()
