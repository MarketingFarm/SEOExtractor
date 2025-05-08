import streamlit as st
st.write(f"STREAMLIT VERSION IN USE: {st.__version__}") # RIGA DI DEBUG
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
        margin-top: 10px;
    }
    .sidebar-logo img {
        width: 60px;
    }
    /* Rimuove padding eccessivo dalla sidebar se necessario */
    [data-testid="stSidebarNav"] {
        padding-top: 0rem; /* Riduci padding in cima al menu di navigazione */
    }
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
    """Estrae informazioni SEO da un URL."""
    data = {
        "URL": url, "H1": "N/D", "H2": "N/D", "Meta title": "N/D",
        "Meta title length": 0, "Meta description": "N/D",
        "Meta description length": 0, "Canonical": "N/D", "Meta robots": "N/D"
    }
    try:
        current_url_to_process = url # Manteniamo l'URL originale per il dizionario
        if not url.startswith("http://") and not url.startswith("https://"):
            # Tentativo di default con https per URL senza schema
            url_to_request = "https://" + url
        else:
            url_to_request = url

        resp = requests.get(url_to_request, headers=BASE_HEADERS, timeout=15, allow_redirects=True)
        resp.raise_for_status() # Solleva un'eccezione per codici di stato HTTP errati
        
        # Aggiorna l'URL nel dizionario se c'è stato un redirect
        if resp.url != url_to_request:
            data["URL"] = resp.url # URL effettivo dopo i redirect
        else:
            data["URL"] = current_url_to_process # URL originale fornito se non ci sono redirect evidenti

        soup = BeautifulSoup(resp.content, "html.parser")

        h1_tag = soup.find("h1")
        h2_tags = soup.find_all("h2")
        title_tag = soup.title
        description_tag = soup.find("meta", attrs={"name": "description"})
        canonical_tag = soup.find("link", rel="canonical")
        robots_tag = soup.find("meta", attrs={"name": "robots"})

        if h1_tag: data["H1"] = h1_tag.get_text(strip=True)
        if h2_tags:
            h2_texts = [h.get_text(strip=True) for h in h2_tags if h.get_text(strip=True)]
            if h2_texts: data["H2"] = " | ".join(h2_texts)
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
        # Questo errore dovrebbe essere gestito dalla logica di aggiunta schema, ma lo teniamo per sicurezza
        st.warning(f"URL non valido (schema http/https mancante): {current_url_to_process}")
        for key in data:
            if key != "URL": data[key] = "Errore Schema URL"
        data["URL"] = current_url_to_process
        return data
    except requests.exceptions.RequestException as e:
        st.warning(f"Errore nel recuperare {current_url_to_process}: {e}")
        for key in data:
            if key != "URL": data[key] = "Errore Richiesta"
        data["URL"] = current_url_to_process
        return data
    except Exception as e:
        st.warning(f"Errore generico nell'analisi di {current_url_to_process}: {e}")
        for key in data:
            if key != "URL": data[key] = "Errore Analisi"
        data["URL"] = current_url_to_process
        return data


def pagina_seo_extractor():
    """Pagina per il tool SEO Extractor."""
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai H1, H2, Meta title/length, Meta description/length, Canonical e Meta robots da una lista di URL.")
    st.divider()

    col1_input, col2_options = st.columns([0.65, 0.35], gap="large")

    with col1_input:
        urls_input_str = st.text_area(
            "Incolla gli URL (uno per riga)",
            height=280,
            placeholder="esempio.com/pagina1\nwww.altroesempio.it/articolo\nmiosito.org/contatti",
            label_visibility="collapsed"
        )
        st.caption("Puoi incollare URL con o senza `http://` o `https://`.")


    campi_disponibili = [
        "H1", "H2", "Meta title", "Meta title length",
        "Meta description", "Meta description length", "Canonical", "Meta robots"
    ]
    default_fields = [
        "URL", "H1", "Meta title", "Meta description", "Canonical" # Aggiunto URL ai default
    ]

    with col2_options:
        st.subheader("Campi da Estrarre")
        # Assicurati che 'URL' sia sempre una opzione e selezionato di default, ma non mostrato come opzione deselezionabile
        # per l'utente se lo vogliamo sempre presente. Per ora lo lascio come opzione standard.
        campi_selezionati_utente = st.multiselect(
            "Seleziona i campi:",
            options=["URL"] + campi_disponibili, # 'URL' è il primo, gli altri seguono
            default=default_fields,
            label_visibility="collapsed"
        )
        st.caption("Seleziona i dati SEO che desideri visualizzare nella tabella. 'URL' si riferisce all'URL finale dopo eventuali redirect.")


    if st.button("🚀 Avvia Estrazione", type="primary", use_container_width=True):
        urls_raw = [u.strip() for u in urls_input_str.splitlines() if u.strip()]
        
        if not urls_raw:
            st.error("Inserisci almeno un URL.")
            return
        if not campi_selezionati_utente: # Anche se URL è di default, l'utente potrebbe deselezionare tutto
            st.error("Seleziona almeno un campo da estrarre.")
            return

        progress_bar = st.progress(0, text="Inizializzazione analisi...")
        results_list = []
        total_urls = len(urls_raw)
        status_placeholder = st.empty()

        for i, url_originale in enumerate(urls_raw):
            percent_complete = (i + 1) / total_urls
            status_placeholder.text(f"Analizzando: {url_originale} ({i+1}/{total_urls})")
            progress_bar.progress(percent_complete, text=f"Analisi in corso... {int(percent_complete*100)}%")
            
            info_seo = estrai_info_seo(url_originale) # La funzione estrai_info_seo ora gestisce l'URL
            
            # Costruisci la riga dei risultati basandoti sui campi selezionati dall'utente
            riga_risultati = {}
            for campo in campi_selezionati_utente:
                riga_risultati[campo] = info_seo.get(campo, "N/D") # Usa .get per sicurezza se un campo non fosse in info_seo
            results_list.append(riga_risultati)

        status_placeholder.empty()
        progress_bar.empty()

        if results_list:
            st.success(f"Estrazione completata per {len(results_list)} URL.")
            # Non mostrare palloncini se ci sono stati warning durante l'estrazione
            # Questo richiede di tracciare i warning, per ora li lascio
            st.balloons()

            df = pd.DataFrame(results_list)
            
            # Assicura che le colonne siano nell'ordine selezionato dall'utente
            # e che 'URL' (o il campo URL effettivo) sia il primo se selezionato.
            colonne_ordinate = [c for c in campi_selezionati_utente if c in df.columns]
            df_display = df[colonne_ordinate]


            st.dataframe(df_display, use_container_width=True, hide_index=True)

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_display.to_excel(writer, index=False, sheet_name='Estrazione SEO')
            excel_data = output.getvalue()

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
    st.subheader(f"Sezione: {group_name}") # Mostra il nome del gruppo per contesto
    st.info(f"Questa è una pagina placeholder per il tool: **{tool_name}**.")
    st.write("Il contenuto specifico per questo tool verrà implementato qui.")
    st.image("https://via.placeholder.com/800x300.png?text=Contenuto+del+Tool+in+Arrivo",
             caption=f"Immagine placeholder per {tool_name}")

# --- Sidebar e Navigazione ---
# NOTA IMPORTANTE: La seguente sezione st.navigation con l'argomento 'group'
# richiede Streamlit versione 1.33.0 o successiva.
# Se riscontri l'errore "TypeError: Page() got an unexpected keyword argument 'group'",
# assicurati che il tuo file 'requirements.txt' specifichi una versione adeguata
# (es. streamlit==1.36.0) e che Streamlit Cloud stia usando quella versione.
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">'
        '<img src="https://i.ibb.co/0yMG6kDs/logo.png" alt="Logo"/>'
        '</div>',
        unsafe_allow_html=True
    )

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
