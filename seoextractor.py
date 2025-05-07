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

# Sidebar
st.sidebar.image("https://tuo-dominio.com/logo.png", use_column_width=True)
st.sidebar.markdown("## Impostazioni")
urls_input = st.sidebar.text_area("URL (uno per riga)", height=200)
cb_h1    = st.sidebar.checkbox("H1", value=True)
cb_title = st.sidebar.checkbox("Title", value=True)
cb_desc  = st.sidebar.checkbox("Description", value=True)
analizza = st.sidebar.button("🚀 Avvia Estrazione")

# Header
st.title("🔍 SEO Extractor")
st.markdown(
    """
    Estrai `<h1>`, `<title>` e meta description da una lista di pagine web.
    Seleziona i campi dalla sidebar, incolla gli URL e clicca **Avvia Estrazione**.
    """,
    unsafe_allow_html=True
)

if analizza:
    urls = [u.strip() for u in urls_input.splitlines() if u.strip()]
    if not urls:
        st.error("Inserisci almeno un URL valido nella sidebar.")
    else:
        data = []
        progress = st.progress(0)
        with st.spinner("Analisi in corso…"):
            for i, url in enumerate(urls):
                # (riutilizza qui la tua funzione estrai_info)
                info = estrai_info(url)
                row = {"URL": url}
                if cb_h1:    row["H1"]          = info["H1"]
                if cb_title: row["Title"]       = info["Title"]
                if cb_desc:  row["Description"] = info["Description"]
                data.append(row)
                progress.progress((i+1)/len(urls))
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
