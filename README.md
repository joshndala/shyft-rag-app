# Retrieval Augmented Generation Application

A web application that implements Retrieval Augmented Generation (RAG) to answer questions using information from uploaded documents.

## Features

- **Hybrid Search**: Combines both semantic search (using embeddings) and keyword search (BM25) for optimal retrieval
- **Document Upload**: Support for PDF documents and HTML websites
- **Streaming Responses**: Real-time streaming of AI responses

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: React.js with Material UI components
- **Embeddings**: Sentence Transformers for generating text embeddings
- **Vector Search**: FAISS for efficient similarity search
- **Keyword Search**: BM25 for traditional keyword-based retrieval
- **LLM Integration**: OpenRouter API for accessing large language models
- **Containerization**: Docker for easy deployment

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenRouter API key (for LLM access)
- Hugging Face token (read-only access is sufficient, for downloading embedding models)

### Setup

1. Clone this repository:

2. Create a `.env` file in the `backend` directory with the following contents:
   ```
   OPENROUTER_API_KEY=your_openrouter_api_key
   HUGGINGFACE_HUB_TOKEN=your_huggingface_token
   ```

3. Build and start the application using Docker Compose:
   ```bash
   docker compose build
   docker compose up -d
   ```

4. Access the application at [http://localhost:3000](http://localhost:3000)

## Usage

### Uploading Documents

1. Navigate to the "Upload" page
2. Click "Choose File" and select a PDF or HTML file (The document tested for this app can be found [here](https://arxiv.org/pdf/2412.19437))
3. Click "Upload" to process the document
4. Wait for confirmation that the document has been indexed

### Searching Documents

1. Navigate to the "Search" page
2. Enter your search query
3. View the retrieved passages from your documents

### Asking Questions

1. Navigate to the "Ask" page
2. Enter your question related to the uploaded documents
3. The answer will stream in real-time, using information from the documents

## Development

For development purposes, you can work with the application directly without Docker:

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
```
