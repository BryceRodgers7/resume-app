import streamlit as st
from pathlib import Path

# Page configuration
st.set_page_config(
    page_title="About Me - Bryce Rodgers",
    page_icon="🧍🏻‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🧍🏻‍♂️ About Me")

st.markdown("""
This is a page where you'll learn all about me, Bryce Rodgers!

---
""")

photo_path = Path(__file__).parent.parent / '.static' / 'me.jpg'
# display my photo
st.image(photo_path, width=231, caption="Bryce Rodgers")

st.info("""
I’m a senior software engineer with more than 15 years of experience building scalable backend systems, 
developer tooling, and data-driven applications. I’ve worked on large production systems at companies 
like Pearson and Samsung, where my focus ranged from building internal tools and automation platforms 
to designing reliable software used by millions of people. I have hands-on experience with a variety of 
technologies including Java, Scala, Python, C#, SQL & NoSQL, Docker and modern cloud infrastructure, 
but I tend to approach problems from a systems perspective rather than a language or framework preference.

I hold a U.S. patent (US9299264B2 — Sound Assessment and Remediation) and have an extensive academic 
background starting with Mathematics, Psychometrics & Psychology, plus graduate degrees in both Computer 
Science and Business Administration. That foundation shapes how I approach engineering decisions — 
balancing technical rigor with practical outcomes and an understanding of how it fits into larger 
organizational frameworks and how it is used by people.
        
In recent years, I’ve focused heavily on AI-driven applications, machine learning workflows, and modern 
cloud-native architectures. I enjoy building practical systems that combine LLMs, vector search, and 
traditional software engineering to create reliable, usable tools — from agentic support systems and RAG 
pipelines to data-driven applications and experimental simulations. Many of the projects on this site 
reflect that philosophy: real systems built to explore emerging technologies while maintaining 
production-quality engineering standards.

I enjoy working as part of a strong engineering team and value collaboration, shared ownership, and 
thoughtful technical discussion. Outside of work, I’m an active student of markets and data-driven 
decision making through stock and crypto trading, and a lifelong science fiction fan — particularly 
Star Trek (live long and prosper!), whose optimistic view of technology as a tool for progress 
continues to influence how I think about building software today.
""")