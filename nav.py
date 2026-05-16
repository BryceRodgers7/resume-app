import streamlit as st

# Guard: avoid nested pg.run() when a page script imports app and app calls config_navigation again.
_in_nav_run = False


def config_navigation(home_page):
    global _in_nav_run
    if _in_nav_run:
        return
    _in_nav_run = True
    try:
        # Configure navigation with custom labels
        # Note: Using explicit page configuration prevents Streamlit from falling back
        # to auto-discovery mode which shows pages in alphabetical order
        pages = [
            st.Page(home_page, title="Home", icon="🏠", default=True),
            st.Page("pages/support_agent.py", title="Support Agent", icon="💬"),
            st.Page("pages/image_classifier.py", title="Image Classifier", icon="🖼️"),
            st.Page("pages/pirate_chatbot.py", title="Pirate Chatbot", icon="🏴‍☠️"),
            st.Page("pages/stability.py", title="Stability", icon="🎨"),
            st.Page("pages/voyager_gpt.py", title="Voyager GPT", icon="🚀"),
            st.Page("pages/fhir_omop.py", title="FHIR → OMOP", icon="🧬"),
            st.Page("pages/architecture.py", title="Architecture", icon="🏗️"),
        ]
        pg = st.navigation(pages)
        pg.run()
    finally:
        _in_nav_run = False