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

### Adding Your Existing Code

Each demo page is located in the `pages/` directory:
- `pages/customer_support.py` - Customer support chatbot
- `pages/gpt_model.py` - GPT model demo
- `pages/text_to_image.py` - Text-to-image generator
- `pages/image_classifier.py` - Image classifier
- `pages/simple_chatbot.py` - Simple chatbot

Simply replace the placeholder code in each file with your existing implementations.

### Project Structure

```
resume-app/
├── app.py                  # Main application with navigation
├── pages/                  # Individual page modules
│   ├── __init__.py
│   ├── home.py
│   ├── customer_support.py
│   ├── gpt_model.py
│   ├── text_to_image.py
│   ├── image_classifier.py
│   └── simple_chatbot.py
├── requirements.txt        # Python dependencies
├── .streamlit/            # Streamlit configuration (create if needed)
│   └── secrets.toml       # API keys and secrets
└── README.md              # This file
```

## 🌐 Deployment

### Streamlit Community Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Add secrets in the app settings
5. Deploy!

### Other Options

- **Heroku**: Use the Procfile and setup.sh
- **Docker**: Create a Dockerfile with Python and Streamlit
- **AWS/GCP/Azure**: Deploy as a containerized app

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
