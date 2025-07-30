import streamlit as st
from core.scholar_scraper import scrape_google_scholar_headless
from core.topic_generator import generate_research_topics
from core.pdf_reader import extract_abstract_from_pdf
import json
import os

st.set_page_config(page_title="Smart Research Assistant")

st.title("📚 Smart Research Assistant")
st.write("Masukkan kata kunci pencarian untuk menemukan dan menganalisis jurnal terbaru.")

query = st.text_input("🔍 Kata Kunci Pencarian", value="Artificial Intelligence in Education")

if st.button("Cari Jurnal"):
    with st.spinner("Sedang mencari jurnal..."):
        results = scrape_google_scholar_headless(query)
        st.session_state["results"] = results

# Jika hasil ada
if "results" in st.session_state:
    st.subheader("📄 Hasil Pencarian")
    selections = []
    for i, r in enumerate(st.session_state["results"], 1):
        if st.checkbox(f"{r['title']}", key=i):
            selections.append(r)

    if selections:
        st.markdown("---")
        if st.button("🔬 Analisis Topik"):
            with st.spinner("Memproses dan menganalisis..."):
                topics = generate_research_topics(selections)
                st.subheader("💡 Rekomendasi Topik Penelitian")
                for t in topics:
                    st.write(f"- {t}")

                with open("outputs/selected_articles.json", "w", encoding="utf-8") as f:
                    json.dump(selections, f, ensure_ascii=False, indent=2)
                with open("outputs/topic_suggestions.txt", "w", encoding="utf-8") as f:
                    f.write("\n".join(topics))

# Upload PDF
st.markdown("---")
st.subheader("📤 Upload PDF Jurnal")
uploaded_pdf = st.file_uploader("Pilih file PDF", type=["pdf"])
if uploaded_pdf:
    temp_path = os.path.join("outputs", uploaded_pdf.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_pdf.getbuffer())

    abstrak_text = extract_abstract_from_pdf(temp_path)
    st.text_area("📑 Abstrak yang Terdeteksi", abstrak_text, height=200)
