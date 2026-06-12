import fitz

def extract_text_from_pdfs(uploaded_files):
    full_text = ""
    file_names = []

    for uploaded_file in uploaded_files:
        file_names.append(uploaded_file.name)
        try:
            # استفاده از getvalue برای پایداری بیشتر در سرور
            pdf_bytes = uploaded_file.getvalue() 
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")

            for page in doc:
                text = page.get_text()
                if text:
                    full_text += text
            doc.close()
        except Exception as e:
            full_text += f"\n[خطا: {str(e)}]\n"

    return full_text.strip(), file_names
