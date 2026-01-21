import plotly.graph_objects as go
import streamlit as st
from typing import List, Dict

class TokenVisualizer:
    """Visualize token usage and context window management."""

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """
        Rough token estimation (4 characters ≈ 1 token).

        For educational purposes. Real tokenization is more complex.
        """
        return len(text) // 4

    @staticmethod
    def show_context_window(
        conversation_turns: List[Dict],
        max_tokens: int = 8000
    ):
        """
        Visualize how conversation history fills the context window.

        Args:
            conversation_turns: List of conversation turns
            max_tokens: Maximum context window size
        """
        if not conversation_turns:
            st.info("No conversation history yet")
            return

        # Calculate cumulative tokens
        cumulative_tokens = []
        labels = []
        token_counts = []

        total = 0
        for i, turn in enumerate(conversation_turns):
            # Estimate tokens for this turn
            user_tokens = TokenVisualizer.estimate_tokens(turn['user_message'])
            assistant_tokens = TokenVisualizer.estimate_tokens(turn['assistant_response'])
            turn_tokens = user_tokens + assistant_tokens

            total += turn_tokens
            cumulative_tokens.append(total)
            labels.append(f"Turn {i+1}")
            token_counts.append(turn_tokens)

        # Create stacked bar chart
        fig = go.Figure()

        # Show each turn as a segment
        y_start = 0
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']

        for i, (label, tokens) in enumerate(zip(labels, token_counts)):
            fig.add_trace(go.Bar(
                y=[tokens],
                name=label,
                marker_color=colors[i % len(colors)],
                hovertemplate=f"{label}<br>Tokens: {tokens}<extra></extra>",
                orientation='v'
            ))

        # Add context limit line
        fig.add_hline(
            y=max_tokens,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Context Limit ({max_tokens} tokens)",
            annotation_position="right"
        )

        fig.update_layout(
            title="Context Window Usage",
            yaxis_title="Cumulative Tokens",
            barmode='stack',
            height=400,
            showlegend=True
        )

        st.plotly_chart(fig, use_container_width=True)

        # Show statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Tokens", f"{cumulative_tokens[-1]:,}")
        with col2:
            st.metric("Utilization", f"{(cumulative_tokens[-1]/max_tokens*100):.1f}%")
        with col3:
            remaining = max_tokens - cumulative_tokens[-1]
            st.metric("Remaining", f"{remaining:,}")

        # Warning if approaching limit
        if cumulative_tokens[-1] > max_tokens * 0.8:
            st.warning("⚠️ Approaching context limit! Older messages will be dropped soon.")

    @staticmethod
    def show_token_comparison(with_memory_tokens: int, without_memory_tokens: int):
        """
        Compare token usage between WITH and WITHOUT memory.

        Args:
            with_memory_tokens: Tokens used with memory
            without_memory_tokens: Tokens used without memory
        """
        st.markdown("### 📊 Token Usage Comparison")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "WITH Memory",
                f"{with_memory_tokens:,} tokens",
                delta=f"+{with_memory_tokens - without_memory_tokens:,}",
                delta_color="normal"
            )

        with col2:
            st.metric(
                "WITHOUT Memory",
                f"{without_memory_tokens:,} tokens",
                delta=None
            )

        # Create comparison chart
        fig = go.Figure(data=[
            go.Bar(
                x=['WITH Memory', 'WITHOUT Memory'],
                y=[with_memory_tokens, without_memory_tokens],
                marker_color=['#FF6B6B', '#4ECDC4'],
                text=[f"{with_memory_tokens:,}", f"{without_memory_tokens:,}"],
                textposition='auto',
            )
        ])

        fig.update_layout(
            title="Token Usage",
            yaxis_title="Tokens",
            height=300
        )

        st.plotly_chart(fig, use_container_width=True)

        # Explanation
        st.info("""
        **Why more tokens with memory?**

        Memory requires additional context:
        - 📚 Retrieved documents (semantic memory)
        - 💬 Conversation history (episodic memory)

        **Trade-off:** More tokens = more cost BUT better accuracy and context
        """)

    @staticmethod
    def show_sliding_window_demo(turns: List[Dict], max_turns: int):
        """
        Demonstrate sliding window mechanism for conversation history.

        Args:
            turns: All conversation turns
            max_turns: Maximum turns to keep
        """
        st.markdown("### 🪟 Sliding Window Mechanism")

        if len(turns) <= max_turns:
            st.success(f"✅ All {len(turns)} turns fit in memory (max: {max_turns})")
        else:
            dropped = len(turns) - max_turns
            st.warning(f"⚠️ {dropped} oldest turn(s) dropped to fit {max_turns} turn limit")

        # Visualize which turns are kept
        for i, turn in enumerate(turns):
            turn_num = i + 1
            if i < len(turns) - max_turns:
                # Dropped
                st.markdown(f"~~Turn {turn_num}~~ ❌ (dropped)")
            else:
                # Kept
                st.markdown(f"**Turn {turn_num}** ✅ (in memory)")
