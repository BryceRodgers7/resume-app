# GPT Model API - Google Cloud Run Backend

This backend API serves your custom GPT model for text generation.

## Setup

### Prerequisites
- Google Cloud SDK installed
- Google Cloud project created
- Docker installed (for local testing)

### Configuration

1. **Add your model files**: Place your trained GPT model files in the `models/` directory or configure to load from Google Cloud Storage.

2. **Update model loading**: Edit `main.py` and replace the placeholder model loading code with your actual model architecture and loading logic.

### Local Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python main.py

# Test the API
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "temperature": 0.8, "num_chars": 100}'
```

### Deploy to Google Cloud Run

```bash
# Set your project ID
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Deploy to Cloud Run
gcloud run deploy gpt-model-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Get the service URL
gcloud run services describe gpt-model-api --region us-central1 --format 'value(status.url)'
```

### Environment Variables

You can set environment variables during deployment:

```bash
gcloud run deploy gpt-model-api \
  --source . \
  --set-env-vars MODEL_PATH=/app/models/model.pt
```

### API Endpoints

#### Health Check
```
GET /health
```

#### Generate Text
```
POST /generate
Content-Type: application/json

{
  "seed": 42,           // Optional, default: 42
  "temperature": 0.8,   // Optional, default: 1.0
  "num_chars": 500      // Required, max: 5000
}
```

Response:
```json
{
  "success": true,
  "generated_text": "...",
  "parameters": {
    "seed": 42,
    "temperature": 0.8,
    "num_chars": 500
  }
}
```

## Customization

### Using Google Cloud Storage for Model Files

If your model is too large to include in the container, store it in GCS:

```python
from google.cloud import storage

def download_model_from_gcs(bucket_name, source_blob_name, destination_file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
```

Add to requirements.txt:
```
google-cloud-storage==2.10.0
```

### Adjusting Resources

For larger models, you may need more memory or CPU:

```bash
gcloud run deploy gpt-model-api \
  --memory 4Gi \
  --cpu 4
```

## Monitoring

View logs:
```bash
gcloud run logs tail gpt-model-api --region us-central1
```

## Security

For production, consider:
- Adding authentication (API keys, OAuth)
- Rate limiting
- Request validation
- HTTPS enforcement (automatic on Cloud Run)

