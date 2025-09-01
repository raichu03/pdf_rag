from typing import Literal, Optional, Dict, Any
import os
import io

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from pypdf import PdfReader
from docx import Document

from utils import TextProcessor
from services import AddRecords

router: APIRouter = APIRouter()

data_ingestor: AddRecords = AddRecords()
text_processor: TextProcessor = TextProcessor()

ChunkingStrategy = Literal["char", "sentence"]

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
        Accepted values are 'char' or 'sentence'.""",
    ),
) -> Optional[str]:
    """Handle document upload, text extraction, and ingestion process."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided."
        )
    
    file_extension: str = os.path.splitext(file.filename)[1].lower()

    if file_extension not in [".txt", ".pdf", ".docx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Please upload a .pdf, .txt, or .docx file."
        )

    try:
        content: bytes = await file.read()
        
        text: str
        if file_extension == ".txt":
            text = _extract_text_from_txt(content)
        elif file_extension == ".pdf":
            text = _extract_text_from_pdf(content)
        elif file_extension == ".docx":
            text = _extract_text_from_docx(content)

        chunks: list[str] = text_processor.chunk_text(
            text=text,
            strategy=chunking_strategy,
            chunk_size=100
        )
        ingestion_response: Optional[str] = data_ingestor.ingest_data(
            document_name=file.filename, text_chunks=chunks
        )
        return ingestion_response

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during file processing: {e}"
        )


def _extract_text_from_txt(content: bytes) -> str:
    """Extract text from a .txt file.
    
    Args:
        content: The file content as bytes.
        
    Returns:
        The decoded text content.
        
    Raises:
        HTTPException: If the file cannot be decoded.
    """
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not decode .txt file. Ensure it is UTF-8 encoded."
        )

def _extract_text_from_pdf(content: bytes) -> str:
    """Extract text from a .pdf file.
    
    Args:
        content: The file content as bytes.
        
    Returns:
        The extracted text content.
    """
    pdf_reader: PdfReader = PdfReader(io.BytesIO(content))
    text: str = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def _extract_text_from_docx(content: bytes) -> str:
    """Extract text from a .docx file.
    
    Args:
        content: The file content as bytes.
        
    Returns:
        The extracted text content.
    """
    doc: Document = Document(io.BytesIO(content))
    text: str = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text