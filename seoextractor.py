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

# CSS: nasconde label vuoti e colora la progress bar
st.markdown("""
    <style>
      label[data-testid="stWidgetLabel"] { display: none !important; }
      .stProgress > div > div > div { background-color: #f63366 !important; }
    </style>
""", unsafe_allow_html=True)

# Sidebar: logo + navigation (using st.navigation)
st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:20px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40"/>'
    '</div>',
    unsafe_allow_html=True
)

# Shared extraction logic
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

# Page functions
def seo_extractor():
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai **H1**, **H2**, **Meta title**, **Meta description**, **Canonical** e **Meta robots** rapidamente.")
    st.divider()
    col1, col2 = st.columns([2,1], gap="large")
    with col1:
        st.markdown("**Incolla le URL (una per riga):**")
        urls = st.text_area("", height=200, placeholder="https://esempio.com/pagina1\nhttps://esempio.com/pagina2", label_visibility="collapsed")
    with col2:
        st.markdown("**Campi da estrarre:**")
        fields = st.pills("", list(estrai_info("https://www.example.com").keys()), selection_mode="multi", default=[])

    if st.button("🚀 Avvia Estrazione"):
        if not fields:
            st.error("❗ Seleziona almeno un campo da estrarre.")
            return
        url_list = [u.strip() for u in urls.splitlines() if u.strip()]
        if not url_list:
            st.error("❗ Inserisci almeno un URL valido.")
            return
        prog = st.progress(0)
        results = []
        with st.spinner("Analisi in corso…"):
            for i, u in enumerate(url_list, 1):
                info = estrai_info(u)
                row = {"URL": u}
                for f in fields:
                    row[f] = info[f]
                results.append(row)
                prog.progress(int(i/len(url_list)*100))
        st.success(f"✅ Ho analizzato {len(url_list)} URL.")
        st.balloons()
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        buf = BytesIO()
        df.to_excel(buf, index=False, engine="openpyxl")
        buf.seek(0)
        st.download_button("📥 Download XLSX", data=buf, file_name="estrazione_seo.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def placeholder_tool():
    st.title("🛠️ Altro Tool")
    st.info("Contenuto del tool placeholder.")

# Build navigation structure
pages = {
    "On-Page SEO": [
        st.Page(seo_extractor, title="SEO Extractor"),
        st.Page(placeholder_tool, title="Altro Tool")
    ],
    "Technical SEO": [
        st.Page(placeholder_tool, title="Tool A"),
        st.Page(placeholder_tool, title="Tool B")
    ],
    "Off-Page SEO": [
        st.Page(placeholder_tool, title="Tool C"),
        st.Page(placeholder_tool, title="Tool D")
    ],
}

# Run navigation
selected = st.navigation(pages, position="sidebar", expanded=True)
selected.run()
