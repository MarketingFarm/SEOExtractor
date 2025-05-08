import streamlit as st
# RIGA DI DEBUG - RIMUOVERE UNA VOLTA RISOLTO IL PROBLEMA DI VERSIONE
st.write(f"STREAMLIT VERSION IN USE: {st.__version__}")

import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO

# --- Configurazione della Pagina ---
st.set_page_config(
    page_title="Multi-Tool Dashboard SEO",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Stili CSS Personalizzati ---
st.markdown("""
<style>
    .stProgress > div > div > div { background-color: #f63366 !important; }
    .sidebar-logo { text-align: center; margin-bottom: 20px; margin-top: 10px; }
    .sidebar-logo img { width: 60px; }
    [data-testid="stSidebarNav"] { padding-top: 0rem; }
</style>
""", unsafe_allow_html=True)

# --- Funzioni dei Tool ---
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
}

def estrai_info_seo(url):
    data = {
        "URL": url, "H1": "N/D", "H2": "N/D", "Meta title": "N/D",
        "Meta title length": 0, "Meta description": "N/D",
        "Meta description length": 0, "Canonical": "N/D", "Meta robots": "N/D"
    }
    try:
        current_url_to_process = url
        url_to_request = url
        if not url.startswith("http://") and not url.startswith("https://"):
            url_to_request = "https://" + url

        resp = requests.get(url_to_request, headers=BASE_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        
        data["URL"] = resp.url if resp.url != url_to_request else current_url_to_process
        soup = BeautifulSoup(resp.content, "html.parser")

        h1_tag = soup.find("h1")
        if h1_tag: data["H1"] = h1_tag.get_text(strip=True)
        
        h2_tags = soup.find_all("h2")
        if h2_tags:
            h2_texts = [h.get_text(strip=True) for h in h2_tags if h.get_text(strip=True)]
            if h2_texts: data["H2"] = " | ".join(h2_texts)
        
        title_tag = soup.title
        if title_tag:
            data["Meta title"] = title_tag.get_text(strip=True)
            data["Meta title length"] = len(data["Meta title"])
        
        description_tag = soup.find("meta", attrs={"name": "description"})
        if description_tag and description_tag.has_attr("content"):
            data["Meta description"] = description_tag["content"].strip()
            data["Meta description length"] = len(data["Meta description"])
        
        canonical_tag = soup.find("link", rel="canonical")
        if canonical_tag and canonical_tag.has_attr("href"): data["Canonical"] = canonical_tag["href"].strip()
        
        robots_tag = soup.find("meta", attrs={"name": "robots"})
        if robots_tag and robots_tag.has_attr("content"): data["Meta robots"] = robots_tag["content"].strip()
        return data

    except requests.exceptions.RequestException as e: # Cattura più errori di richiesta
        st.warning(f"Errore ({type(e).__name__}) nel recuperare {current_url_to_process}: {str(e)[:100]}") # Limita lunghezza errore
        for key in data:
            if key != "URL": data[key] = f"Errore Richiesta ({type(e).__name__})"
        data["URL"] = current_url_to_process
        return data
    except Exception as e:
        st.warning(f"Errore generico ({type(e).__name__}) nell'analisi di {current_url_to_process}: {str(e)[:100]}")
        for key in data:
            if key != "URL": data[key] = f"Errore Analisi ({type(e).__name__})"
        data["URL"] = current_url_to_process
        return data

def pagina_seo_extractor():
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai H1, H2, Meta title/length, Meta description/length, Canonical e Meta robots.")
    st.divider()

    col1_input, col2_options = st.columns([0.65, 0.35], gap="large")
    with col1_input:
        urls_input_str = st.text_area(
            "Incolla gli URL (uno per riga)", height=280,
            placeholder="esempio.com/pagina1\nwww.altroesempio.it/articolo",
            label_visibility="collapsed"
        )
        st.caption("Puoi incollare URL con o senza `http://` o `https://`.")

    campi_disponibili = [
        "H1", "H2", "Meta title", "Meta title length",
        "Meta description", "Meta description length", "Canonical", "Meta robots"
    ]
    default_fields = ["URL", "H1", "Meta title", "Meta description", "Canonical"]

    with col2_options:
        st.subheader("Campi da Estrarre")
        campi_selezionati_utente = st.multiselect(
            "Seleziona i campi:", options=["URL"] + campi_disponibili,
            default=default_fields, label_visibility="collapsed"
        )
        st.caption("Seleziona i dati SEO da visualizzare. 'URL' è l'URL finale post-redirect.")

    if st.button("🚀 Avvia Estrazione", type="primary", use_container_width=True):
        urls_raw = [u.strip() for u in urls_input_str.splitlines() if u.strip()]
        if not urls_raw:
            st.error("Inserisci almeno un URL."); return
        if not campi_selezionati_utente:
            st.error("Seleziona almeno un campo da estrarre."); return

        progress_bar = st.progress(0, text="Inizializzazione...")
        results_list = []
        total_urls = len(urls_raw)
        status_placeholder = st.empty()

        for i, url_originale in enumerate(urls_raw):
            percent_complete = (i + 1) / total_urls
            status_placeholder.text(f"Analizzando: {url_originale} ({i+1}/{total_urls})")
            progress_bar.progress(percent_complete, text=f"Analisi... {int(percent_complete*100)}%")
            
            info_seo = estrai_info_seo(url_originale)
            riga_risultati = {campo: info_seo.get(campo, "N/D") for campo in campi_selezionati_utente}
            results_list.append(riga_risultati)

        status_placeholder.empty(); progress_bar.empty()

        if results_list:
            st.success(f"Estrazione completata per {len(results_list)} URL.")
            st.balloons()
            df = pd.DataFrame(results_list)
            colonne_ordinate = [c for c in campi_selezionati_utente if c in df.columns]
            df_display = df[colonne_ordinate]
            st.dataframe(df_display, use_container_width=True, hide_index=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Estrazione SEO')
            st.download_button(
                label="📥 Download Report (XLSX)", data=output.getvalue(),
                file_name=f"estrazione_seo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("Nessun dato estratto. Controlla URL o messaggi di avviso.")

def pagina_placeholder(tool_name="Tool Placeholder", icon="🛠️", section_info="N/D"): # section_info invece di group_name
    st.title(f"{icon} {tool_name}")
    st.subheader(f"(Placeholder per la sezione: {section_info})") # Mostra info sezione
    st.info(f"Contenuto per **{tool_name}** da implementare.")
    st.image("https://via.placeholder.com/800x300.png?text=Contenuto+del+Tool", caption=f"Placeholder {tool_name}")

# --- Sidebar e Navigazione (SENZA 'group' per compatibilità) ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo"><img src="https://i.ibb.co/0yMG6kDs/logo.png" alt="Logo"/></div>',
        unsafe_allow_html=True
    )

    # Navigazione senza l'argomento 'group'
    pg = st.navigation(
        [
            st.Page(pagina_seo_extractor, title="SEO Extractor (On-Page)", icon="🔍"), # Aggiunto "(On-Page)" al titolo
            st.Page(lambda: pagina_placeholder("Struttura Dati", icon="📝", section_info="On-Page SEO"), title="Struttura Dati (On-Page)", icon="📝"),
            st.Page(lambda: pagina_placeholder("Analisi Contenuto", icon="📰", section_info="On-Page SEO"), title="Analisi Contenuto (On-Page)", icon="📰"),

            st.Page(lambda: pagina_placeholder("Verifica Robots.txt", icon="🤖", section_info="Technical SEO"), title="Verifica Robots.txt (Tech)", icon="🤖"),
            st.Page(lambda: pagina_placeholder("Analisi Sitemap", icon="🗺️", section_info="Technical SEO"), title="Analisi Sitemap (Tech)", icon="🗺️"),
            st.Page(lambda: pagina_placeholder("Controllo Redirect", icon="↪️", section_info="Technical SEO"), title="Controllo Redirect (Tech)", icon="↪️"),

            st.Page(lambda: pagina_placeholder("Analisi Backlink", icon="🔄", section_info="Off-Page SEO"), title="Analisi Backlink (Off-Page)", icon="🔄"),
            st.Page(lambda: pagina_placeholder("Ricerca Menzioni", icon="🗣️", section_info="Off-Page SEO"), title="Ricerca Menzioni (Off-Page)", icon="🗣️"),
        ]
    )

pg.run()
