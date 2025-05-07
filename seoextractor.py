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

# --- Sidebar ---
# Logo cliccabile
st.sidebar.markdown(
    '[<img src="https://i.ibb.co/0yMG6kDs/logo.png" alt="logo" border="0">](https://imgbb.com/)',
    unsafe_allow_html=True
)

st.sidebar.title("Menu")
app_mode = st.sidebar.radio(
    "Seleziona lo strumento:",
    ["SEO Extractor", "Altro Tool"]
)

# --- Funzione di estrazione ---
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

# --- SEO Extractor UI ---
if app_mode == "SEO Extractor":
    st.title("🔍 SEO Extractor")
    st.markdown(
        "Incolla una lista di URL (uno per riga) nel box qui sotto, "
        "seleziona i campi da estrarre e clicca **Avvia Estrazione**."
    )

    urls_text = st.text_area("URL (uno per riga)", height=200)
    cols_h1    = st.checkbox("H1", value=True)
    cols_title = st.checkbox("Title", value=True)
    cols_desc  = st.checkbox("Description", value=True)
    if st.button("🚀 Avvia Estrazione"):
        urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
        if not urls:
            st.error("Inserisci almeno un URL valido.")
        else:
            data = []
            progress_bar = st.progress(0)
            with st.spinner("Analisi in corso…"):
                for i, url in enumerate(urls, start=1):
                    info = estrai_info(url)
                    row = {"URL": url}
                    if cols_h1:    row["H1"]          = info["H1"]
                    if cols_title: row["Title"]       = info["Title"]
                    if cols_desc:  row["Description"] = info["Description"]
                    data.append(row)
                    progress_bar.progress(i / len(urls))
            st.success(f"Fatto! Ho analizzato {len(urls)} URL.")

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

# --- Placeholder per altri tool ---
elif app_mode == "Altro Tool":
    st.title("🛠️ Altro Tool")
    st.info("Qui comparirà la UI del tuo secondo strumento.")
    # ... aggiungi qui il codice per il secondo tool ...
