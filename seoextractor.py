# all’inizio del file, subito dopo set_page_config:
if "fields" not in st.session_state:
    st.session_state.fields = {"H1": True, "Meta title": True, "Meta description": True}

def toggle(field):
    st.session_state.fields[field] = not st.session_state.fields[field]

# …

if app_mode == "🔍 SEO Extractor":
    st.title("🔍 SEO Extractor")

    urls_text = st.text_area("URL (uno per riga)", height=200)
    st.markdown("**Seleziona i campi da estrarre**")
    btn_cols = st.columns(3)
    for i, field in enumerate(["H1", "Meta title", "Meta description"]):
        active = st.session_state.fields[field]
        style = "success" if active else "secondary"
        btn_cols[i].button(
            field,
            key=f"btn_{field}",
            on_click=toggle,
            args=(field,),
            button_style=style,
            use_container_width=True
        )

    if st.button("🚀 Avvia Estrazione"):
        selected = [f for f,v in st.session_state.fields.items() if v]
        if not selected:
            st.error("Seleziona almeno un campo da estrarre.")
        else:
            urls = [u.strip() for u in urls_text.splitlines() if u.strip()]
            if not urls:
                st.error("Inserisci almeno un URL valido.")
            else:
                data = []
                progress = st.progress(0)
                with st.spinner("Analisi in corso…"):
                    for i, url in enumerate(urls, start=1):
                        info = estrai_info(url)
                        row = {"URL": url}
                        for f in selected:
                            row[f] = info[f]
                        data.append(row)
                        progress.progress(i / len(urls))
                st.success(f"Fatto! {len(urls)} URL analizzati.")

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
