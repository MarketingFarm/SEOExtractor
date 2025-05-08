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
      .stProgress > div > div > div {
        background-color: #f63366 !important;
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

    h1 = soup.find("h1")
    h2_texts = [h.get_text(strip=True) for h in soup.find_all("h2")]
    title = soup.title
    meta_desc = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", rel="canonical")
    meta_robots = soup.find("meta", attrs={"name": "robots"})

    return {
        "H1": h1.get_text(strip=True) if h1 else "",
        "H2": " | ".join(h2_texts) if h2_texts else "",
        "Meta title": title.get_text(strip=True) if title else "",
        "Meta title length": len(title.get_text(strip=True)) if title else 0,
        "Meta description": meta_desc["content"].strip() if meta_desc and meta_desc.has_attr("content") else "",
        "Meta description length": len(meta_desc["content"].strip()) if meta_desc and meta_desc.has_attr("content") else 0,
        "Canonical": canonical["href"].strip() if canonical and canonical.has_attr("href") else "",
        "Meta robots": meta_robots["content"].strip() if meta_robots and meta_robots.has_attr("content") else ""
    }

if app_mode == "🔍 SEO Extractor":
    st.title("🔍 SEO Extractor")
    st.markdown(
        "> Estrai **H1**, **H2**, **Meta title** (e lunghezza), **Meta description** (e lunghezza), **Canonical** e **Meta robots**"
    )
    st.divider()

    col1, col2 = st.columns([2, 1], gap="large")
    with col1:
        st.markdown("**Incolla le URL (una per riga):**")
        urls_text = st.text_area(
            "",
            height=200,
            placeholder="https://esempio.com/pagina1\nhttps://esempio.com/pagina2",
            label_visibility="collapsed"
        )
    with col2:
        st.markdown("**Campi da estrarre:**")
        fields = st.pills(
            "",
            ["H1", "H2", "Meta title", "Meta description", "Canonical", "Meta robots"],
            selection_mode="multi",
            default=[]
        )

    st.markdown("")  # spazio
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
                        pct = int(i / len(urls) * 100)
                        progress.progress(pct)
                st.success(f"✅ Ho analizzato {len(urls)} URL.")
                st.balloons()

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
                    use_container_width=False
                )

elif app_mode == "🛠️ Altro Tool":
    st.title("🛠️ Altro Tool")
    st.info("Qui comparirà il contenuto del tuo secondo strumento.")
