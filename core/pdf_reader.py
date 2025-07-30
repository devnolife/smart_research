import fitz  # PyMuPDF

def extract_abstract_from_pdf(file_path):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
        if "abstract" in text.lower():
            break
    return text
