
import re

def split_into_chunks(text: str) -> list[str]:
    """
    Basic chunking:
    Split text whenever there is an empty line.
    """

    chunks = re.split(
        r'(?=\d+\.\s)',
        text
    )

    # Remove empty chunks and extra spaces
    chunks = [
        chunk.strip()
        for chunk in chunks
        if chunk.strip()
    ]

    return chunks