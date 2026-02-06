# Deployment Guide for Fly.io

This guide will help you deploy your Streamlit application to Fly.io.

## Prerequisites

1. **Install flyctl** (Fly.io CLI)
   ```bash
   # macOS/Linux
   curl -L https://fly.io/install.sh | sh
   
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Sign up for Fly.io**
   ```bash
   flyctl auth signup
   # or login if you already have an account
   flyctl auth login
   ```

## Initial Setup

### 1. Create Fly.io App (First Time Only)

```bash
# Launch the app (this creates the app on Fly.io)
flyctl launch
```

When prompted:
- **App name**: Choose a unique name (or use `resume-app`)
- **Region**: Choose closest to your users (e.g., `iad` for US East)
- **Would you like to set up a PostgreSQL database?**: No (you're using Supabase)
- **Would you like to set up a Redis database?**: No
- **Would you like to deploy now?**: No (we'll set secrets first)

### 2. Set Environment Variables (Secrets)

⚠️ **IMPORTANT**: Set these before your first deployment!

```bash
# OpenAI API Key
flyctl secrets set OPENAI_API_KEY="your-openai-api-key-here"

# Supabase Database
flyctl secrets set DATABASE_URL="postgresql://user:password@host:port/database"
flyctl secrets set SUPABASE_URL="https://your-project.supabase.co"
flyctl secrets set SUPABASE_KEY="your-supabase-anon-key"

# Qdrant Vector Database
flyctl secrets set QDRANT_URL="https://your-cluster.qdrant.io"
flyctl secrets set QDRANT_API_KEY="your-qdrant-api-key"

# Stability AI
flyctl secrets set STABILITY_KEY="your-stability-ai-key"

# Custom GPT API (Google Cloud Run)
flyctl secrets set BRYCEGPT_API_URL="https://your-service.run.app"
```

To view set secrets (values are hidden):
```bash
flyctl secrets list
```

To remove a secret:
```bash
flyctl secrets unset SECRET_NAME
```

## Deploy

### Deploy to Fly.io

```bash
# Deploy the app
flyctl deploy --ha=false
```

The `--ha=false` flag deploys a single instance (cheaper, suitable for portfolio projects).

### Monitor Deployment

```bash
# Watch the deployment logs
flyctl logs

# Check app status
flyctl status

# View dashboard in browser
flyctl dashboard
```

## Post-Deployment

### Open Your App

```bash
# Open in browser
flyctl open
```

Your app will be available at: `https://resume-app.fly.dev` (or your chosen app name)

### View Logs

```bash
# Real-time logs
flyctl logs

# Filter logs
flyctl logs --app resume-app
```

### Check Resource Usage

```bash
# View metrics
flyctl metrics

# SSH into the container (for debugging)
flyctl ssh console
```

## Scaling

### Manual Scaling

```bash
# Scale to specific count
flyctl scale count 2

# Scale VM size
flyctl scale vm shared-cpu-2x --memory 4096
```

### Auto-Scaling (Configured in fly.toml)

The app is configured to:
- **Auto-stop**: Machines stop when idle
- **Auto-start**: Machines start on request
- **Min machines**: 0 (scale to zero for cost savings)

## Cost Optimization

### Current Configuration
- **CPU**: 2 shared CPUs
- **Memory**: 2GB RAM
- **Auto-scaling**: Scale to zero when idle
- **Estimated cost**: ~$0-5/month (depending on usage)

### To Reduce Costs
```bash
# Scale down VM
flyctl scale vm shared-cpu-1x --memory 1024

# Or set min machines to 0 in fly.toml (already configured)
```

## Troubleshooting

### App Won't Start

1. **Check logs**:
   ```bash
   flyctl logs
   ```

2. **Common issues**:
   - Missing environment variables (secrets)
   - Port mismatch (ensure Streamlit uses port 8501)
   - Dependencies not installed (check Dockerfile)

### Health Check Failing

The health check endpoint is `/_stcore/health`. If it fails:
```bash
# Increase grace period in fly.toml
[[http_service.checks]]
  grace_period = "30s"  # Increase from 10s
```

### Out of Memory

```bash
# Increase memory
flyctl scale vm shared-cpu-2x --memory 4096
```

### Connection Issues to External Services

Ensure all secrets are set correctly:
```bash
flyctl secrets list
```

### Debug in Production

```bash
# SSH into the running container
flyctl ssh console

# Run Python commands
python3 -c "import streamlit; print(streamlit.__version__)"
```

## Update fly.toml Configuration

Edit `fly.toml` to change:
- **Region**: `primary_region = "iad"` (change to closest region)
- **Resources**: VM size and memory
- **Auto-scaling**: Min/max machines

Available regions:
```bash
flyctl regions list
```

Common regions:
- `iad` - Ashburn, VA (US East)
- `lax` - Los Angeles, CA (US West)
- `ord` - Chicago, IL (US Central)
- `lhr` - London, UK
- `fra` - Frankfurt, Germany
- `syd` - Sydney, Australia

## CI/CD (GitHub Actions)

To set up automatic deployments on push to main:

1. Get your Fly.io API token:
   ```bash
   flyctl auth token
   ```

2. Add as GitHub secret: `FLY_API_TOKEN`

3. Create `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to Fly.io
   on:
     push:
       branches: [main]
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - uses: superfly/flyctl-actions/setup-flyctl@master
         - run: flyctl deploy --remote-only
           env:
             FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
   ```

## Useful Commands Reference

```bash
# View all apps
flyctl apps list

# Destroy app (careful!)
flyctl apps destroy resume-app

# View pricing
flyctl platform vm-sizes

# View regions
flyctl platform regions

# Restart app
flyctl apps restart resume-app

# View certificates (HTTPS)
flyctl certs list

# Scale to zero (stop all machines)
flyctl scale count 0

# Scale back up
flyctl scale count 1
```

## Environment-Specific Configuration

### Development
```bash
# Test locally with Docker
docker build -t resume-app .
docker run -p 8501:8501 resume-app
```

### Staging (Optional)
```bash
# Create staging app
flyctl apps create resume-app-staging
flyctl deploy --app resume-app-staging
```

## Support & Resources

- **Fly.io Docs**: https://fly.io/docs/
- **Fly.io Community**: https://community.fly.io/
- **Streamlit Docs**: https://docs.streamlit.io/
- **Your App Dashboard**: https://fly.io/apps/resume-app

## Next Steps After Deployment

1. ✅ Test all features in production
2. ✅ Set up custom domain (optional)
3. ✅ Configure monitoring/alerts
4. ✅ Set up backups for any persistent data
5. ✅ Add analytics (Google Analytics, etc.)

## Custom Domain (Optional)

```bash
# Add custom domain
flyctl certs add yourdomain.com

# Get DNS records to add
flyctl certs show yourdomain.com
```

Then add the provided DNS records to your domain registrar.

---

**Questions?** Check the Fly.io docs or community forums!
