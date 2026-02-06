# AI Portfolio Resume App

A Streamlit-based portfolio app showcasing various AI/ML projects and demos.

## 🚀 Features

- **Customer Support Chatbot**: Agentic customer support system
- **Custom GPT Model**: 11M parameter GPT model trained from scratch
- **Text-to-Image Generator**: Using Stability AI's API
- **Image Classifier**: Custom-trained image classification model
- **Simple Chatbot**: Interactive chatbot with editable system prompts

## 📦 Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd resume-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your secrets (optional, for API keys):
Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-openai-key"
STABILITY_API_KEY = "your-stability-key"
ANTHROPIC_API_KEY = "your-anthropic-key"
```

## 🏃 Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔧 Development

### Training the Image Classifier

The image classifier can identify **birds**, **planes**, **Superman**, and **other** objects!

To train your custom model:

1. **Create dataset structure:**
   ```bash
   cd model_tuning
   python download_sample_data.py
   ```

2. **Add training images** to `model_tuning/dataset/train/<category>/`
   - Add validation images to `model_tuning/dataset/val/<category>/`
   - Recommended: 50-100+ images per category for training
   - Recommended: 10-20+ images per category for validation

3. **Train the model:**
   ```bash
   python train_classifier.py
   ```

4. **Test the model:**
   ```bash
   python test_model.py
   ```

5. **Use in the app** - The model will be automatically loaded by the Image Classifier page!

See `model_tuning/README.md` for detailed instructions.

### Adding Your Existing Code

Each demo page is located in the `pages/` directory:
- `pages/customer_support.py` - Customer support chatbot
- `pages/gpt_model.py` - GPT model demo
- `pages/stability.py` - Text-to-image generator
- `pages/image_classifier.py` - Image classifier (now fully functional!)
- `pages/pirate_chatbot.py` - Pirate-themed chatbot

Simply replace the placeholder code in each file with your existing implementations.

### Project Structure

```
resume-app/
├── app.py                  # Main application with navigation
├── pages/                  # Individual page modules
│   ├── __init__.py
│   ├── about_me.py
│   ├── customer_support.py
│   ├── gpt_model.py
│   ├── stability.py
│   ├── image_classifier.py
│   └── pirate_chatbot.py
├── model_tuning/          # Model training scripts
│   ├── train_classifier.py
│   ├── download_sample_data.py
│   ├── test_model.py
│   ├── README.md
│   └── dataset/          # Training data goes here
├── models/                # Trained models
├── requirements.txt       # Python dependencies
├── .streamlit/           # Streamlit configuration (create if needed)
│   └── secrets.toml      # API keys and secrets
└── README.md             # This file
```

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

Edit `app.py` and `pages/home.py` to update:
- Your name
- GitHub URL
- Business website URL
- LinkedIn profile
- Project descriptions

### Add More Pages

1. Create a new file in `pages/` directory
2. Define a `show()` function
3. Add navigation option in `app.py`

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
