"""
ChipFlow Documentation Chat API

A FastAPI backend that provides AI-powered Q&A for ChipFlow documentation.
Uses Vertex AI for embeddings and LLM responses with simple in-memory RAG.
"""
import os
import json
import logging
from typing import Optional
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DOCS_URL = os.getenv("DOCS_URL", "https://chipflow-docs.docs.chipflow-infra.com/llms-full.txt")
GCP_PROJECT = os.getenv("GCP_PROJECT", "chipflow-docs")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")
EMBEDDING_MODEL = "text-embedding-005"
LLM_MODEL = "gemini-1.5-flash"

# Allowed origins for CORS
ALLOWED_ORIGINS = [
    "https://docs.chipflow.io",
    "https://chipflow-docs.docs.chipflow-infra.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]


class ChatRequest(BaseModel):
    question: str
    conversation_history: list = []
    page: Optional[str] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list = []


class DocumentStore:
    """Simple in-memory document store with vector search."""

    def __init__(self):
        self.chunks: list[dict] = []
        self.embeddings: Optional[np.ndarray] = None
        self.initialized = False

    async def initialize(self, docs_url: str):
        """Load and process documentation."""
        logger.info(f"Fetching documentation from {docs_url}")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(docs_url)
            response.raise_for_status()
            content = response.text

        # Split into chunks (by section headers or fixed size)
        self.chunks = self._chunk_content(content)
        logger.info(f"Created {len(self.chunks)} chunks")

        # Generate embeddings
        self.embeddings = await self._generate_embeddings([c["text"] for c in self.chunks])
        self.initialized = True
        logger.info("Document store initialized")

    def _chunk_content(self, content: str, chunk_size: int = 1500, overlap: int = 200) -> list[dict]:
        """Split content into overlapping chunks."""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_size = 0
        current_title = "Documentation"

        for line in lines:
            # Track section headers
            if line.startswith('# '):
                current_title = line[2:].strip()
            elif line.startswith('## '):
                current_title = line[3:].strip()

            current_chunk.append(line)
            current_size += len(line) + 1

            if current_size >= chunk_size:
                chunk_text = '\n'.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "title": current_title,
                })

                # Keep overlap
                overlap_lines = []
                overlap_size = 0
                for l in reversed(current_chunk):
                    if overlap_size + len(l) > overlap:
                        break
                    overlap_lines.insert(0, l)
                    overlap_size += len(l) + 1

                current_chunk = overlap_lines
                current_size = overlap_size

        # Add remaining content
        if current_chunk:
            chunks.append({
                "text": '\n'.join(current_chunk),
                "title": current_title,
            })

        return chunks

    async def _generate_embeddings(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings using Vertex AI."""
        from google.cloud import aiplatform
        from vertexai.language_models import TextEmbeddingModel

        aiplatform.init(project=GCP_PROJECT, location=GCP_LOCATION)
        model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

        # Process in batches
        all_embeddings = []
        batch_size = 5

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            embeddings = model.get_embeddings(batch)
            all_embeddings.extend([e.values for e in embeddings])

        return np.array(all_embeddings)

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for relevant chunks."""
        if not self.initialized:
            raise RuntimeError("Document store not initialized")

        # Generate query embedding
        from google.cloud import aiplatform
        from vertexai.language_models import TextEmbeddingModel

        aiplatform.init(project=GCP_PROJECT, location=GCP_LOCATION)
        model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

        query_embedding = model.get_embeddings([query])[0].values
        query_vec = np.array(query_embedding)

        # Cosine similarity
        similarities = np.dot(self.embeddings, query_vec) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_vec)
        )

        # Get top-k
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.chunks[idx]["text"],
                "title": self.chunks[idx]["title"],
                "score": float(similarities[idx]),
            })

        return results


# Global document store
doc_store = DocumentStore()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize document store on startup."""
    try:
        await doc_store.initialize(DOCS_URL)
    except Exception as e:
        logger.error(f"Failed to initialize document store: {e}")
        # Continue without initialization - will fail gracefully on requests
    yield


app = FastAPI(
    title="ChipFlow Docs Chat API",
    description="AI-powered Q&A for ChipFlow documentation",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "initialized": doc_store.initialized,
        "chunks": len(doc_store.chunks) if doc_store.initialized else 0,
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Answer questions about ChipFlow documentation."""
    if not doc_store.initialized:
        raise HTTPException(
            status_code=503,
            detail="Service initializing, please try again in a moment"
        )

    try:
        # Search for relevant context
        results = await doc_store.search(request.question, top_k=5)

        # Build context
        context_parts = []
        sources = []
        for r in results:
            if r["score"] > 0.5:  # Only include relevant results
                context_parts.append(f"### {r['title']}\n{r['text']}")
                if r["title"] not in sources:
                    sources.append(r["title"])

        context = "\n\n---\n\n".join(context_parts)

        # Build conversation history
        history_text = ""
        if request.conversation_history:
            for msg in request.conversation_history[-4:]:  # Last 4 messages
                role = "User" if msg.get("role") == "user" else "Assistant"
                history_text += f"{role}: {msg.get('content', '')}\n"

        # Generate response using Vertex AI
        from google.cloud import aiplatform
        import vertexai
        from vertexai.generative_models import GenerativeModel

        vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
        model = GenerativeModel(LLM_MODEL)

        prompt = f"""You are a helpful assistant for ChipFlow documentation. Answer the user's question based on the provided context from the documentation.

Guidelines:
- Be concise and accurate
- If the context doesn't contain relevant information, say so
- Reference specific documentation sections when helpful
- Use code examples from the context when relevant

Context from ChipFlow documentation:
{context}

{f"Previous conversation:{chr(10)}{history_text}" if history_text else ""}

User question: {request.question}

Answer:"""

        response = model.generate_content(prompt)
        answer = response.text.strip()

        return ChatResponse(answer=answer, sources=sources)

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
