from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import uuid
import pypdf
from bs4 import BeautifulSoup
import datetime
from app.services.embedder import document_embedder

router = APIRouter()

UPLOAD_DIR = "data/uploads/"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

def extract_text_from_pdf(filepath):
    """Extract text from PDF."""
    try:
        reader = pypdf.PdfReader(filepath)
        extracted_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        print(f"📝 Extracted {len(extracted_text)} characters from PDF", flush=True)
        return extracted_text
    except Exception as e:
        print(f"❌ Error extracting text from PDF: {str(e)}", flush=True)
        raise HTTPException(status_code=400, detail=f"Error processing PDF: {str(e)}")

def extract_text_from_html(filepath):
    """Extract text from HTML file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f.read(), "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()
        # Get text
        extracted_text = soup.get_text()
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in extracted_text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Remove blank lines
        extracted_text = '\n'.join(chunk for chunk in chunks if chunk)
        
        print(f"📝 Extracted {len(extracted_text)} characters from HTML", flush=True)
        return extracted_text
    except Exception as e:
        print(f"❌ Error extracting text from HTML: {str(e)}", flush=True)
        raise HTTPException(status_code=400, detail=f"Error processing HTML: {str(e)}")

@router.post("/")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document file.
    
    Args:
        file (UploadFile): The file to upload
        
    Returns:
        dict: Status message and document details
    """
    # Generate a unique document ID
    document_id = str(uuid.uuid4())
    
    # Create a timestamp for the upload
    timestamp = datetime.datetime.now().isoformat()
    
    # Get original filename and create unique filename for storage
    original_filename = file.filename
    unique_filename = f"{document_id}_{original_filename}"
    filepath = os.path.join(UPLOAD_DIR, unique_filename)

    # Save uploaded file
    with open(filepath, "wb") as f:
        f.write(file.file.read())

    print(f"📂 File saved at: {filepath}", flush=True)

    # Extract text based on file type
    if file.filename.lower().endswith(".pdf"):
        text = extract_text_from_pdf(filepath)
    elif file.filename.lower().endswith((".html", ".htm")):
        text = extract_text_from_html(filepath)
    else:
        os.remove(filepath)  # Clean up the file
        return {"error": "Unsupported file format. Please upload PDF or HTML files."}

    if not text.strip():
        os.remove(filepath)  # Clean up the file
        return {"error": "No text could be extracted from the document."}

    print(f"🔹 Storing text embeddings for {len(text)} characters", flush=True)

    # Document metadata
    doc_metadata = {
        "id": document_id,
        "original_filename": original_filename,
        "stored_filename": unique_filename,
        "upload_timestamp": timestamp,
        "file_path": filepath,
        "file_size_bytes": os.path.getsize(filepath),
        "character_count": len(text)
    }

    # Store text in search index with document metadata
    chunks_processed = document_embedder.store_text_embeddings(
        text, 
        document_id=document_id, 
        filename=original_filename
    )

    print(f"✅ Text embeddings stored successfully! Processed {chunks_processed} chunks.", flush=True)

    return {
        "message": "Document uploaded and processed successfully",
        "document_id": document_id,
        "filename": original_filename,
        "chunks_processed": chunks_processed,
        "character_count": len(text),
        "timestamp": timestamp
    }