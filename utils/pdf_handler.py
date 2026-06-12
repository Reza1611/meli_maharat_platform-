import fitz

def extract_text_from_pdfs(uploaded_files):
    full_text = ""
    file_names = []
    for uploaded_file in uploaded_files:
        file_names.append(uploaded_file.name)
        try:
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            for page in doc:
                full_text += page.get_text()
            doc.close()
        except Exception as e:
            full_text += f"\n[خطا در فایل {uploaded_file.name}]\n"
    return full_text, file_names
