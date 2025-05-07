!pip install requests bs4 streamlit-toggle-switch openpyxl --quiet
import requests
from bs4 import BeautifulSoup
import streamlit as st
from streamlit_toggle_switch import toggle_switch
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse

st.set_page_config(
    page_title="Multi-Tool Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.markdown(
    '<div style="text-align:center; margin-bottom:10px;">'
    '<img src="https://i.ibb.co/0yMG6kDs/logo.png" width="40"/>'
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

def estrai_info(url):
    parsed = urlparse(url)
    lang_seg = parsed.path.lstrip("/").split("/")[0]
    headers = BASE_HEADERS.copy()
    if "-" in lang_seg and len(lang_seg)==5:
        l,r = lang_seg.split("-")
        headers["Accept-Language"] = f"{l}-{r.upper()},{l};q=0.9"
    else:
        headers["Accept-Language"] = "en-US,en;q=0.9"
    s = requests.Session(); s.headers.update(headers)
    if "-" in lang_seg:
        try: s.get(f"{parsed.scheme}://{parsed.netloc}/{lang_seg}/", timeout=5)
        except: pass
    r = s.get(url, timeout=10); r.raise_for_status()
    soup = BeautifulSoup(r.text,"html.parser")
    return {
        "H1": soup.find("h1").get_text(strip=True) if soup.find("h1") else "",
        "Meta title": soup.title.get_text(strip=True) if soup.title else "",
        "Meta description": (soup.find("meta",{"name":"description"})["content"].strip()
                             if soup.find("meta",{"name":"description"}) and soup.find("meta",{"name":"description"}).has_attr("content") else "")
    }

if app_mode=="🔍 SEO Extractor":
    st.title("🔍 SEO Extractor")
    urls = st.text_area("URL (uno per riga)", height=200)
    st.markdown("### Seleziona campi da estrarre:")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        sel_h1 = toggle_switch("H1", key="t1", default=True)
    with col2:
        sel_title = toggle_switch("Meta title", key="t2", default=True)
    with col3:
        sel_desc = toggle_switch("Meta description", key="t3", default=True)

    if st.button("🚀 Avvia Estrazione"):
        list_urls = [u.strip() for u in urls.splitlines() if u.strip()]
        if not list_urls:
            st.error("Inserisci almeno un URL")
        else:
            data=[]; prog=st.progress(0)
            for i,u in enumerate(list_urls,1):
                info=estrai_info(u); row={"URL":u}
                if sel_h1: row["H1"]=info["H1"]
                if sel_title: row["Meta title"]=info["Meta title"]
                if sel_desc: row["Meta description"]=info["Meta description"]
                data.append(row); prog.progress(i/len(list_urls))
            df=pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)
            bio=BytesIO(); df.to_excel(bio,index=False,engine="openpyxl"); bio.seek(0)
            st.download_button("📥 Download XLSX", data=bio, file_name="estrazione.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
else:
    st.title("🛠️ Altro Tool")
    st.info("Qui comparirà il tuo secondo strumento.")
