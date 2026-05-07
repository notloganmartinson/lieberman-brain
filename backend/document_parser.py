import os
import io
import csv
from typing import List

import fitz  # type: ignore # pymupdf
import docx  # type: ignore


def extract_pdf(file_bytes: bytes) -> str:
    """Extracts text from a PDF file."""
    text = ""
    with fitz.open(stream=file_bytes, filetype="pdf") as doc:
        for page in doc:
            text += page.get_text() + "\n"
    return text


def extract_docx(file_bytes: bytes) -> str:
    """Extracts text from a DOCX file."""
    document = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([paragraph.text for paragraph in document.paragraphs])


def extract_csv(file_bytes: bytes) -> str:
    """Extracts text from a CSV file."""
    text_content = file_bytes.decode("utf-8")
    reader = csv.reader(io.StringIO(text_content))
    return "\n".join([", ".join(row) for row in reader])


def extract_txt(file_bytes: bytes) -> str:
    """Extracts text from a TXT file."""
    return file_bytes.decode("utf-8")


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Splits text into chunks of `chunk_size` characters with `overlap` characters."""
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be greater than overlap.")
    
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


def process_file(filename: str, file_bytes: bytes) -> List[str]:
    """Routes to the correct extractor based on extension and returns text chunks."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext == ".pdf":
        text = extract_pdf(file_bytes)
    elif ext == ".docx":
        text = extract_docx(file_bytes)
    elif ext == ".csv":
        text = extract_csv(file_bytes)
    elif ext == ".txt":
        text = extract_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
        
    return chunk_text(text)
