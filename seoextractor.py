import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
# from urllib.parse import urlparse # Non usata, ma la lascio se prevista per usi futuri

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
    /* Colora la progress bar */
    .stProgress > div > div > div { background-color: #f63366 !important; }

    /* Stile per il logo nella sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
        margin-top: 10px; /* Aggiunto spazio sopra il logo */
    }
    .sidebar-logo img {
        width: 60px; /* Leggermente aggiustata la dimensione */
    }
    /* Rimuove padding eccessivo dalla sidebar se necessario */
    [data-testid="stSidebarNav"] {
        padding-top: 0rem; /* Riduci padding in cima al menu di navigazione */
    }
    [data-testid="stSidebarUserContent"] {
        padding-top: 1rem; /* Riduci padding sopra il logo se è dentro user content */
    }
</style>
""", unsafe_allow_html=True)

# --- Funzioni dei Tool ---
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7", # Aggiunto per preferire contenuti in italiano
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Connection": "keep-alive"
}

def estrai_info_seo(url):
    """Estrae informazioni SEO da un URL."""
    data = {
        "URL": url, "H1": "N/D", "H2": "N/D", "Meta title": "N/D",
        "Meta title length": 0, "Meta description": "N/D",
        "Meta description length": 0, "Canonical": "N/D", "Meta robots": "N/D"
    }
    try:
        # Aggiungi http:// se manca per richieste semplici, ma idealmente l'URL dovrebbe essere completo
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "http://" + url # Tentativo basico, potrebbe non essere sempre corretto per https
            data["URL"] = url # Aggiorna l'URL se modificato

        resp = requests.get(url, headers=BASE_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        h1_tag = soup.find("h1")
        h2_tags = soup.find_all("h2")
        title_tag = soup.title
        description_tag = soup.find("meta", attrs={"name": "description"})
        canonical_tag = soup.find("link", rel="canonical")
        robots_tag = soup.find("meta", attrs={"name": "robots"})

        if h1_tag: data["H1"] = h1_tag.get_text(strip=True)
        if h2_tags: data["H2"] = " | ".join([h.get_text(strip=True) for h in h2_tags if h.get_text(strip=True)])
        if title_tag:
            data["Meta title"] = title_tag.get_text(strip=True)
            data["Meta title length"] = len(data["Meta title"])
        if description_tag and description_tag.has_attr("content"):
            data["Meta description"] = description_tag["content"].strip()
            data["Meta description length"] = len(data["Meta description"])
        if canonical_tag and canonical_tag.has_attr("href"): data["Canonical"] = canonical_tag["href"].strip()
        if robots_tag and robots_tag.has_attr("content"): data["Meta robots"] = robots_tag["content"].strip()

        return data

    except requests.exceptions.MissingSchema:
        st.warning(f"URL non valido (schema mancante http/https): {url}")
        for key in data:
            if key != "URL": data[key] = "Errore Schema URL"
        return data
    except requests.exceptions.RequestException as e:
        st.warning(f"Errore nel recuperare {url}: {e}")
        for key in data:
            if key != "URL": data[key] = "Errore Richiesta"
        return data
    except Exception as e:
        st.warning(f"Errore generico nell'analisi di {url}: {e}")
        for key in data:
            if key != "URL": data[key] = "Errore Analisi"
        return data


def pagina_seo_extractor():
    """Pagina per il tool SEO Extractor."""
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai H1, H2, Meta title/length, Meta description/length, Canonical e Meta robots da una lista di URL.")
    st.divider()

    col1_input, col2_options = st.columns([0.65, 0.35], gap="large")

    with col1_input:
        urls_input = st.text_area(
            "Incolla gli URL (uno per riga)",
            height=280, # Aumentata altezza
            placeholder="https://esempio.com/pagina1\nhttps://www.altroesempio.it/articolo\nhttp://miosito.org/contatti",
            label_visibility="collapsed"
        )

    campi_disponibili = [
        "H1", "H2", "Meta title", "Meta title length",
        "Meta description", "Meta description length", "Canonical", "Meta robots"
    ]
    default_fields = [
        "H1", "Meta title", "Meta description", "Canonical"
    ]

    with col2_options:
        st.subheader("Campi da Estrarre")
        campi_selezionati = st.multiselect(
            "Seleziona i campi:",
            options=campi_disponibili,
            default=default_fields,
            label_visibility="collapsed"
        )
        st.caption("Seleziona i dati SEO che desideri visualizzare nella tabella.")

    if st.button("🚀 Avvia Estrazione", type="primary", use_container_width=True):
        urls_raw = [u.strip() for u in urls_input.splitlines() if u.strip()]
        
        urls_validi = []
        for u_raw in urls_raw:
            if not (u_raw.startswith("http://") or u_raw.startswith("https://")):
                # Tenta di aggiungere https:// di default se lo schema manca,
                # ma avvisa l'utente o gestisci in modo più sofisticato se necessario
                urls_validi.append("https://" + u_raw)
            else:
                urls_validi.append(u_raw)

        if not urls_validi:
            st.error("Inserisci almeno un URL valido.")
            return
        if not campi_selezionati:
            st.error("Seleziona almeno un campo da estrarre.")
            return

        progress_bar = st.progress(0, text="Inizializzazione analisi...")
        results_list = []
        total_urls = len(urls_validi)
        status_placeholder = st.empty()

        for i, url in enumerate(urls_validi):
            percent_complete = (i + 1) / total_urls
            status_placeholder.text(f"Analizzando: {url} ({i+1}/{total_urls})")
            progress_bar.progress(percent_complete, text=f"Analisi in corso... {int(percent_complete*100)}%")
            
            info = estrai_info_seo(url)
            riga_risultati = {"URL Originale": url} # Manteniamo l'URL processato
            for campo in campi_selezionati:
                riga_risultati[campo] = info.get(campo, "N/D")
            results_list.append(riga_risultati)

        status_placeholder.empty()
        progress_bar.empty()

        if results_list:
            st.success(f"Estrazione completata per {len(results_list)} URL.")
            st.balloons()

            df = pd.DataFrame(results_list)
            colonne_ordinate = ["URL Originale"] + [c for c in campi_selezionati if c in df.columns]
            df_display = df[colonne_ordinate]

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            output = BytesIO()
            # Usare 'with' assicura che lo writer sia chiuso correttamente
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Estrazione SEO')
            excel_data = output.getvalue() # .getvalue() è corretto per BytesIO

            st.download_button(
                label="📥 Download Report (XLSX)",
                data=excel_data,
                file_name=f"estrazione_seo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.warning("Nessun dato è stato estratto. Controlla gli URL o i messaggi di avviso sopra.")

def pagina_placeholder(tool_name="Tool Placeholder", icon="🛠️", group_name="N/D"):
    """Pagina placeholder generica per altri tool."""
    st.title(f"{icon} {tool_name}")
    st.subheader(f"Sezione: {group_name}")
    st.info(f"Questa è una pagina placeholder per il tool: **{tool_name}**.")
    st.write("Il contenuto specifico per questo tool verrà implementato qui.")
    st.image("https://via.placeholder.com/800x300.png?text=Contenuto+del+Tool+in+Arrivo",
             caption=f"Immagine placeholder per {tool_name}")

# --- Sidebar e Navigazione ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">'
        '<img src="https://i.ibb.co/0yMG6kDs/logo.png" alt="Logo"/>' # Assicurati che questo URL sia valido e accessibile
        '</div>',
        unsafe_allow_html=True
    )
    # st.markdown("### Navigazione Principale") # L'header del gruppo fa già da titolo

    pg = st.navigation(
        [
            st.Page(pagina_seo_extractor, title="SEO Extractor", icon="🔍", group="On-Page SEO"),
            st.Page(lambda: pagina_placeholder("Struttura Dati", icon="📝", group_name="On-Page SEO"), title="Struttura Dati", icon="📝", group="On-Page SEO"),
            st.Page(lambda: pagina_placeholder("Analisi Contenuto", icon="📰", group_name="On-Page SEO"), title="Analisi Contenuto", icon="📰", group="On-Page SEO"),

            st.Page(lambda: pagina_placeholder("Verifica Robots.txt", icon="🤖", group_name="Technical SEO"), title="Verifica Robots.txt", icon="🤖", group="Technical SEO"),
            st.Page(lambda: pagina_placeholder("Analisi Sitemap", icon="🗺️", group_name="Technical SEO"), title="Analisi Sitemap", icon="🗺️", group="Technical SEO"),
            st.Page(lambda: pagina_placeholder("Controllo Redirect", icon="↪️", group_name="Technical SEO"), title="Controllo Redirect", icon="↪️", group="Technical SEO"),


            st.Page(lambda: pagina_placeholder("Analisi Backlink", icon="🔄", group_name="Off-Page SEO"), title="Analisi Backlink", icon="🔄", group="Off-Page SEO"),
            st.Page(lambda: pagina_placeholder("Ricerca Menzioni", icon="🗣️", group_name="Off-Page SEO"), title="Ricerca Menzioni", icon="🗣️", group="Off-Page SEO"),
        ]
    )

# --- Esegui la Pagina Selezionata ---
pg.run()
