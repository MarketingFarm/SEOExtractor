import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse

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

st.set_page_config(page_title="Estrattore H1/Title/Meta", layout="wide")
st.markdown("## Estrattore `<h1>`, `<title>` e `meta description`")
st.markdown("Incolla una lista di URL (uno per riga), seleziona i campi da estrarre e premi **Analizza**.")

# Input URL
urls_text = st.text_area("URL (uno per riga)", height=150)

# Selezione campi
col1, col2, col3 = st.columns(3)
with col1:
    cb_h1 = st.checkbox("H1", value=True)
with col2:
    cb_title = st.checkbox("Title", value=True)
with col3:
    cb_desc = st.checkbox("Description", value=True)

# Bottone di avvio
if st.button("Analizza"):
    urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
    if not urls:
        st.error("Inserisci almeno un URL valido.")
    else:
        data = []
        progress_bar = st.progress(0)
        for i, url in enumerate(urls, start=1):
            info = {"URL": url}
            try:
                fetched = estrai_info(url)
                if cb_h1: info["H1"] = fetched["H1"]
                if cb_title: info["Title"] = fetched["Title"]
                if cb_desc: info["Description"] = fetched["Description"]
            except Exception as e:
                info["H1"] = info.get("H1", "") or f"Errore: {e}"
                if cb_title: info["Title"] = ""
                if cb_desc: info["Description"] = ""
            data.append(info)
            progress_bar.progress(i / len(urls))

        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # Pulsante per download XLSX
        towrite = BytesIO()
        df.to_excel(towrite, index=False, engine='openpyxl')
        towrite.seek(0)
        st.download_button(
            label="Download XLSX",
            data=towrite,
            file_name="estrazione.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
