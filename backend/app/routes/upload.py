from fastapi import APIRouter, File, UploadFile
import os
import pypdf
from bs4 import BeautifulSoup
from app.services.embedder import store_text_embeddings

router = APIRouter()

UPLOAD_DIR = "data/"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_pdf(filepath):
    """Extract text from PDF."""
    reader = pypdf.PdfReader(filepath)
    return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

def extract_text_from_html(filepath):
    """Extract text from HTML file."""
    with open(filepath, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    return soup.get_text()

@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    filepath = os.path.join(UPLOAD_DIR, file.filename)

    # Save uploaded file
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    # Extract text
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(filepath)
    elif file.filename.endswith(".html"):
        text = extract_text_from_html(filepath)
    else:
        return {"error": "Unsupported file format"}

    # Store text in search index
    store_text_embeddings(text)
    
    return {"message": "Document uploaded and processed successfully"}