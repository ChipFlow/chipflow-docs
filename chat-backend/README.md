# ChipFlow Docs Chat Backend

A FastAPI backend that provides AI-powered Q&A for ChipFlow documentation using Vertex AI.

## Architecture

- **FastAPI** - Web framework with async support
- **Vertex AI** - Embeddings (text-embedding-005)
- **Gemini API** - LLM responses (Gemini 2.0 Flash)
- **In-memory RAG** - Simple vector search using numpy
- **Cloud Run** - Serverless deployment
- **Gmail SMTP** - Support email delivery

## How it Works

1. On startup, fetches `llms-full.txt` from the docs site
2. Chunks the documentation into overlapping segments
3. Generates embeddings for each chunk using Vertex AI
4. When a question arrives:
   - Generates query embedding
   - Finds most similar chunks via cosine similarity
   - Sends relevant context + question to Gemini
   - Returns the response

## Local Development

### Prerequisites

- Python 3.12+
- Google Cloud SDK with authentication configured
- Access to a GCP project with Vertex AI enabled

### Setup

```bash
cd chat-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GCP_PROJECT=your-project-id
export GCP_LOCATION=us-central1
export DOCS_URL=https://docs.chipflow.io/llms-full.txt

# Run locally
python main.py
```

The server will start at http://localhost:8080

### Test the API

```bash
# Health check
curl http://localhost:8080/health

# Ask a question
curl -X POST http://localhost:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Amaranth?"}'
```

## Deployment to Cloud Run

### Prerequisites

1. GCP project with billing enabled
2. Enable required APIs:
   ```bash
   gcloud services enable \
     cloudbuild.googleapis.com \
     run.googleapis.com \
     aiplatform.googleapis.com \
     containerregistry.googleapis.com
   ```

3. Grant Cloud Run service account Vertex AI access:
   ```bash
   PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
     --role="roles/aiplatform.user"
   ```

### Deploy with Cloud Build

```bash
cd chat-backend

# Deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or manually build and deploy
gcloud builds submit --tag gcr.io/$PROJECT_ID/chipflow-docs-chat
gcloud run deploy chipflow-docs-chat \
  --image gcr.io/$PROJECT_ID/chipflow-docs-chat \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --set-env-vars "DOCS_URL=https://docs.chipflow.io/llms-full.txt,GCP_PROJECT=$PROJECT_ID,GCP_LOCATION=us-central1"
```

### After Deployment

1. Get the Cloud Run URL:
   ```bash
   gcloud run services describe chipflow-docs-chat --region us-central1 --format='value(status.url)'
   ```

2. Update the chat widget in `docs/source/_static/js/chat-widget.js`:
   ```javascript
   const CONFIG = {
     apiUrl: 'https://chipflow-docs-chat-xxxxx.a.run.app/api/chat',
     // ...
   };
   ```

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCS_URL` | `https://chipflow-docs.docs.chipflow-infra.com/llms-full.txt` | URL to fetch documentation |
| `GCP_PROJECT` | `chipflow-docs` | Google Cloud project ID |
| `GCP_LOCATION` | `us-central1` | Vertex AI region |
| `GEMINI_API_KEY` | - | API key from Google AI Studio |
| `SMTP_USER` | - | Gmail address for sending support emails |
| `SMTP_PASSWORD` | - | Gmail App Password (16 characters) |
| `SUPPORT_EMAIL` | `support@chipflow.io` | Where support requests are sent |
| `PORT` | `8080` | Server port |

### Setting up Gmail SMTP for Support Emails

The `/api/request-support` endpoint uses Gmail SMTP to send support request emails.

1. **Create a Gmail App Password** (requires 2FA to be enabled on the account):
   - Go to https://myaccount.google.com/apppasswords
   - Sign in to your Google account
   - Select "Mail" as the app and your device type
   - Click "Generate"
   - Copy the 16-character password (spaces are optional)

2. **Add the secrets to GitHub** (for CI/CD deployment):
   ```bash
   # The Gmail address to send from
   gh secret set SMTP_USER --repo ChipFlow/chipflow-docs

   # The 16-character app password
   gh secret set SMTP_PASSWORD --repo ChipFlow/chipflow-docs
   ```

3. **Optionally configure the support destination**:
   ```bash
   # Where support emails are sent (defaults to support@chipflow.io)
   gh variable set SUPPORT_EMAIL --repo ChipFlow/chipflow-docs
   ```

**Note:** If using Google Workspace, ensure "Less secure app access" or App Passwords are enabled in the admin console.

## Cost Estimation

Based on ~50 users with infrequent queries (~100 queries/day):

- **Vertex AI Embeddings**: ~$0.01/1000 queries
- **Gemini 1.5 Flash**: ~$0.075/1M input tokens, $0.30/1M output tokens
- **Cloud Run**: Pay-per-use, scales to zero when idle

Estimated monthly cost: **$5-20** (well under $100 budget)

## API Reference

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "initialized": true,
  "chunks": 150
}
```

### `POST /api/chat`

Ask a question about the documentation.

**Request:**
```json
{
  "question": "How do I create an Amaranth module?",
  "conversation_history": [
    {"role": "user", "content": "previous question"},
    {"role": "assistant", "content": "previous answer"}
  ],
  "page": "/amaranth/guide/basics.html"
}
```

**Response:**
```json
{
  "answer": "To create an Amaranth module...",
  "sources": ["Getting Started", "Module Basics"]
}
```

### `POST /api/request-support`

Send a support request email with conversation context.

**Request:**
```json
{
  "email": "user@example.com",
  "subject": "Help with pin configuration",
  "message": "I'm having trouble configuring the GPIO pins...",
  "conversation_history": [
    {"role": "user", "content": "How do I configure GPIO?"},
    {"role": "assistant", "content": "You can configure GPIO using..."}
  ],
  "page": "/chipflow-lib/gpio.html"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Your support request has been sent. We'll respond to your email shortly."
}
```
