import fitz


def extract_text(pdf_bytes: bytes) -> str:
    """
    Extract all text from a PDF and return it as a single string.
    """

    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        text = ""

        for page in doc:
            text += page.get_text()

    return text