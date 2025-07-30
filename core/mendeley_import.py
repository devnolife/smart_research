def import_bibtex(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()  # nanti bisa diolah lagi sebagai metadata
