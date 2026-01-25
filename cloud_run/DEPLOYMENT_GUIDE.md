# GPT Model Feature - Full Deployment Guide

This guide covers deploying the GPT model feature with:
- **Backend**: Google Cloud Run (Python Flask API)
- **Frontend**: Fly.io (Streamlit app)

## Architecture Overview

```
┌─────────────────┐
│   Streamlit     │
│   (Fly.io)      │
│  Frontend UI    │
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Flask API      │
│ (Cloud Run)     │
│  GPT Model      │
└─────────────────┘
```

## Part 1: Backend Setup (Google Cloud Run)

### Step 1: Customize the Model Loading

Edit `cloud_run/main.py` and replace the placeholder in the `load_model()` function:

```python
def load_model():
    global model, device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # YOUR CODE HERE:
    # Import your model class
    # Load your model weights
    # Set to eval mode
    
    model.to(device)
    model.eval()
    print(f"Model loaded on device: {device}")
    return model
```

And update the `generate_text()` function with your generation logic:

```python
def generate_text(seed, temperature, num_chars):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
    
    # YOUR CODE HERE:
    # Use your model to generate text
    
    with torch.no_grad():
        # Your generation code
        pass
    
    return generated_text
```

### Step 2: Add Model Files

Choose one option:

**Option A: Include in Docker Image** (for smaller models)
- Place your model file(s) in `cloud_run/models/`
- Update Dockerfile if needed to copy model files

**Option B: Load from Google Cloud Storage** (recommended for larger models)
- Upload model to GCS bucket
- Add download logic in `load_model()`
- Add `google-cloud-storage` to `cloud_run/requirements.txt`

### Step 3: Deploy to Cloud Run

```bash
# Navigate to cloud_run directory
cd cloud_run

# Set your GCP project
export PROJECT_ID=your-project-id
gcloud config set project $PROJECT_ID

# Enable required APIs (first time only)
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Deploy
gcloud run deploy gpt-model-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10

# Get your service URL
gcloud run services describe gpt-model-api \
  --region us-central1 \
  --format 'value(status.url)'
```

Save the URL that's printed - you'll need it for the frontend!

### Step 4: Test the Backend

```bash
# Test health endpoint
curl https://your-service-url.run.app/health

# Test generation
curl -X POST https://your-service-url.run.app/generate \
  -H "Content-Type: application/json" \
  -d '{
    "seed": 42,
    "temperature": 0.8,
    "num_chars": 100
  }'
```

## Part 2: Frontend Setup (Fly.io)

### Step 1: Set Environment Variable

You need to tell your Streamlit app where the Cloud Run API is.

**Option A: Using fly.toml**

Add to your `fly.toml`:

```toml
[env]
  GPT_API_URL = "https://your-service-url.run.app"
```

**Option B: Using Fly CLI**

```bash
fly secrets set GPT_API_URL="https://your-service-url.run.app"
```

### Step 2: Deploy to Fly.io

```bash
# From project root
fly deploy
```

### Step 3: Test the Complete Flow

1. Open your Streamlit app on Fly.io
2. Navigate to the "Custom GPT Model" page
3. Click "Test Connection" in the sidebar
4. If successful, configure generation parameters
5. Click "Generate Text"

## Troubleshooting

### Backend Issues

**Model not loading:**
- Check Cloud Run logs: `gcloud run logs tail gpt-model-api --region us-central1`
- Verify model file paths
- Check memory limits (increase if needed)

**Timeout errors:**
- Increase timeout: `--timeout 600`
- Increase memory/CPU resources
- Optimize generation code

**Cold start issues:**
- Set minimum instances: `--min-instances 1`
- Implement model caching properly

### Frontend Issues

**Connection failed:**
- Verify API URL is correct
- Check Cloud Run service is deployed
- Ensure Cloud Run allows unauthenticated requests
- Check CORS is enabled in backend

**Slow generation:**
- This is expected for large models
- Consider adding progress indicators
- Set appropriate timeout in frontend (currently 300s)

### CORS Issues

If you get CORS errors, verify in `cloud_run/main.py`:

```python
from flask_cors import CORS
CORS(app)  # This should be present
```

## Cost Optimization

### Google Cloud Run

- **CPU allocation**: Use "CPU is only allocated during request processing"
- **Auto-scaling**: Set max-instances based on expected load
- **Minimum instances**: Set to 0 if cost is a concern (increases cold start time)

```bash
gcloud run deploy gpt-model-api \
  --cpu-throttling \
  --min-instances 0 \
  --max-instances 5
```

### Monitoring Costs

```bash
# View Cloud Run metrics
gcloud run services describe gpt-model-api --region us-central1

# Check billing
gcloud billing accounts list
```

## Security Enhancements (Optional)

### Add API Key Authentication

1. Add to backend (`cloud_run/main.py`):

```python
API_KEY = os.environ.get('API_KEY')

@app.before_request
def check_api_key():
    if request.endpoint not in ['health']:
        key = request.headers.get('X-API-Key')
        if key != API_KEY:
            return jsonify({"error": "Unauthorized"}), 401
```

2. Set API key in Cloud Run:

```bash
gcloud run deploy gpt-model-api \
  --set-env-vars API_KEY=your-secret-key
```

3. Update frontend to send API key in headers

### Rate Limiting

Consider adding rate limiting to prevent abuse:

```bash
pip install flask-limiter
```

## Next Steps

1. ✅ Customize model loading logic
2. ✅ Deploy backend to Cloud Run
3. ✅ Test API endpoints
4. ✅ Configure frontend environment
5. ✅ Deploy frontend to Fly.io
6. ✅ Test complete integration
7. 📊 Monitor performance and costs
8. 🔒 Add security features (optional)

## Resources

- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Fly.io Documentation](https://fly.io/docs/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

