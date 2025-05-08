# File: seoextractor.py (o il nome del tuo file principale)
import streamlit as st

# 1. Configurazione della pagina (primo comando Streamlit)
try:
    st.set_page_config(page_title="Test Minimale App", layout="wide")
except Exception as e:
    st.error(f"Errore durante st.set_page_config: {e}")
    st.stop() # Interrompe l'esecuzione se set_page_config fallisce

# 2. Scrivi la versione di Streamlit per conferma
st.write(f"Streamlit Version in uso: {st.__version__}")

# 3. Definisci alcune semplici funzioni per le pagine
def pagina_principale():
    st.title("Pagina Principale")
    st.write("Benvenuto nella pagina principale di test!")
    st.success("La pagina principale è stata caricata.")

def pagina_impostazioni():
    st.title("Pagina Impostazioni")
    st.write("Questa è la pagina delle impostazioni, parte del gruppo 'Config'.")
    st.info("La pagina impostazioni è stata caricata.")

# 4. Test della sidebar e della navigazione
try:
    with st.sidebar:
        st.header("Sidebar Test")
        st.write("Contenuto della Sidebar.")

    # Test di st.navigation con st.Page e l'argomento 'group'
    pg = st.navigation([
        st.Page(pagina_principale, title="Home", icon="🏠"),
        st.Page(pagina_impostazioni, title="Impostazioni App", icon="⚙️", group="Configurazione")
    ])

    st.sidebar.info("Menu st.navigation creato con successo.") # Messaggio nella sidebar

except Exception as e:
    st.error(f"Errore durante la creazione di st.sidebar o st.navigation: {e}")
    st.exception(e) # Mostra il traceback completo nell'app
    st.stop()

# 5. Esegui la navigazione
try:
    pg.run()
    # Non mettere st.write dopo pg.run() nella pagina principale,
    # perché pg.run() sostituisce il contenuto della pagina.
    # Eventuali messaggi post-run dovrebbero essere nella sidebar o gestiti diversamente.
except Exception as e:
    st.error(f"Errore durante pg.run(): {e}")
    st.exception(e)
    st.stop()
