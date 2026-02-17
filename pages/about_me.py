import streamlit as st
from pathlib import Path
import nav
from app import home_page

# Page configuration
st.set_page_config(
    page_title="About Me - Bryce Rodgers",
    page_icon="🧍🏻‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

st.title("🧍🏻‍♂️ About Me")

st.markdown("""
---
""")

photo_path = Path(__file__).parent.parent / '.static' / 'me.jpg'
# display my photo (convert Path to string for Streamlit compatibility)
st.image(str(photo_path), width=231, caption="Bryce Rodgers")

st.info("""
I’m a senior software engineer with more than 15 years of experience building scalable backend systems, 
developer tooling, and data-driven applications. I’ve shipped large production systems at companies 
like Pearson and Samsung, where my focus ranged from building internal tools and automation platforms 
to designing reliable software used by millions of people. I have hands-on experience with a variety of 
technologies including Java, Scala, Python, C#, SQL & NoSQL, Docker and modern cloud infrastructure. 
However, I tend to approach problems from a systems perspective rather than a language or framework preference.

I hold a U.S. patent (US9299264B2 — Sound Assessment and Remediation) and have an extensive academic 
background including Mathematics, Statistics and graduate degrees in both Computer 
Science and Business Administration. That foundation shapes how I approach engineering decisions — 
balancing technical rigor with practical outcomes, understanding how it fits into larger 
organizational frameworks, and learning how it is actually used by people.
        
In recent years, I’ve focused heavily on AI-driven applications, machine learning workflows, and modern 
cloud-native architectures. I enjoy building practical systems that combine LLMs, vector search, and 
traditional software engineering to create reliable, usable tools — from agentic support systems and RAG 
pipelines to data-driven applications and experimental simulations. Many of the projects on this site 
reflect that philosophy: real systems built to explore emerging technologies while maintaining 
production-quality engineering standards. I am also in the early stages of building an app and starting 
a company to connect non-profit organizations with donors based on alignment of shared values.

I enjoy working as part of a strong engineering team and value collaboration, shared ownership, and 
thoughtful technical discussion. Outside of work, I’m an active student of markets and data-driven 
decision making through stock and crypto trading, as well as a lifelong sci-fi fan (live long and prosper!) 
whose optimistic view of technology as a tool for progress influences how I think about building software today.
""")