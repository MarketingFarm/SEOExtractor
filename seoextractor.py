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

# Sidebar: logo piccolo e menu a tendina
st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:10px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="60"/>'
    '</div>',
    unsafe_allow_html=True
)
app_mode = st.sidebar.selectbox(
    "", 
    ["🔍 SEO Extractor", "🛠️ Altro Tool"],
    index=0
)

BASE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/90.0.4430.93 Safari/537.36"
    )
}

def estrai_info(url: str):
    parsed = urlparse(url)
    segments = parsed.path.lstrip("/").split("/")
    lang_code = segments[0] if segments and "-" in segments[0] else ""
    headers = BASE_HEADERS.copy()
    if "-" in lang_code and len(lang_code) == 5:
        lang, region = lang_code.split("-")
        headers["Accept-Language"] = f"{lang}-{region.upper()},{lang};q=0.9"
    else:
        headers["Accept-Language"] = "en-US,en;q=0.9"
    session = requests.Session()
    session.headers.update(headers)
    if lang_code:
        try:
            session.get(f"{parsed.scheme}://{parsed.netloc}/{lang_code}/", timeout=5)
        except:
            pass
    resp = session.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    return {
        "H1": soup.find("h1").get_text(strip=True) if soup.find("h1") else "",
        "Title": soup.title.get_text(strip=True) if soup.title else "",
        "Description": (
            soup.find("meta", attrs={"name":"description"})["content"].strip()
            if soup.find("meta", attrs={"name":"description"}) and
               soup.find("meta", attrs={"name":"description"}).has_attr("content")
            else ""
        )
    }

if app_mode == "🔍 SEO Extractor":
    st.title("🔍 SEO Extractor")
    st.markdown("Incolla gli URL (uno per riga), scegli i campi e clicca **Avvia Estrazione**.")

    urls_text = st.text_area("", height=200)
    cb_h1    = st.checkbox("H1", value=True)
    cb_title = st.checkbox("Title", value=True)
    cb_desc  = st.checkbox("Description", value=True)
    if st.button("🚀 Avvia Estrazione"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.error("Inserisci almeno un URL valido.")
        else:
            data = []
            progress = st.progress(0)
            with st.spinner("Analisi in corso…"):
                for i, url in enumerate(urls, start=1):
                    info = estrai_info(url)
                    row = {"URL": url}
                    if cb_h1:    row["H1"]          = info["H1"]
                    if cb_title: row["Title"]       = info["Title"]
                    if cb_desc:  row["Description"] = info["Description"]
                    data.append(row)
                    progress.progress(i / len(urls))
            st.success(f"Fatto! {len(urls)} URL analizzati.")

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            towrite = BytesIO()
            df.to_excel(towrite, index=False, engine='openpyxl')
            towrite.seek(0)
            st.download_button(
                label="📥 Download XLSX",
                data=towrite,
                file_name="estrazione_seo.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

elif app_mode == "🛠️ Altro Tool":
    st.title("🛠️ Altro Tool")
    st.info("Qui il contenuto del tuo secondo strumento.")
