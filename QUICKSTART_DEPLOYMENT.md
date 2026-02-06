# 🚀 Quick Start: Deploy to Fly.io

Get your app deployed in 5 minutes!

## Step 1: Install Fly.io CLI

**Windows (PowerShell)**:
```powershell
iwr https://fly.io/install.ps1 -useb | iex
```

**Mac/Linux**:
```bash
curl -L https://fly.io/install.sh | sh
```

## Step 2: Login to Fly.io

```bash
flyctl auth login
```

This opens a browser for authentication.

## Step 3: Launch Your App

```bash
# Navigate to your project directory
cd c:\git\resume-app

# Launch the app
flyctl launch
```

Answer the prompts:
- **App name**: `resume-app` (or choose your own)
- **Region**: `iad` (or choose closest to you)
- **PostgreSQL?**: No
- **Redis?**: No
- **Deploy now?**: No (we need to set secrets first)

## Step 4: Set Your Secrets

Replace the placeholder values with your actual credentials:

```bash
# Required: OpenAI
flyctl secrets set OPENAI_API_KEY="sk-..."

# Required: Supabase
flyctl secrets set DATABASE_URL="postgresql://..."
flyctl secrets set SUPABASE_URL="https://..."
flyctl secrets set SUPABASE_KEY="..."

# Required: Qdrant
flyctl secrets set QDRANT_URL="https://..."
flyctl secrets set QDRANT_API_KEY="..."

# Optional: Stability AI (for text-to-image)
flyctl secrets set STABILITY_KEY="..."

# Optional: Custom GPT
flyctl secrets set BRYCEGPT_API_URL="https://..."
```

## Step 5: Deploy!

```bash
flyctl deploy --ha=false
```

Wait 2-3 minutes for the build and deployment.

## Step 6: Open Your App

```bash
flyctl open
```

Your app is now live at `https://your-app-name.fly.dev`! 🎉

---

## Quick Commands

```bash
# View logs
flyctl logs

# Check status
flyctl status

# Scale (if needed)
flyctl scale vm shared-cpu-2x --memory 2048

# Restart
flyctl apps restart
```

## Troubleshooting

**App won't start?**
```bash
# Check logs for errors
flyctl logs

# Most common issue: missing secrets
flyctl secrets list
```

**Out of memory?**
```bash
# Increase memory to 4GB
flyctl scale vm shared-cpu-2x --memory 4096
```

**Need to update secrets?**
```bash
flyctl secrets set KEY="new-value"
```

---

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)
