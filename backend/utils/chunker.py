import re
from typing import List

def chunk_text(text: str, max_chunk_chars: int = 500) -> List[str]:
    # Naive paragraph/line-based chunking
    paragraphs = re.split(r'\n{2,}', text.strip())

    chunks = []
    current = ""

    for p in paragraphs:
        if len(current) + len(p) < max_chunk_chars:
            current += p + "\n\n"
        else:
            if current:
                chunks.append(current.strip())
            current = p + "\n\n"

    if current:
        chunks.append(current.strip())

    return chunks