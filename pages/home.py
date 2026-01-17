import streamlit as st

def show():
    st.title("Welcome to My AI Portfolio 🤖")
    
    st.markdown("""
    ## About Me
    
    Welcome! I'm an AI/ML practitioner passionate about building intelligent systems. 
    This portfolio showcases several projects I've developed over the past couple of years.
    
    ---
    """)
    
    # Create columns for better layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 What You'll Find Here
        
        - **Customer Support Chatbot**: An agentic customer support system with intelligent routing
        - **Custom GPT Model**: A 11-million parameter GPT model I trained from scratch
        - **Text-to-Image Generator**: Create images from text using Stability AI
        - **Image Classifier**: A custom-trained image classification model
        - **Simple Chatbot**: Interactive chatbot with customizable system prompts
        """)
    
    with col2:
        st.markdown("""
        ### 🔧 Technologies Used
        
        - Python & Streamlit
        - PyTorch & TensorFlow
        - Transformers
        - Stability AI API
        - OpenAI API
        - Custom ML Models
        """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 🌐 Connect With Me
    
    Feel free to explore the demos using the navigation on the left. You can also find me at:
    """)
    
    # Create buttons for links
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📁 View My GitHub", use_container_width=True):
            st.markdown("[GitHub Profile](https://github.com/yourusername)")
    
    with col2:
        if st.button("💼 My Business", use_container_width=True):
            st.markdown("[Business Website](https://yourbusiness.com)")
    
    with col3:
        if st.button("💻 LinkedIn", use_container_width=True):
            st.markdown("[LinkedIn Profile](https://linkedin.com/in/yourprofile)")
    
    st.markdown("---")
    
    st.info("👈 Use the sidebar to navigate between different projects and demos!")
