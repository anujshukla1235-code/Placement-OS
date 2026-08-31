import io
import logging

import pdfplumber
import PyPDF2

logger = logging.getLogger("ai_module")


def extract_text_from_pdf(file_obj):
    text = ""
    try:
        # file_obj can be FieldFile, UploadedFile, or path
        if hasattr(file_obj, "path"):
            path = file_obj.path
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            if text.strip():
                return text
        if hasattr(file_obj, "read"):
            file_obj.seek(0)
            data = file_obj.read()
            file_obj.seek(0)
            with pdfplumber.open(io.BytesIO(data)) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            if text.strip():
                return text
            # fallback PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(data))
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            return text
        else:
            with pdfplumber.open(file_obj) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or "") + "\n"
            return text
    except Exception as e:
        logger.warning("pdf_extract_failed", extra={"error": str(e)})
        return text or ""
    return text
