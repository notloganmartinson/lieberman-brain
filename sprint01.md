# SPRINT 1: Parsers and Semantic Chunking

We need a dedicated backend utility to handle file parsing and chunking deterministically. Do not touch `api.py` or the frontend yet.

## Tasks
Create a new file `backend/document_parser.py`.
1. **File Extractors:** Implement functions to extract raw text based on file extensions:
   - `extract_pdf(file_bytes)` using `pymupdf` (`fitz`).
   - `extract_docx(file_bytes)` using `docx.Document`.
   - `extract_csv(file_bytes)` using standard `csv` or `pandas` (convert rows to readable string formats).
   - `extract_txt(file_bytes)` using standard utf-8 decoding.
2. **Text Chunker:** Implement a `chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]` function. 
   - It should split the extracted text into manageable chunks, ensuring paragraphs aren't hard-cut without overlap.
3. **Main Entrypoint:** Implement `process_file(filename: str, file_bytes: bytes) -> List[str]` that routes to the correct extractor based on the extension and returns a list of text chunks. Raise a ValueError for unsupported formats.

Output only `backend/document_parser.py`.
