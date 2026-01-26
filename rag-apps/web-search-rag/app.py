import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Web Search RAG",
    page_icon="🔍",
    layout="wide"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'search_history' not in st.session_state:
    st.session_state.search_history = []

# Header
st.markdown('<p class="main-header">🔍 Web Search RAG</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Ask anything. Get answers from the web with citations.</p>', unsafe_allow_html=True)

# Sidebar - Configuration and History
with st.sidebar:
    st.header("⚙️ Configuration")

    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4", "gpt-3.5-turbo"],
        index=1,  # Default to GPT-3.5 (faster and cheaper)
        help="GPT-4 is more accurate but slower and more expensive"
    )

    # Number of search results
    num_results = st.slider(
        "Search Results to Retrieve",
        min_value=3,
        max_value=10,
        value=5,
        help="More results = better context but slower"
    )

    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.1,
        step=0.1,
        help="Lower = more focused, Higher = more creative"
    )

    st.divider()

    # Search History
    st.header("📜 Search History")
    if st.session_state.search_history:
        for i, query in enumerate(reversed(st.session_state.search_history[-5:]), 1):
            st.caption(f"{i}. {query}")
    else:
        st.caption("No searches yet")

    if st.button("Clear History"):
        st.session_state.search_history = []
        st.rerun()

# Helper Functions
def search_duckduckgo(query, num_results=5):
    """Search DuckDuckGo and return results"""
    try:
        # Using DuckDuckGo HTML version
        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        response = requests.post(url, data=params, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = []
        result_divs = soup.find_all('div', class_='result')[:num_results]

        for div in result_divs:
            title_elem = div.find('a', class_='result__a')
            snippet_elem = div.find('a', class_='result__snippet')

            if title_elem and snippet_elem:
                results.append({
                    'title': title_elem.get_text(strip=True),
                    'url': title_elem.get('href', 'N/A'),
                    'snippet': snippet_elem.get_text(strip=True)
                })

        return results
    except Exception as e:
        st.error(f"Search error: {str(e)}")
        return []

def generate_answer(query, search_results, model="gpt-3.5-turbo", temperature=0.1):
    """Generate answer using OpenAI based on search results"""

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Format search results
        formatted_results = ""
        for i, result in enumerate(search_results, 1):
            formatted_results += f"[{i}] {result['title']}\n"
            formatted_results += f"URL: {result['url']}\n"
            formatted_results += f"Content: {result['snippet']}\n\n"

        prompt = f"""You are a helpful research assistant. Answer the user's question based on the web search results provided.

IMPORTANT INSTRUCTIONS:
1. Provide a comprehensive, well-structured answer
2. Use ONLY information from the search results
3. Include inline citations using [1], [2], [3] etc. to reference sources
4. If the search results don't contain enough information, say so
5. Be accurate and factual
6. Format your answer in clear paragraphs

Search Results:
{formatted_results}

User Question: {query}

Answer (with citations):"""

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful research assistant that provides accurate answers with citations."},
                {"role": "user", "content": prompt}
            ],
            temperature=temperature
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating answer: {str(e)}\n\nPlease check your OpenAI API key is set correctly in .env file."

# Main Interface
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Search input
    query = st.text_input(
        "Ask me anything:",
        placeholder="e.g., What are the latest developments in AI? What happened in tech news today?",
        label_visibility="collapsed"
    )

    col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
    with col_btn2:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Process search
if search_button and query:
    # Add to history
    st.session_state.search_history.append(query)

    # Create columns for results
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📝 Answer")

        with st.spinner("Searching the web..."):
            # Step 1: Search
            search_results = search_duckduckgo(query, num_results)

            if search_results:
                # Step 2: Generate answer
                with st.spinner("Generating answer..."):
                    answer = generate_answer(query, search_results, model, temperature)

                # Display answer
                st.markdown(f'<div class="answer-box">{answer}</div>', unsafe_allow_html=True)

                # Display metrics
                st.caption(f"✓ Generated using {model} | {len(search_results)} sources")
            else:
                st.error("Failed to retrieve search results. Please try again.")

    with col2:
        st.subheader("🔗 Sources")

        if search_results:
            # Display sources
            for i, result in enumerate(search_results, 1):
                with st.expander(f"[{i}] {result['title']}", expanded=(i <= 3)):
                    st.markdown(f"**URL:** {result['url']}")
                    st.markdown(f"**Snippet:**")
                    st.write(result['snippet'])

# Example queries
if not query:
    st.divider()
    st.subheader("💡 Try These Examples:")

    example_col1, example_col2, example_col3 = st.columns(3)

    with example_col1:
        st.markdown("""
        **📰 News & Current Events**
        - What happened in tech news today?
        - Latest developments in AI
        - Recent space exploration news
        """)

    with example_col2:
        st.markdown("""
        **🔬 Research & Learning**
        - How does quantum computing work?
        - Best practices for RAG systems
        - Difference between LLMs and traditional ML
        """)

    with example_col3:
        st.markdown("""
        **🛠️ Practical Questions**
        - How to deploy a Streamlit app?
        - Best Python libraries for data science
        - Tips for effective prompting
        """)

# Footer
st.divider()
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.caption("🔍 Web Search RAG | Powered by OpenAI + DuckDuckGo | Built with Streamlit")
