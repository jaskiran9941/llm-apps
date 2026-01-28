"""
Tab 1: Baseline Text-Only RAG
Simple demonstration showing text-only retrieval.
"""

import streamlit as st


def render():
    """Render baseline RAG tab."""

    st.header("📄 Text-Only RAG (Baseline)")

    st.markdown("""
    This is the **baseline approach** - traditional RAG with text chunks only.

    **Limitations:**
    - ❌ Cannot understand images or diagrams
    - ❌ Cannot parse tables or structured data
    - ❌ Cannot process audio or video content
    - ❌ Misses important visual/structural information

    **This demonstrates WHY we need multimodal RAG!**
    """)

    st.info("💡 **Try the other tabs** to see how adding images, tables, and audio improves results!")

    # Simple demo
    st.markdown("---")
    st.subheader("Example: Why Text-Only Fails")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**❌ Text-Only Query:**")
        st.code("""
Query: "What was Q3 revenue?"

Text-Only Result:
"The document mentions various
quarterly results and revenue
figures across different time
periods..."

❌ Vague, can't find exact number
        """)

    with col2:
        st.markdown("**✅ With Table RAG:**")
        st.code("""
Query: "What was Q3 revenue?"

Table RAG Result:
"Q3 revenue for Widget A was
$145,000, Widget B was $105,000,
and Service A was $1,050,000."

✅ Precise, pulls from actual table
        """)

    st.markdown("---")

    st.markdown("**Continue to the next tabs to see:**")
    st.markdown("- 🖼️ **Tab 2**: How images provide visual context")
    st.markdown("- 📊 **Tab 3**: How tables enable structured queries")
    st.markdown("- 🎵 **Tab 4**: How audio adds spoken information")
    st.markdown("- ⚖️ **Tab 5**: Side-by-side comparison of all approaches")
