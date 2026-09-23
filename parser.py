"""
Resume & Job Description Document Parser Module.

This module provides utilities to extract raw text from various document formats
(PDF, DOCX, and plain text) uploaded through the Streamlit file uploader interface
or passed as standard file-like streams.
"""

import io
from typing import Optional, Union
import docx
import pdfplumber
from streamlit.runtime.uploaded_file_manager import UploadedFile


def extract_text(uploaded_file: Optional[Union[UploadedFile, io.BytesIO, str]]) -> str:
    """
    Extract raw text from an uploaded file (PDF, DOCX, or TXT).

    Args:
        uploaded_file: An uploaded file object from Streamlit, a BytesIO stream,
                       or a raw text string.

    Returns:
        str: Extracted and cleaned text content from the file.

    Raises:
        ValueError: If the file format is unsupported or contains no extractable text.
        RuntimeError: If document reading fails due to parsing or decoding errors.
    """
    if uploaded_file is None:
        return ""

    if isinstance(uploaded_file, str):
        return uploaded_file.strip()

    filename = getattr(uploaded_file, "name", "").lower()

    try:
        if filename.endswith(".pdf"):
            return _extract_pdf(uploaded_file)
        elif filename.endswith(".docx"):
            return _extract_docx(uploaded_file)
        elif filename.endswith(".txt") or not filename:
            return _extract_txt(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: '{filename}'. Please upload a PDF, DOCX, or TXT file.")
    except (ValueError, RuntimeError):
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to extract text from '{filename}': {str(e)}") from e


def _extract_pdf(uploaded_file: Union[UploadedFile, io.BytesIO]) -> str:
    """
    Extract text content from a PDF document page by page.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like buffer for the PDF.

    Returns:
        str: Concatenated text of all pages in the PDF.

    Raises:
        ValueError: If no extractable text is found (e.g., scanned/image-only PDF).
    """
    text_chunks = []
    with pdfplumber.open(uploaded_file) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            page_text = page.extract_text()
            if page_text:
                text_chunks.append(page_text.strip())

    extracted = "\n\n".join(text_chunks).strip()
    if not extracted:
        raise ValueError(
            "No extractable text found in the PDF. The document may be an image-only scan or encrypted."
        )
    return extracted


def _extract_docx(uploaded_file: Union[UploadedFile, io.BytesIO]) -> str:
    """
    Extract text content from a DOCX Microsoft Word document.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like buffer for the DOCX.

    Returns:
        str: Paragraph text concatenated with newlines.
    """
    file_bytes = io.BytesIO(uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file)
    doc = docx.Document(file_bytes)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def _extract_txt(uploaded_file: Union[UploadedFile, io.BytesIO]) -> str:
    """
    Extract text content from a plain text file with fallback encoding support.

    Args:
        uploaded_file: Streamlit UploadedFile or file-like buffer for the TXT.

    Returns:
        str: Decoded text content.
    """
    raw_bytes = uploaded_file.read() if hasattr(uploaded_file, "read") else uploaded_file
    if isinstance(raw_bytes, str):
        return raw_bytes.strip()

    for encoding in ["utf-8", "utf-16", "latin-1", "cp1252"]:
        try:
            return raw_bytes.decode(encoding).strip()
        except (UnicodeDecodeError, AttributeError):
            continue
    return raw_bytes.decode("utf-8", errors="ignore").strip()