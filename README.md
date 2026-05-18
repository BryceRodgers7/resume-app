# AI Portfolio Resume App

A Streamlit-based portfolio app showcasing various AI/ML projects and demos.

## 🚀 Features

- **Agentic Customer Support**: GPT-4 agent with function calling, PostgreSQL tools, and RAG via Qdrant
- **Custom GPT Models**: 10M parameter decoder-only transformers (Shakespeare + Voyager) served via Cloud Run
- **Image Classifier**: Fine-tuned ResNet50 (bird / plane / superman / other) served via Cloud Run
- **Text-to-Image**: Stability AI SD3 integration
- **Pirate Chatbot**: GPT-3.5-turbo with a live-editable system prompt to demonstrate prompt engineering
- **FHIR → OMOP Demo**: Simplified healthcare interoperability — loads synthetic FHIR R4 bundles, transforms them into an OMOP-inspired schema, and surfaces analytics + a terminology mapping report. Supports both sample data and user-uploaded bundles.
- **Architecture View**: Interactive zoomable diagram of the full serverless stack

## 📦 Installation

1. Clone this repository:
```bash
git clone https://github.com/BryceRodgers7/resume-app.git
cd resume-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see [environment variables](#-environment-variables) below).
   For local development you can either set them in your shell or copy
   `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and load them
   via `python-dotenv` / your launch config. `secrets.toml` is in `.gitignore`.

## 🏃 Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔧 Development

### Pages

Each page lives in `pages/` and is registered in `nav.py`:

| File | Route | Purpose |
| --- | --- | --- |
| `pages/support_agent.py` | Support Agent | GPT-4 agent + tools + RAG |
| `pages/image_classifier.py` | Image Classifier | Calls remote ResNet50 inference API |
| `pages/pirate_chatbot.py` | Pirate Chatbot | GPT-3.5-turbo with editable system prompt |
| `pages/stability.py` | Stability | Stability AI SD3 text-to-image |
| `pages/voyager_gpt.py` | Voyager GPT | Calls remote custom-GPT inference API |
| `pages/fhir_omop.py` | FHIR → OMOP | Thin HTTP client over the FHIR → OMOP backend service |
| `pages/architecture.py` | Architecture | Renders the zoomable SVG diagram |

The home page is defined in `app.py` (`home_page()`), passed into
`nav.config_navigation()` so every page renders the same nav. Pages also
`from app import home_page` so navigation works whether the user enters via
`app.py` or any individual page URL.

### Supporting / Upstream Projects

The training pipelines for the deployed models live in separate repos and are
no longer part of this codebase:

- **Image classifier training** — <https://github.com/BryceRodgers7/img-classifier-birdplanesuper>
- **Custom GPT training** — <https://github.com/BryceRodgers7/brycegpt>

The trained image-classifier artifact (`models/*.pth`) is committed for
reference but the deployed model is downloaded from GCS by the Cloud Run
service at startup. This app does not load the `.pth` directly.

### Project Structure

```
resume-app/
├── app.py                       # Main entry — defines home page + delegates to nav
├── nav.py                       # Streamlit page registration (st.navigation)
├── Dockerfile                   # Production container
├── fly.toml                     # Fly.io deployment config
├── requirements.txt             # Python dependencies (PyTorch installed via Dockerfile)
├── pages/                       # Sidebar-visible pages
│   ├── support_agent.py
│   ├── image_classifier.py
│   ├── pirate_chatbot.py
│   ├── stability.py
│   ├── voyager_gpt.py
│   ├── fhir_omop.py
│   └── architecture.py
├── views/                       # Pages reached only via in-app links (no sidebar)
│   └── All_Data_Views.py
├── chatbot/                     # Customer support agent
│   ├── agent.py                 # OpenAI loop + tool execution
│   └── prompts.py               # SYSTEM_PROMPT, WELCOME_MESSAGE
├── tools/                       # Agent tool layer
│   ├── schemas.py               # OpenAI function-call schemas
│   └── implementations.py       # Tool bodies — DB + vector calls
├── database/                    # PostgreSQL (Supabase) access
│   ├── db_manager.py            # Connection + queries
│   ├── schema.sql               # Table DDL (agent_* tables)
│   └── *_insert.sql             # Seed data
├── qdrant/                      # Vector DB (knowledge base)
│   ├── vector_store.py          # Search interface used by the agent
│   ├── vector_load_kb.py        # Bulk-load chunks.json into Qdrant
│   ├── vector_load_onechunk.py  # Single-chunk upsert helper
│   └── chunks.json              # Knowledge-base source content
├── projects/                    # Self-contained portfolio sub-projects
│   └── fhir_omop/               # FHIR → OMOP demo (front-end only — backend lives in a separate repo)
│       ├── README.md
│       └── pipeline/            # api_client.py (HTTP client) + terminology.py (pure compute)
├── components/
│   └── svg_viewer.py            # Zoomable/fullscreen SVG component
├── models/                      # Reference copy of trained classifier artifact
├── .static/                     # Images served by Streamlit (architecture.svg, me.jpg, parrot.jpg)
├── .streamlit/
│   └── secrets.toml.example     # Template — copy to secrets.toml for local dev
├── ARCHITECTURE.md              # System design + diagram
├── DEPLOYMENT.md                # Fly.io deployment guide
└── QUICKSTART_DEPLOYMENT.md     # 5-minute deploy walkthrough
```

### 🔑 Environment Variables

Required for full functionality (set as Fly secrets in production, or via
shell/`secrets.toml` locally):

| Variable | Used by | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | support agent, pirate chatbot, vector store | OpenAI access |
| `SUPADATABASE_URL` | `database/db_manager.py` (support agent, data views, FHIR-OMOP demo) | PostgreSQL connection string (Supabase) |
| `QDRANT_URL` | `qdrant/vector_store.py` | Qdrant Cloud endpoint |
| `QDRANT_API_KEY` | `qdrant/vector_store.py` | Qdrant Cloud auth |
| `STABILITY_KEY` | `pages/stability.py` | Stability AI SD3 |
| `BRYCEGPT_API_URL` | `pages/voyager_gpt.py` | Cloud Run URL for the custom-GPT service |
| `BPSIMGCLSS_API_URL` | `pages/image_classifier.py` | Cloud Run URL for the image-classifier service |

Optional:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LOG_LEVEL` | `INFO` | Root logger level (`DEBUG`, `INFO`, `WARNING`, …) |
| `BPSIMGCLSS_TIMEOUT` | `120` | Read-timeout (seconds) for image classifier API |

## 🌐 Deployment

### ☁️ Fly.io (Recommended - Serverless)

**Quick deployment in 5 minutes!** See [QUICKSTART_DEPLOYMENT.md](QUICKSTART_DEPLOYMENT.md)

```bash
# Install Fly.io CLI
iwr https://fly.io/install.ps1 -useb | iex  # Windows
curl -L https://fly.io/install.sh | sh      # Mac/Linux

# Login and deploy
flyctl auth login
flyctl launch
flyctl secrets set OPENAI_API_KEY="..." DATABASE_URL="..." # etc.
flyctl deploy --ha=false
```

**Features**:
- ✅ Serverless architecture (scales to zero)
- ✅ Auto-scaling based on traffic
- ✅ Built-in HTTPS & CDN
- ✅ Pay-per-use pricing (~$0-5/month)

For detailed instructions, see [DEPLOYMENT.md](DEPLOYMENT.md)

### Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in the app settings
5. Deploy!

### Other Options

- **Docker**: Dockerfile included - `docker build -t resume-app .`
- **AWS/GCP/Azure**: Deploy as a containerized app
- **Heroku**: Deploy with container stack

## 🔐 Security Notes

- Never commit API keys or secrets to version control
- Use `.streamlit/secrets.toml` for local development
- Use environment variables or secrets management for production
- Add `.streamlit/secrets.toml` to your `.gitignore`

## 📝 Customization

### Update Personal Information

Edit `app.py` (specifically the `home_page()` function) to update:
- Your name
- GitHub URL
- Business website URL
- LinkedIn profile
- Project descriptions

### Add More Pages

1. Create a new file in `pages/` (top-level) or `views/` (no sidebar entry).
2. At the top, set the Streamlit page config and call
   `nav.config_navigation(home_page)` so the page renders with the same nav.
3. Register the page in `nav.py` inside `config_navigation()` with an `st.Page(...)` entry.

## 🐛 Troubleshooting

### Common Issues

1. **Module not found**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **API errors**: Verify your API keys are correctly set in secrets.toml

3. **Model loading issues**: Ensure model files are in the correct paths

4. **Deployment issues**: Check Streamlit version compatibility
   ```bash
   pip install --upgrade streamlit
   ```

## 📄 License

MIT License - feel free to use this for your own portfolio!

## 🤝 Contributing

This is a personal portfolio project, but suggestions are welcome!

---

Built with ❤️ using Streamlit
