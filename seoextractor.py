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

# Sidebar: small logo + app selector
st.sidebar.markdown(
    '<div style="text-align:center; margin:10px 0;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40">'
    '</div>',
    unsafe_allow_html=True
)
app_mode = st.sidebar.selectbox("", ["🔍 SEO Extractor", "🛠️ Altro Tool"])

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
        "Meta title": soup.title.get_text(strip=True) if soup.title else "",
        "Meta description": (
            soup.find("meta", attrs={"name":"description"})["content"].strip()
            if soup.find("meta", attrs={"name":"description"}) and
               soup.find("meta", attrs={"name":"description"}).has_attr("content")
            else ""
        )
    }

if app_mode == "🔍 SEO Extractor":
    st.title("🔍 SEO Extractor")
    st.markdown("Questo tool estrae H1, Meta title e Meta description dalle pagine web che indichi.")

    # Two columns: left 2/3, right 1/3
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Incolla le URL (una per riga) e seleziona i campi da estrarre:**")
        urls_text = st.text_area(
            "",
            height=200,
            placeholder="https://esempio.com/pagina1\nhttps://esempio.com/pagina2"
        )
    with col2:
        st.markdown("**Campi da estrarre**")
        fields = st.pills(
            "",
            ["H1", "Meta title", "Meta description"],
            selection_mode="multi",
            default=[]
        )

    # Extraction button below columns
    if st.button("🚀 Avvia Estrazione"):
        if not fields:
            st.error("❗ Seleziona almeno un campo da estrarre.")
        else:
            urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
            if not urls:
                st.error("❗ Inserisci almeno un URL valido.")
            else:
                results = []
                progress = st.progress(0)
                with st.spinner("Analisi in corso…"):
                    for i, url in enumerate(urls, start=1):
                        info = estrai_info(url)
                        row = {"URL": url}
                        for f in fields:
                            row[f] = info.get(f, "")
                        results.append(row)
                        progress.progress(i / len(urls))
                st.success(f"✅ Ho analizzato {len(urls)} URL.")

                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)

                buf = BytesIO()
                df.to_excel(buf, index=False, engine="openpyxl")
                buf.seek(0)
                st.download_button(
                    label="📥 Download XLSX",
                    data=buf,
                    file_name="estrazione_seo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

elif app_mode == "🛠️ Altro Tool":
    st.title("🛠️ Altro Tool")
    st.info("Qui comparirà il contenuto del tuo secondo strumento.")
