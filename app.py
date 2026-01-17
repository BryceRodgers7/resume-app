import streamlit as st

# Page configuration
st.set_page_config(
    page_title="AI Portfolio - Your Name",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .big-font {
        font-size: 24px !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.title("🤖 AI Portfolio")
st.sidebar.markdown("---")

# Navigation
page = st.sidebar.radio(
    "Navigate to:",
    [
        "🏠 Home",
        "💬 Customer Support Chatbot",
        "🧠 GPT Model (11M Parameters)",
        "🎨 Text-to-Image Generator",
        "🖼️ Image Classifier",
        "🤖 Simple Chatbot"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔗 Links")
st.sidebar.markdown("[GitHub](https://github.com/yourusername)")
st.sidebar.markdown("[Business Website](https://yourbusiness.com)")
st.sidebar.markdown("[LinkedIn](https://linkedin.com/in/yourprofile)")

# Page routing
if page == "🏠 Home":
    from pages import home
    home.show()
elif page == "💬 Customer Support Chatbot":
    from pages import customer_support
    customer_support.show()
elif page == "🧠 GPT Model (11M Parameters)":
    from pages import gpt_model
    gpt_model.show()
elif page == "🎨 Text-to-Image Generator":
    from pages import text_to_image
    text_to_image.show()
elif page == "🖼️ Image Classifier":
    from pages import image_classifier
    image_classifier.show()
elif page == "🤖 Simple Chatbot":
    from pages import simple_chatbot
    simple_chatbot.show()
