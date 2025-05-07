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

# Nasconde label vuoti e definisce stile card
st.markdown("""
    <style>
      label[data-testid="stWidgetLabel"] { display: none !important; }
      .card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 16px;
        background: #fff;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        margin-bottom: 20px;
      }
    </style>
""", unsafe_allow_html=True)

# Sidebar con logo e menu
st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:20px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40" />'
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
    st.markdown("Estrai **H1**, **Meta title** e **Meta description** in modo rapido e intuitivo.")
    st.divider()

    # Card contenente URL e selezione campi
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown("**Incolla le URL (una per riga):**")
        urls_text = st.text_area(
            label="",
            height=200,
            placeholder="https://esempio.com/pagina1\nhttps://esempio.com/pagina2",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("**Campi da estrarre:**")
        fields = st.pills(
            "",
            ["H1", "Meta title", "Meta description"],
            selection_mode="multi",
            default=[]
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # Pulsante di estrazione sotto la card
    if st.button("🚀 Avvia Estrazione"):
        if not fields:
            st.error("❗ Seleziona almeno un campo da estrarre prima di procedere.")
        else:
            urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
            if not urls:
                st.error("❗ Inserisci almeno un URL valido.")
            else:
                data = []
                progress = st.progress(0)
                with st.spinner("Analisi in corso…"):
                    for i, url in enumerate(urls, start=1):
                        info = estrai_info(url)
                        row = {"URL": url}
                        for f in fields:
                            row[f] = info.get(f, "")
                        data.append(row)
                        progress.progress(i / len(urls))
                st.success(f"✅ Ho analizzato {len(urls)} URL.")
                st.balloons()

                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True)

                buf = BytesIO()
                df.to_excel(buf, index=False, engine="openpyxl")
                buf.seek(0)
                st.download_button(
                    label="📥 Download XLSX",
                    data=buf,
                    file_name="estrazione_seo.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=False
                )

elif app_mode == "🛠️ Altro Tool":
    st.title("🛠️ Altro Tool")
    st.info("Qui comparirà il contenuto del tuo secondo strumento.")
