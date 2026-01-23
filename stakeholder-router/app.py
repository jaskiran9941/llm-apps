"""Streamlit UI for Stakeholder Router."""
import json
import os
from pathlib import Path

import streamlit as st
import structlog

# Configure structlog for Streamlit
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]
)

from src.router.orchestrator import RoutingOrchestrator
from src.config.settings import router_settings

# Page configuration
st.set_page_config(
    page_title="Stakeholder Router",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "routing_history" not in st.session_state:
    st.session_state.routing_history = []


def load_example_queries():
    """Load example queries from JSON file."""
    examples_path = Path(__file__).parent / "examples" / "test_queries.json"
    if examples_path.exists():
        with open(examples_path) as f:
            return json.load(f)
    return {}


def load_sabotage_scenarios():
    """Load sabotage scenarios from JSON file."""
    scenarios_path = Path(__file__).parent / "examples" / "sabotage_scenarios.json"
    if scenarios_path.exists():
        with open(scenarios_path) as f:
            return json.load(f)
    return {}


def render_classification_card(classification):
    """Render classification result as a card."""
    # Color based on category
    category_colors = {
        "pricing": "🔵",
        "ux": "🟢",
        "ambiguous": "🟡",
        "ood": "🔴",
    }

    icon = category_colors.get(classification.category, "⚪")

    st.markdown(f"### {icon} Classification Result")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Category", classification.category.upper())
        st.metric("Confidence", f"{classification.confidence:.2%}")

    with col2:
        st.markdown("**Reasoning:**")
        st.info(classification.reasoning)

    if classification.clarifying_questions:
        st.markdown("**Clarifying Questions:**")
        for i, q in enumerate(classification.clarifying_questions, 1):
            st.markdown(f"{i}. {q}")


def render_expert_response(expert_response, index=0):
    """Render expert response."""
    # Different colors for different experts
    expert_colors = {
        "Pricing Expert": "blue",
        "UX Expert": "green",
    }

    color = expert_colors.get(expert_response.expert_name, "gray")

    with st.container():
        st.markdown(f"### {expert_response.expert_name}")
        st.markdown(f"**Confidence:** {expert_response.confidence:.2%}")
        st.markdown(expert_response.response)

        if expert_response.sources:
            st.caption(f"Sources mentioned: {', '.join(expert_response.sources)}")


def render_routing_result(result):
    """Render complete routing result."""
    st.markdown("---")

    # Classification
    with st.expander("📊 Classification Details", expanded=True):
        render_classification_card(result.classification)

    # OOD Detection
    if result.ood_result:
        with st.expander("🛡️ OOD Detection", expanded=result.ood_result.is_ood):
            if result.ood_result.is_ood:
                st.error(f"**OOD Detected:** {result.ood_result.ood_category}")
                st.info(result.ood_result.reasoning)
            else:
                st.success("Query passed OOD detection")

    # Ambiguity Resolution
    if result.ambiguity_resolution:
        with st.expander("🔀 Ambiguity Handling", expanded=True):
            st.markdown(f"**Strategy:** {result.ambiguity_resolution.strategy}")
            st.markdown(f"**Reasoning:** {result.ambiguity_resolution.reasoning}")
            if result.ambiguity_resolution.target_experts:
                st.markdown(
                    f"**Routing to:** {', '.join(result.ambiguity_resolution.target_experts)}"
                )

    # Expert Responses
    if result.expert_responses:
        st.markdown("### 🎓 Expert Responses")

        if len(result.expert_responses) == 1:
            render_expert_response(result.expert_responses[0])
        else:
            # Side-by-side comparison
            cols = st.columns(len(result.expert_responses))
            for i, expert_response in enumerate(result.expert_responses):
                with cols[i]:
                    render_expert_response(expert_response, i)

    # Final Response
    st.markdown("### 📝 Final Response")
    st.markdown(result.final_response)

    # Debug Info
    with st.expander("🔍 Debug Info (JSON)", expanded=False):
        st.json(result.to_dict())


def main():
    """Main Streamlit app."""
    st.title("🎯 Stakeholder Router")
    st.markdown(
        "Advanced AI routing with guardrails, ambiguity handling, and OOD detection"
    )

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Check for API key
        api_key_configured = os.getenv("ANTHROPIC_API_KEY") is not None
        if api_key_configured:
            st.success("✅ API Key Configured")
        else:
            st.error("❌ API Key Missing")
            st.info("Set ANTHROPIC_API_KEY in your .env file")

        st.markdown("---")

        # Routing Strategy
        st.subheader("Routing Strategy")
        ambiguity_strategy = st.selectbox(
            "Ambiguity Handling",
            options=["ask_clarifying", "route_both", "pick_primary"],
            index=0,
            help="How to handle ambiguous queries",
        )

        # OOD Detection
        enable_ood = st.checkbox(
            "Enable OOD Detection",
            value=True,
            help="Pre-filter out-of-distribution queries",
        )

        # Confidence Thresholds
        st.subheader("Confidence Thresholds")
        threshold_high = st.slider(
            "High Confidence",
            min_value=0.5,
            max_value=1.0,
            value=0.8,
            step=0.05,
            help="Threshold for high-confidence routing",
        )

        threshold_low = st.slider(
            "Low Confidence",
            min_value=0.0,
            max_value=0.8,
            value=0.5,
            step=0.05,
            help="Below this, treat as ambiguous",
        )

        st.markdown("---")

        # Example Queries
        st.subheader("📚 Example Queries")

        examples = load_example_queries()

        if examples:
            example_category = st.selectbox(
                "Category",
                options=[
                    "clear_pricing_queries",
                    "clear_ux_queries",
                    "ambiguous_queries",
                    "ood_queries",
                    "edge_cases",
                ],
                format_func=lambda x: x.replace("_", " ").title(),
            )

            if example_category in examples:
                example_queries = examples[example_category]
                selected_example = st.selectbox(
                    "Select Example",
                    options=range(len(example_queries)),
                    format_func=lambda i: example_queries[i]["query"][:60] + "...",
                )

                if st.button("Load Example"):
                    st.session_state.example_query = example_queries[selected_example][
                        "query"
                    ]

        st.markdown("---")

        # Stats
        st.subheader("📊 Session Stats")
        st.metric("Queries Processed", len(st.session_state.routing_history))

        if st.session_state.routing_history:
            categories = [r.classification.category for r in st.session_state.routing_history if r.classification]
            if categories:
                from collections import Counter

                category_counts = Counter(categories)
                for cat, count in category_counts.items():
                    st.metric(cat.upper(), count)

        if st.button("Clear History"):
            st.session_state.messages = []
            st.session_state.routing_history = []
            st.rerun()

    # Main Content Area
    if not api_key_configured:
        st.warning(
            "⚠️ Please configure your ANTHROPIC_API_KEY in the .env file to use the router."
        )
        st.code("ANTHROPIC_API_KEY=your_api_key_here", language="bash")
        return

    # Initialize orchestrator with current settings
    orchestrator = RoutingOrchestrator(
        enable_ood_detection=enable_ood,
        ambiguity_strategy=ambiguity_strategy,
        confidence_threshold_high=threshold_high,
        confidence_threshold_low=threshold_low,
    )

    # Chat Interface
    st.markdown("### 💬 Chat Interface")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    query = st.chat_input("Ask about pricing or UX...")

    # Handle example query from sidebar
    if "example_query" in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query

    if query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})

        with st.chat_message("user"):
            st.markdown(query)

        # Process query
        with st.chat_message("assistant"):
            with st.spinner("Routing your query..."):
                try:
                    result = orchestrator.route_query(
                        query=query,
                        ambiguity_strategy_override=ambiguity_strategy,
                    )

                    # Store in history
                    st.session_state.routing_history.append(result)

                    # Render result
                    render_routing_result(result)

                    # Add assistant message
                    st.session_state.messages.append(
                        {"role": "assistant", "content": result.final_response}
                    )

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")
                    st.exception(e)

    # Tabs for additional views
    tab1, tab2, tab3 = st.tabs(["💡 About", "🧪 Test Scenarios", "📈 Analytics"])

    with tab1:
        st.markdown("""
        ## About Stakeholder Router

        This system demonstrates advanced AI routing with:

        - **JSON Classification**: Structured output for reliable categorization
        - **OOD Detection**: Guardrails to reject inappropriate queries
        - **Ambiguity Handling**: Multiple strategies for handling unclear queries
        - **Expert Sub-Agents**: Domain-specific experts (Pricing & UX)
        - **Transparent Routing**: Observable AI decision-making

        ### Routing Flow

        1. **OOD Detection**: Pre-filter inappropriate queries
        2. **Classification**: Categorize as pricing/UX/ambiguous/OOD
        3. **Ambiguity Handling**: Based on selected strategy
        4. **Expert Routing**: Send to appropriate expert(s)
        5. **Response Aggregation**: Combine and present results

        ### Ambiguity Strategies

        - **Ask Clarifying**: Present questions to disambiguate
        - **Route Both**: Send to both experts, compare perspectives
        - **Pick Primary**: Use heuristics to choose most likely expert
        """)

    with tab2:
        st.markdown("## 🧪 Test Scenarios")

        scenarios = load_sabotage_scenarios()

        if scenarios and "scenarios" in scenarios:
            for scenario_group in scenarios["scenarios"]:
                st.subheader(scenario_group["category"].replace("_", " ").title())
                st.markdown(scenario_group["description"])

                if "tests" in scenario_group:
                    for test in scenario_group["tests"]:
                        with st.expander(test["query"][:80] + "..."):
                            st.markdown(f"**Query:** {test['query']}")
                            st.markdown(f"**Expected:** {test.get('expected_behavior', 'N/A')}")

                            if "success_criteria" in test:
                                st.markdown("**Success Criteria:**")
                                for criterion in test["success_criteria"]:
                                    st.markdown(f"- {criterion}")

                            if st.button(f"Test This Query", key=test["query"]):
                                st.session_state.example_query = test["query"]
                                st.rerun()

    with tab3:
        st.markdown("## 📈 Analytics")

        if st.session_state.routing_history:
            import pandas as pd

            # Create DataFrame from history
            data = []
            for result in st.session_state.routing_history:
                if result.classification:
                    data.append(
                        {
                            "Query": result.query[:50] + "...",
                            "Category": result.classification.category,
                            "Confidence": result.classification.confidence,
                            "Routed To": ", ".join(
                                result.metadata.get("routed_to", ["none"])
                            ),
                            "Rejected": result.metadata.get("rejected", False),
                        }
                    )

            if data:
                df = pd.DataFrame(data)

                st.markdown("### Query History")
                st.dataframe(df, use_container_width=True)

                st.markdown("### Confidence Distribution")
                st.bar_chart(df["Confidence"])

        else:
            st.info("No queries processed yet. Start chatting to see analytics!")


if __name__ == "__main__":
    main()
