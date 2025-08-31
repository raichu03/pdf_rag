from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import Literal
from pypdf import PdfReader
from docx import Document
import io
import os

from utils import TextProcessor
from services import AddRecords

router = APIRouter()

data_ingestor = AddRecords()
text_processor = TextProcessor()

ChunkingStrategy = Literal["char", "recursive"]

@router.post(
    "/upload-docs/",
    summary="Upload and process a document",
    description="""Uploads a .pdf, .txt, or .docx file, extracts its text,
    and ingests it into the system after chunking.
    """,
    status_code=status.HTTP_201_CREATED,
)
async def upload_and_process_document(
    file: UploadFile = File(
        ..., description="The document to upload (PDF, TXT, or DOCX)."
    ),
    chunking_strategy: ChunkingStrategy = Query(
        "char",
        description="""The strategy to use for text chunking.
        Accepted values are 'char' or 'recursive'.""",
    ),
):
    """
    Handles the document upload, text extraction, and ingestion process.
    """
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in [".txt", ".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Please upload a .pdf, .txt, or .docx file."
        )

    try:
        content = await file.read()
        
        if file_extension == ".txt":
            text = _extract_text_from_txt(content)
        elif file_extension == ".pdf":
            text = _extract_text_from_pdf(content)
        elif file_extension == ".docx":
            text = _extract_text_from_docx(content)

        chunks = text_processor.chunk_text(
            text=text,
            strategy=chunking_strategy,
            chunk_size=100
        )
        ingestion_response = data_ingestor.ingest_data(
            document_name=file.filename, text_chunks=chunks
        )
        return ingestion_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during file processing: {e}"
        )


def _extract_text_from_txt(content: bytes) -> str:
    """Helper function to extract text from a .txt file."""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode .txt file. Ensure it is UTF-8 encoded."
        )


def _extract_text_from_pdf(content: bytes) -> str:
    """Helper function to extract text from a .pdf file."""
    pdf_reader = PdfReader(io.BytesIO(content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


def _extract_text_from_docx(content: bytes) -> str:
    """Helper function to extract text from a .docx file."""
    doc = Document(io.BytesIO(content))
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text