from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pypdf import PdfReader
from docx import Document
import io
import os
from utils import TextProcessor

router = APIRouter()

text_processor = TextProcessor()

@router.post("/upload-and-extract/")
async def upload_and_extract_text(file: UploadFile = File(...)):
    """
    Upload a .pdf, .txt, or .docx file and extract its text content.
    """
    file_extension = os.path.splitext(file.filename)[1].lower()
    
    if file_extension == ".txt":
        try:
            content = await file.read()
            text = content.decode("utf-8")
            return {"filename": file.filename, "extracted_text": text} ### TODO ###
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading .txt file: {e}")

    elif file_extension == ".pdf":
        try:
            content = await file.read()
            pdf_reader = PdfReader(io.BytesIO(content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() or ""
            chunks = text_processor.chunk_text(text=text, strategy="char", chunk_size=100)
            return {"filename": file.filename, "chunked_text": chunks} ### TODO ###
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading .pdf file: {e}")

    elif file_extension == ".docx":
        try:
            content = await file.read()
            doc = Document(io.BytesIO(content))
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return {"filename": file.filename, "extracted_text": text} ### TODO ###
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error reading .docx file: {e}")

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_extension}. Please upload a .pdf, .txt, or .docx file."
        )