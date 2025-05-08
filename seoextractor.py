import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import BytesIO
from urllib.parse import urlparse # Non usata nel codice fornito, ma la lascio se serve altrove

# --- Configurazione della Pagina ---
st.set_page_config(
    page_title="Multi-Tool Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Stili CSS Personalizzati ---
st.markdown("""
<style>
    /* Nascondi le label vuote dei widget se non necessarie */
    /* label[data-testid="stWidgetLabel"] { display: none !important; } */

    /* Colora la progress bar */
    .stProgress > div > div > div { background-color: #f63366 !important; }

    /* Stile per il logo nella sidebar */
    .sidebar-logo {
        text-align: center;
        margin-bottom: 20px;
    }
    .sidebar-logo img {
        width: 70px; /* Aumentato per migliore visibilità */
    }
</style>
""", unsafe_allow_html=True)

# --- Funzioni dei Tool ---
BASE_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"} # User agent più comune

def estrai_info_seo(url):
    """Estrae informazioni SEO da un URL."""
    try:
        resp = requests.get(url, headers=BASE_HEADERS, timeout=15) # Timeout aumentato
        resp.raise_for_status() # Solleva un'eccezione per codici di stato HTTP errati
        soup = BeautifulSoup(resp.content, "html.parser") # Usare resp.content per gestire correttamente encoding

        h1_tag = soup.find("h1")
        h2_tags = soup.find_all("h2")
        title_tag = soup.title
        description_tag = soup.find("meta", attrs={"name": "description"}) # attrs per chiarezza
        canonical_tag = soup.find("link", rel="canonical")
        robots_tag = soup.find("meta", attrs={"name": "robots"})

        h1_text = h1_tag.get_text(strip=True) if h1_tag else "N/D" # N/D se non trovato
        h2_texts = " | ".join([h.get_text(strip=True) for h in h2_tags]) if h2_tags else "N/D"
        meta_title_text = title_tag.get_text(strip=True) if title_tag else "N/D"
        meta_description_text = description_tag["content"].strip() if description_tag and description_tag.has_attr("content") else "N/D"
        canonical_url = canonical_tag["href"].strip() if canonical_tag and canonical_tag.has_attr("href") else "N/D"
        meta_robots_content = robots_tag["content"].strip() if robots_tag and robots_tag.has_attr("content") else "N/D"

        return {
            "URL": url, # Aggiunto URL alla riga per riferimento
            "H1": h1_text,
            "H2": h2_texts,
            "Meta title": meta_title_text,
            "Meta title length": len(meta_title_text) if meta_title_text != "N/D" else 0,
            "Meta description": meta_description_text,
            "Meta description length": len(meta_description_text) if meta_description_text != "N/D" else 0,
            "Canonical": canonical_url,
            "Meta robots": meta_robots_content
        }
    except requests.exceptions.RequestException as e:
        st.warning(f"Errore nel recuperare {url}: {e}")
        return {
            "URL": url,
            "H1": "Errore", "H2": "Errore", "Meta title": "Errore", "Meta title length": 0,
            "Meta description": "Errore", "Meta description length": 0, "Canonical": "Errore", "Meta robots": "Errore"
        }
    except Exception as e:
        st.warning(f"Errore generico nell'analisi di {url}: {e}")
        return {
            "URL": url,
            "H1": "Errore Analisi", "H2": "Errore Analisi", "Meta title": "Errore Analisi", "Meta title length": 0,
            "Meta description": "Errore Analisi", "Meta description length": 0, "Canonical": "Errore Analisi", "Meta robots": "Errore Analisi"
        }


def pagina_seo_extractor():
    """Pagina per il tool SEO Extractor."""
    st.title("🔍 SEO Extractor")
    st.markdown("Estrai H1, H2, Meta title/length, Meta description/length, Canonical e Meta robots da una lista di URL.")
    st.divider()

    col1, col2 = st.columns([0.7, 0.3], gap="large")

    with col1:
        urls_input = st.text_area(
            "Incolla gli URL (uno per riga)",
            height=250,
            placeholder="https://esempio.com/pagina1\nhttps://esempio.com/pagina2\nhttps://esempio.com/pagina3",
            label_visibility="collapsed" # Nasconde la label se il placeholder è sufficiente
        )

    # Definisci i campi possibili PRIMA, basandoti su una chiamata fittizia o una lista statica
    # Questo evita di chiamare example.com ogni volta che la pagina si ricarica
    campi_disponibili = [
        "H1", "H2", "Meta title", "Meta title length",
        "Meta description", "Meta description length", "Canonical", "Meta robots"
    ]
    default_fields = [
        "H1", "Meta title", "Meta description", "Canonical"
    ]

    with col2:
        st.subheader("Campi da Estrarre")
        campi_selezionati = st.multiselect(
            "Seleziona i campi:",
            options=campi_disponibili,
            default=default_fields,
            label_visibility="collapsed"
        )

    if st.button("🚀 Avvia Estrazione", type="primary", use_container_width=True):
        urls = [u.strip() for u in urls_input.splitlines() if u.strip() and (u.startswith("http://") or u.startswith("https://"))]

        if not urls:
            st.error("Inserisci almeno un URL valido (deve iniziare con http:// o https://).")
            return
        if not campi_selezionati:
            st.error("Seleziona almeno un campo da estrarre.")
            return

        progress_bar = st.progress(0, text="Analisi in corso...")
        results_list = []
        total_urls = len(urls)

        status_placeholder = st.empty() # Per mostrare l'URL corrente in analisi

        for i, url in enumerate(urls):
            status_placeholder.text(f"Analizzando: {url} ({i+1}/{total_urls})")
            info = estrai_info_seo(url)
            # Seleziona solo i campi richiesti, più l'URL per riferimento
            riga_risultati = {"URL": url}
            for campo in campi_selezionati:
                riga_risultati[campo] = info.get(campo, "N/D") # .get() per sicurezza
            results_list.append(riga_risultati)
            progress_bar.progress((i + 1) / total_urls, text=f"Analisi in corso... ({i+1}/{total_urls})")

        status_placeholder.empty() # Rimuove il testo dell'URL corrente
        progress_bar.empty() # Rimuove la progress bar dopo il completamento

        if results_list:
            st.success(f"Estrazione completata per {len(results_list)} URL.")
            st.balloons()

            df = pd.DataFrame(results_list)
            # Riordina le colonne per avere "URL" per primo, seguito dai campi selezionati
            colonne_ordinate = ["URL"] + [c for c in campi_selezionati if c in df.columns]
            df_display = df[colonne_ordinate]

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Download
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
            st.warning("Nessun dato è stato estratto. Controlla gli URL o i log di errore.")

def pagina_placeholder(tool_name="Tool Placeholder", icon="🛠️"):
    """Pagina placeholder generica per altri tool."""
    st.title(f"{icon} {tool_name}")
    st.info(f"Questa è una pagina placeholder per il tool: **{tool_name}**.")
    st.write("Il contenuto specifico per questo tool verrà implementato qui.")
    st.image("https://via.placeholder.com/800x300.png?text=Contenuto+del+Tool+in+Arrivo",
             caption=f"Immagine placeholder per {tool_name}")

# --- Sidebar e Navigazione ---
with st.sidebar:
    st.markdown(
        '<div class="sidebar-logo">'
        '<img src="https://i.ibb.co/0yMG6kDs/logo.png" alt="Logo"/>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("### Navigazione Principale")

    # Definisci le pagine per st.navigation
    # NOTA: st.navigation è disponibile da Streamlit 1.33+.
    # Se hai una versione precedente, questo approccio non funzionerà
    # e dovrai usare altri metodi come st.radio o st.selectbox per la navigazione.
    # Assicurati che il tuo Streamlit sia aggiornato: pip install --upgrade streamlit

    pg = st.navigation(
        [
            st.Page(pagina_seo_extractor, title="SEO Extractor", icon="🔍", group="On-Page SEO"),
            st.Page(lambda: pagina_placeholder("Struttura Dati & Schema"), title="Struttura Dati & Schema", icon="📝", group="On-Page SEO"),
            st.Page(lambda: pagina_placeholder("Analisi Contenuto"), title="Analisi Contenuto", icon="📰", group="On-Page SEO"),

            st.Page(lambda: pagina_placeholder("Verifica Robots.txt"), title="Verifica Robots.txt", icon="🤖", group="Technical SEO"),
            st.Page(lambda: pagina_placeholder("Analisi Sitemap"), title="Analisi Sitemap", icon="🗺️", group="Technical SEO"),
            st.Page(lambda: pagina_placeholder("Controllo Link Rotti"), title="Controllo Link Rotti", icon="🔗", group="Technical SEO"),

            st.Page(lambda: pagina_placeholder("Analisi Backlink"), title="Analisi Backlink", icon="🔄", group="Off-Page SEO"),
            st.Page(lambda: pagina_placeholder("Ricerca Menzioni"), title="Ricerca Menzioni", icon="🗣️", group="Off-Page SEO"),
        ]
    )

# --- Esegui la Pagina Selezionata ---
pg.run()
