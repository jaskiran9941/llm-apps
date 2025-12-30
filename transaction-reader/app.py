"""Streamlit UI for Transaction Reader Agent."""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from datetime import datetime
from agent import TransactionReaderAgent
from gmail_helper import get_gmail_service, get_account_email, list_configured_accounts

# Page config
st.set_page_config(
    page_title="Transaction Reader",
    page_icon="💳",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">💳 Transaction Reader</h1>', unsafe_allow_html=True)
st.markdown("**AI-powered Gmail purchase analyzer**")

# Sidebar
with st.sidebar:
    st.header("📧 Email Accounts")

    # List configured accounts
    accounts = list_configured_accounts()

    if accounts:
        st.success(f"✓ {len(accounts)} account(s) configured")

        # Show configured accounts with email addresses
        if 'account_emails' not in st.session_state:
            st.session_state.account_emails = {}

        for account in accounts:
            if account not in st.session_state.account_emails:
                try:
                    service = get_gmail_service(account)
                    email = get_account_email(service)
                    st.session_state.account_emails[account] = email
                except:
                    st.session_state.account_emails[account] = account

        # Account selection
        selected_accounts = st.multiselect(
            "Select accounts to analyze:",
            accounts,
            default=accounts,
            format_func=lambda x: st.session_state.account_emails.get(x, x)
        )
    else:
        st.info("No accounts configured yet")
        selected_accounts = []

    # Add new account
    st.markdown("---")
    with st.expander("➕ Add New Account"):
        account_name = st.text_input("Account nickname (e.g., 'personal', 'work')")

        if st.button("Authenticate New Account"):
            if account_name:
                try:
                    with st.spinner(f"Authenticating {account_name}..."):
                        service = get_gmail_service(account_name)
                        email = get_account_email(service)
                        st.success(f"✓ Added {email}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
            else:
                st.warning("Please enter an account nickname")

    st.markdown("---")
    st.header("⚙️ Settings")
    max_emails = st.slider("Max emails to fetch", 10, 200, 50)
    days_back = st.slider("Days to look back", 7, 90, 30)

    st.markdown("---")
    st.markdown("### About")
    st.info("This app analyzes your Gmail for purchases and provides spending insights using AI.")

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'agent_run' not in st.session_state:
    st.session_state.agent_run = False

# Main content
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "🔍 Analyze", "📝 Transactions"])

# Tab 2: Analyze (put first so users start here)
with tab2:
    st.header("Analyze Your Purchases")
    st.write("Click the button below to fetch and analyze your Gmail purchases.")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            if not selected_accounts:
                st.warning("⚠️ Please select at least one email account to analyze")
            else:
                with st.spinner("Fetching and analyzing emails... This may take a minute."):
                    try:
                        # Run the agent
                        agent = TransactionReaderAgent()

                        # Fetch emails from selected accounts
                        if len(selected_accounts) == 1:
                            # Single account
                            emails = agent.fetch_emails(
                                max_results=max_emails,
                                days_back=days_back,
                                account_name=selected_accounts[0]
                            )
                        else:
                            # Multiple accounts
                            emails = agent.fetch_emails_from_accounts(
                                account_names=selected_accounts,
                                max_results=max_emails,
                                days_back=days_back
                            )

                        st.info(f"✓ Fetched {len(emails)} emails from {len(selected_accounts)} account(s)")

                        if emails:
                            agent.analyze_emails_for_purchases(emails)
                            st.info(f"✓ Found {len(agent.transactions)} purchases")

                            if agent.transactions:
                                analysis = agent.categorize_and_analyze()

                                # Store in session state
                                st.session_state.transactions = agent.transactions
                                st.session_state.analysis = analysis
                                st.session_state.agent_run = True

                                st.success("✅ Analysis complete! Check the Dashboard and Transactions tabs.")
                            else:
                                st.warning("No purchases found in the analyzed emails.")
                        else:
                            st.warning("No emails found.")

                    except Exception as e:
                        st.error(f"Error running analysis: {e}")

    # Show existing data if available
    if st.session_state.agent_run:
        st.markdown("---")
        st.subheader("📈 Latest Analysis")
        st.markdown(st.session_state.analysis)

# Tab 1: Dashboard
with tab1:
    if not st.session_state.transactions:
        st.info("👈 Click 'Analyze' tab to fetch your transactions first!")
    else:
        transactions = st.session_state.transactions
        df = pd.DataFrame(transactions)

        # Convert amount to float
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        # Metrics row
        st.subheader("📊 Overview")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_spent = df['amount'].sum()
            st.metric("Total Spent", f"${total_spent:.2f}")

        with col2:
            num_transactions = len(df)
            st.metric("Transactions", num_transactions)

        with col3:
            avg_transaction = df['amount'].mean()
            st.metric("Avg Transaction", f"${avg_transaction:.2f}")

        with col4:
            num_merchants = df['merchant'].nunique()
            st.metric("Merchants", num_merchants)

        st.markdown("---")

        # Charts row
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💰 Spending by Category")
            category_spend = df.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(category_spend, values='amount', names='category',
                        title='Spending Distribution')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("🏪 Top Merchants")
            merchant_spend = df.groupby('merchant')['amount'].sum().reset_index()
            merchant_spend = merchant_spend.sort_values('amount', ascending=False).head(10)
            fig = px.bar(merchant_spend, x='merchant', y='amount',
                        title='Top 10 Merchants by Spending')
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Timeline
        st.subheader("📅 Spending Over Time")
        df['date'] = pd.to_datetime(df['date'])
        daily_spend = df.groupby('date')['amount'].sum().reset_index()
        fig = px.line(daily_spend, x='date', y='amount',
                     title='Daily Spending Trend',
                     labels={'amount': 'Amount ($)', 'date': 'Date'})
        st.plotly_chart(fig, use_container_width=True)

# Tab 3: Transactions
with tab3:
    st.header("Transaction Details")

    if not st.session_state.transactions:
        st.info("👈 Click 'Analyze' tab to fetch your transactions first!")
    else:
        df = pd.DataFrame(st.session_state.transactions)
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')

        # Filters
        col1, col2 = st.columns(2)
        with col1:
            categories = ['All'] + sorted(df['category'].unique().tolist())
            selected_category = st.selectbox("Filter by Category", categories)

        with col2:
            merchants = ['All'] + sorted(df['merchant'].unique().tolist())
            selected_merchant = st.selectbox("Filter by Merchant", merchants)

        # Apply filters
        filtered_df = df.copy()
        if selected_category != 'All':
            filtered_df = filtered_df[filtered_df['category'] == selected_category]
        if selected_merchant != 'All':
            filtered_df = filtered_df[filtered_df['merchant'] == selected_merchant]

        # Display table
        st.dataframe(
            filtered_df[['date', 'merchant', 'amount', 'currency', 'category', 'items']],
            use_container_width=True,
            hide_index=True
        )

        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv"
        )

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Claude AI & Streamlit")
