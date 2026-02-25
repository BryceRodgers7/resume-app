import streamlit as st
import streamlit.components.v1 as components
import os
import sys
import logging
from pathlib import Path
import nav
from app import home_page

# Page configuration
st.set_page_config(
    page_title="Customer Support Agent",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

nav.config_navigation(home_page)

# Configure logging (don't import from app.py to avoid rendering homepage)
logger = logging.getLogger(__name__)

# Check if we should show the data views instead
query_params = st.query_params
show_data_views = query_params.get("view") == "data"

# If showing data views, load and execute that module instead
if show_data_views:
    # Hide sidebar and page navigation
    st.markdown("""
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Execute the data views script
    views_path = Path(__file__).parent.parent / 'views' / 'All_Data_Views.py'
    with open(views_path, 'r', encoding='utf-8') as f:
        exec(f.read())
    st.stop()

# Custom CSS
st.markdown("""
<style>
    .tool-call-box {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .success-badge {
        background-color: #d4edda;
        color: #155724;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.85em;
    }
    .error-badge {
        background-color: #f8d7da;
        color: #721c24;
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 0.85em;
    }
</style>
<script>
    // Prevent auto-scroll on page load
    window.addEventListener('load', function() {
        setTimeout(function() {
            window.scrollTo(0, 0);
        }, 100);
    });
</script>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = []
    
    # Lazy initialization - only create agent when needed
    if "agent" not in st.session_state:
        st.session_state.agent = None
    
    if "tool_usage" not in st.session_state:
        st.session_state.tool_usage = []
    
    if "show_welcome" not in st.session_state:
        st.session_state.show_welcome = True


def get_agent():
    """Lazy initialization of the agent - only create when first needed."""
    if st.session_state.agent is None:
        # Import only when needed
        from chatbot.agent import CustomerSupportAgent
        with st.spinner("Initializing AI agent..."):
            st.session_state.agent = CustomerSupportAgent()
    return st.session_state.agent


def render_sidebar():
    """Render the sidebar with tool information and usage tracking."""
    with st.sidebar:
        # Tool usage statistics
        st.markdown("### 📊 Tool Usage (This Session)")
        if st.session_state.tool_usage:
            tool_counts = {}
            for usage in st.session_state.tool_usage:
                tool_name = usage['tool']
                tool_counts[tool_name] = tool_counts.get(tool_name, 0) + 1
            
            for tool_name, count in sorted(tool_counts.items(), key=lambda x: x[1], reverse=True):
                st.metric(tool_name, count)
        else:
            st.info("No tools used yet")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.session_state.conversation_history = []
            st.session_state.tool_usage = []
            st.session_state.show_welcome = True
            st.rerun()
        
        st.divider()
        
        # Available Tools section at the bottom
        st.markdown("### 🔧 Available Tools")
        
        # Get tool descriptions (lazy import)
        from tools.schemas import get_tool_descriptions
        tool_descriptions = get_tool_descriptions()
        
        for tool_name, description in tool_descriptions.items():
            with st.expander(f"📌 {tool_name}"):
                st.write(description)


def render_tool_calls(tool_calls):
    """Render tool calls in an expandable section.
    
    Args:
        tool_calls: List of tool call dictionaries
    """
    if not tool_calls:
        logger.debug("No tool calls to render")
        return
    
    logger.info(f"Rendering tool calls section with {len(tool_calls)} calls")
    
    with st.expander(f"🔧 Tools Used ({len(tool_calls)})", expanded=False):
        for i, call in enumerate(tool_calls, 1):
            tool_name = call['tool']
            arguments = call['arguments']
            result = call['result']
            success = result.get('success', False)
            
            logger.debug(f"Rendering tool call {i}: {tool_name} (success={success})")
            
            st.markdown(f"**{i}. {tool_name}**")
            
            # Arguments
            with st.container():
                st.caption("Arguments:")
                st.json(arguments)
            
            # Result
            if success:
                st.markdown(f'<span class="success-badge">✅ Success</span>', unsafe_allow_html=True)
                if 'message' in result:
                    st.success(result['message'])
            else:
                st.markdown(f'<span class="error-badge">❌ Error</span>', unsafe_allow_html=True)
                if 'error' in result:
                    st.error(result['error'])
            
            if i < len(tool_calls):
                st.divider()


# Initialize session state
initialize_session_state()

# Header
st.title("💬 Agentic Customer Support System")

st.markdown("""
### AI Support Agent with Structured Tool Execution & RAG

This demo showcases an agentic AI system built around structured execution and controlled tool access.  
The agent analyzes user intent, selects appropriate tools, performs validated database operations and semantic retrieval, then synthesizes results into coherent responses — illustrating how LLMs can safely operate within real business systems.
""")

with st.expander("🎯 What This Demonstrates", expanded=False):
    st.markdown("""
    - **Autonomous Tool Selection**: The agent determines when and how to call structured backend tools based on user intent.
    - **LLM Function Calling (GPT-4)**: Dynamic selection and execution of 10+ tools using structured schemas.
    - **Hybrid RAG Architecture**: Combines transactional data with vector-based semantic retrieval.
    - **Multi-Database System Design**:
      - PostgreSQL (Supabase) for orders, products, returns, and tickets
      - Qdrant for knowledge base embeddings and semantic search
    - **Stateful Conversations**: Persistent context and tool usage tracking across turns.
    - **Extensible Tool Framework**: Modular tool schemas and implementations designed for expansion. View the tool code [here](https://github.com/BryceRodgers7/resume-app/tree/main/tools)
    """)

with st.expander("🔧 Design & Capabilities", expanded=False):
    st.markdown("""    
    **Execution Flow:**
    1. User message analyzed for intent
    2. LLM selects appropriate tool(s)
    3. Tool schemas and SOP context loaded and cached
    4. Structured tool calls executed (SQL queries, vector search, etc.)
    5. Results validated and synthesized into a final response
    6. Execution metadata logged for inspection
                
    The agent has access to 9 different tools including:
    - **Order Management**: Draft, place, modify, track, and cancel orders
    - **Product Operations**: Search products by name, category, price range, or availability
    - **Knowledge Base**: Semantic search through company policies and procedures
    - **Support Tickets**: Create and manage customer support issues
    - **Returns Processing**: Initiate and track return requests
    - See the list of all available tools in the sidebar
    """)

with st.expander("💡 Try These Interactions", expanded=False):
    st.markdown("""
    **Order Management:**
    - "I want to order 2 wireless headphones and have them shipped to New York"
    - "I need to cancel order #1001"
    - "Track the status of my recent order"
    
    **Product Search:**
    - "Show me computer monitors under $500"
    - "What wireless headphones do you have in stock?"
    - "Find me smartphones with at least 128GB storage"
    
    **Policies & Support:**
    - "What's your return policy?"
    - "How long does shipping take?"
    - "I need help with a defective product"
    
    **Note:** These workflows are not hard-coded responses — the agent dynamically selects tools and executes real database operations. 
    You can view the backend data for reference and see it change in real-time as the agent performs actions.
    """)

st.info("""📊 **Observability Built In**: Click the 'Tools Used' expander within the responses to see the full execution details. 
        Watch the sidebar to see how many tool calls total the agent has used. 
        View the backend data for reference by clicking the 'View All Data Tables' button below, and see it change due to the agent's actions!
        """)

st.caption("Powered by OpenAI GPT-4 with function calling | PostgreSQL (Supabase) | Qdrant Vector Database")

st.divider()

# Sidebar
render_sidebar()

# Main content area
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### Chat")

with col2:
    # Button to open all data views in a new browser tab
    components.html("""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <button onclick="window.open('/support_agent?view=data', '_blank')" style="
                padding: 0.5rem 1rem;
                background-color: #FF4B4B;
                color: white;
                border: none;
                border-radius: 0.5rem;
                cursor: pointer;
                font-size: 0.9rem;
                font-weight: 500;
            ">
                📊 View All Data Tables
            </button>
        </div>
    """, height=50)

# Check API key for later use
api_key_configured = bool(os.getenv("OPENAI_API_KEY"))

# Display welcome message
if st.session_state.show_welcome:
    # Import only when displaying welcome message
    from chatbot.prompts import WELCOME_MESSAGE
    with st.chat_message("assistant"):
        st.markdown(WELCOME_MESSAGE)
    st.session_state.show_welcome = False

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Show tool calls if present
        if "tool_calls" in message and message["tool_calls"]:
            render_tool_calls(message["tool_calls"])

# Chat input
if prompt := st.chat_input("How can I help you today?"):
    # Check API key
    if not api_key_configured:
        st.error("⚠️ Please configure OPENAI_API_KEY environment variable to use the chatbot.")
        st.stop()
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    
    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Initialize agent on first use
            agent = get_agent()
            response, tool_calls = agent.chat(
                prompt,
                st.session_state.conversation_history
            )
        
        # Log response summary
        logger.info(f"\n{'='*80}")
        logger.info(f"USER QUERY: {prompt}")
        logger.info(f"TOOLS USED: {len(tool_calls)}")
        if tool_calls:
            for idx, tool_call in enumerate(tool_calls, 1):
                logger.info(f"  {idx}. {tool_call['tool']}")
        logger.info(f"{'='*80}\n")
        
        # Display response
        st.markdown(response)
        
        # Display tool calls
        if tool_calls:
            logger.info(f"Rendering {len(tool_calls)} tool call(s) in UI")
            render_tool_calls(tool_calls)
            
            # Update tool usage tracking
            st.session_state.tool_usage.extend(tool_calls)
            logger.info(f"Total tools used in session: {len(st.session_state.tool_usage)}")
    
    # Add assistant message to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "tool_calls": tool_calls
    })
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": response
    })
    
    # Rerun to update the UI
    st.rerun()

