import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse

st.set_page_config(
    page_title="SEO Extractor",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS per hide empty labels e color progress bar
st.markdown("""
<style>
  label[data-testid="stWidgetLabel"] { display: none !important; }
  .stProgress > div > div > div { background-color: #f63366 !important; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar con logo + navigazione manuale ---
st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:20px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40" />'
    '</div>',
    unsafe_allow_html=True
)

# Definizione menu raggruppato
sections = {
    "On-Page SEO": ["🔍 SEO Extractor", "🛠️ Altro Tool"],
    "Technical SEO": ["🛠️ Altro Tool", "🛠️ Altro Tool"],
    "Off-Page SEO": ["🛠️ Altro Tool", "🛠️ Altro Tool"],
}

section = st.sidebar.selectbox("Sezione", list(sections.keys()))
tool = st.sidebar.selectbox("Strumento", sections[section])

# Funzione di estrazione
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

# Pagine
def page_seo_extractor():
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai **H1**, **H2**, **Meta title**, **Meta description**, **Canonical** e **Meta robots**.")
    st.divider()

    col1, col2 = st.columns([2,1], gap="large")
    with col1:
        st.markdown("**Incolla le URL (una per riga):**")
        urls_text = st.text_area("", height=200, placeholder="https://esempio.com/p1\nhttps://esempio.com/p2", label_visibility="collapsed")
    with col2:
        st.markdown("**Campi da estrarre:**")
        fields = st.pills("", list(estrai_info("https://www.example.com").keys()), selection_mode="multi", default=[])

    if st.button("🚀 Avvia Estrazione"):
        if not fields:
            st.error("❗ Seleziona almeno un campo.")
            return
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.error("❗ Inserisci almeno un URL valido.")
            return

        results = []
        progress = st.progress(0)
        with st.spinner("Analisi in corso…"):
            for i, url in enumerate(urls, start=1):
                info = estrai_info(url)
                row = {"URL": url}
                for f in fields:
                    row[f] = info[f]
                results.append(row)
                progress.progress(int(i/len(urls)*100))

        st.success(f"✅ Analizzate {len(urls)} URL.")
        st.balloons()

        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Download XLSX", data=buf, file_name="estrazione_seo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def page_altro():
    st.title("🛠️ Altro Tool")
    st.info("Contenuto del tool.")

# Router manuale
if tool == "🔍 SEO Extractor":
    page_seo_extractor()
else:
    page_altro()
