import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from typing import Dict, List, Tuple

# Import custom utilities
try:
    from utils import (
        calculate_weekly_performance, 
        create_portfolio_trend_chart,
        create_contribution_heatmap,
        calculate_roi_by_crypto,
        get_contribution_streak,
        export_data_to_csv,
        generate_weekly_summary_report
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

# Configure the page
st.set_page_config(
    page_title="Cryptogeezas Investment Club",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize data files
DATA_DIR = "data"
CONTRIBUTIONS_FILE = os.path.join(DATA_DIR, "contributions.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")

# Club members
MEMBERS = ["Charles", "Ross Parmenter", "Jayden Kenna", "Brad Johnson"]
WEEKLY_CONTRIBUTION = 75  # AUD per member per week

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def init_data_files():
    """Initialize data files if they don't exist"""
    if not os.path.exists(CONTRIBUTIONS_FILE):
        initial_contributions = {member: [] for member in MEMBERS}
        save_json(CONTRIBUTIONS_FILE, initial_contributions)
    
    if not os.path.exists(TRANSACTIONS_FILE):
        save_json(TRANSACTIONS_FILE, [])
    
    if not os.path.exists(PORTFOLIO_FILE):
        initial_portfolio = {"BTC": 0, "ETH": 0}
        save_json(PORTFOLIO_FILE, initial_portfolio)

def load_json(file_path: str) -> dict:
    """Load JSON data from file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path: str, data):
    """Save data to JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2, default=str)

def get_crypto_prices() -> Dict[str, float]:
    """Fetch current crypto prices from CoinGecko API in AUD"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=aud"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return {
            "BTC": data["bitcoin"]["aud"],
            "ETH": data["ethereum"]["aud"]
        }
    except Exception as e:
        st.error(f"Failed to fetch crypto prices: {e}")
        # Return fallback prices in AUD
        return {"BTC": 97500, "ETH": 5250}

def calculate_portfolio_value(portfolio: Dict[str, float], prices: Dict[str, float]) -> float:
    """Calculate total portfolio value"""
    total_value = 0
    for crypto, amount in portfolio.items():
        if amount > 0:
            # Use the price if available, otherwise skip (or could use a fallback)
            crypto_price = prices.get(crypto, 0)
            total_value += amount * crypto_price
    return total_value

def calculate_total_contributions() -> Dict[str, float]:
    """Calculate total contributions by each member"""
    contributions = load_json(CONTRIBUTIONS_FILE)
    totals = {}
    for member in MEMBERS:
        member_contributions = contributions.get(member, [])
        totals[member] = sum(contrib["amount"] for contrib in member_contributions)
    return totals

def calculate_ownership_percentages() -> Dict[str, float]:
    """Calculate each member's ownership percentage based on contributions"""
    totals = calculate_total_contributions()
    total_pool = sum(totals.values())
    if total_pool == 0:
        return {member: 0 for member in MEMBERS}
    return {member: (amount / total_pool) * 100 for member, amount in totals.items()}

def add_contribution(member: str, amount: float, date: str = None):
    """Add a contribution for a member"""
    if date is None:
        date = datetime.now().isoformat()
    
    contributions = load_json(CONTRIBUTIONS_FILE)
    if member not in contributions:
        contributions[member] = []
    
    contributions[member].append({
        "amount": amount,
        "date": date,
        "timestamp": datetime.now().isoformat()
    })
    save_json(CONTRIBUTIONS_FILE, contributions)

def add_transaction(crypto: str, amount: float, price: float, transaction_fee: float = 0.0, transaction_type: str = "buy"):
    """Add a crypto transaction with optional transaction fee"""
    transactions = load_json(TRANSACTIONS_FILE)
    portfolio = load_json(PORTFOLIO_FILE)
    
    total_cost = (amount * price) + transaction_fee
    
    transaction = {
        "crypto": crypto,
        "amount": amount,
        "price": price,
        "transaction_fee": transaction_fee,
        "total_cost": total_cost,
        "type": transaction_type,
        "timestamp": datetime.now().isoformat()
    }
    
    transactions.append(transaction)
    
    # Update portfolio
    if transaction_type == "buy":
        portfolio[crypto] = portfolio.get(crypto, 0) + amount
    
    save_json(TRANSACTIONS_FILE, transactions)
    save_json(PORTFOLIO_FILE, portfolio)

def main():
    # Initialize data files
    init_data_files()
    
    # Title and header
    st.title("💰 Cryptogeezas Investment Club")
    st.markdown("---")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", [
        "Dashboard", 
        "Add Contributions", 
        "Buy Crypto", 
        "Transaction History", 
        "Member Details",
        "Analytics",
        "Weekly Summary"
    ])
    
    # Get current data
    prices = get_crypto_prices()
    portfolio = load_json(PORTFOLIO_FILE)
    contributions = load_json(CONTRIBUTIONS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    
    if page == "Dashboard":
        show_dashboard(prices, portfolio, contributions, transactions)
    elif page == "Add Contributions":
        show_contributions_page()
    elif page == "Buy Crypto":
        show_buy_crypto_page(prices)
    elif page == "Transaction History":
        show_transaction_history(transactions)
    elif page == "Member Details":
        show_member_details(contributions)
    elif page == "Analytics":
        show_analytics_page(prices, portfolio, contributions, transactions)
    elif page == "Weekly Summary":
        show_weekly_summary_page(prices, portfolio, contributions, transactions)

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Get password from Streamlit secrets
        try:
            correct_password = st.secrets["passwords"]["app_password"]
        except:
            correct_password = "cryptogeezas2025"  # Fallback password
            
        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input("🔐 Enter the club password to access Cryptogeezas Investment Tracker:", type="password", on_change=password_entered, key="password")
        st.info("💡 This is a private investment club tracker. Please contact Charles for access.")
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("🔐 Enter the club password to access Cryptogeezas Investment Tracker:", type="password", on_change=password_entered, key="password")
        st.error("� Password incorrect. Please check with your club members.")
        return False
    else:
        # Password correct.
        return True

# Add this right after apply_custom_css() in your main() function:
if not check_password():
    st.stop()

def show_dashboard(prices, portfolio, contributions, transactions):
    """Display the main dashboard"""
    st.header("📊 Portfolio Dashboard")
    
    # Calculate key metrics
    portfolio_value = calculate_portfolio_value(portfolio, prices)
    total_contributions = calculate_total_contributions()
    ownership_percentages = calculate_ownership_percentages()
    total_invested = sum(total_contributions.values())
    
    # Top metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Portfolio Value", f"${portfolio_value:,.2f} AUD")
    
    with col2:
        st.metric("Total Invested", f"${total_invested:,.2f} AUD")
    
    with col3:
        gain_loss = portfolio_value - total_invested
        st.metric("Gain/Loss", f"${gain_loss:,.2f} AUD", delta=f"{(gain_loss/total_invested*100) if total_invested > 0 else 0:.1f}%")
    
    with col4:
        st.metric("Weekly Contribution", f"${WEEKLY_CONTRIBUTION} AUD")
    
    st.markdown("---")
    
    # Current prices section
    st.subheader("💱 Current Crypto Prices")
    price_col1, price_col2 = st.columns(2)
    
    with price_col1:
        st.metric("Bitcoin (BTC)", f"${prices['BTC']:,.2f} AUD")
    
    with price_col2:
        st.metric("Ethereum (ETH)", f"${prices['ETH']:,.2f} AUD")
    
    # Portfolio composition
    if portfolio_value > 0:
        st.subheader("🥧 Portfolio Composition")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Crypto allocation pie chart
            crypto_values = {}
            for crypto, amount in portfolio.items():
                if amount > 0 and crypto in prices:
                    crypto_values[crypto] = amount * prices[crypto]
            
            if crypto_values:
                fig_crypto = px.pie(
                    values=list(crypto_values.values()),
                    names=list(crypto_values.keys()),
                    title="Portfolio by Cryptocurrency",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_crypto, use_container_width=True)
            else:
                st.info("Portfolio composition chart unavailable - crypto prices not found.")
        
        with col2:
            # Member ownership pie chart
            if any(ownership_percentages.values()):
                fig_ownership = px.pie(
                    values=list(ownership_percentages.values()),
                    names=list(ownership_percentages.keys()),
                    title="Ownership by Member (%)",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_ownership, use_container_width=True)
    
    # Holdings details
    st.subheader("💼 Current Holdings")
    holdings_data = []
    for crypto, amount in portfolio.items():
        if amount > 0:
            if crypto in prices:
                value = amount * prices[crypto]
                current_price = f"${prices[crypto]:,.2f} AUD"
                total_value = f"${value:,.2f} AUD"
            else:
                current_price = "Price not available"
                total_value = "Value not available"
            
            holdings_data.append({
                "Cryptocurrency": crypto,
                "Amount": f"{amount:.6f}",
                "Current Price": current_price,
                "Total Value": total_value
            })
    
    if holdings_data:
        st.dataframe(pd.DataFrame(holdings_data), use_container_width=True)
    else:
        st.info("No crypto holdings yet. Start by adding contributions and buying crypto!")
    
    # Member ownership breakdown
    st.subheader("👥 Member Ownership Breakdown")
    member_data = []
    for member in MEMBERS:
        total_contrib = total_contributions.get(member, 0)
        ownership_pct = ownership_percentages.get(member, 0)
        portfolio_share = (ownership_pct / 100) * portfolio_value if portfolio_value > 0 else 0
        
        member_data.append({
            "Member": member,
            "Total Contributions": f"${total_contrib:,.2f} AUD",
            "Ownership %": f"{ownership_pct:.1f}%",
            "Portfolio Value": f"${portfolio_share:,.2f} AUD"
        })
    
    st.dataframe(pd.DataFrame(member_data), use_container_width=True)

def show_contributions_page():
    """Page for adding weekly contributions"""
    st.header("💰 Add Weekly Contributions")
    
    # Quick add all members
    st.subheader("Quick Add - Weekly Contributions")
    if st.button("Add $50 AUD for All Members", type="primary"):
        for member in MEMBERS:
            add_contribution(member, 50.0)
        st.success(f"Added $50 AUD contribution for all members!")
        st.rerun()
    
    st.markdown("---")
    
    # Individual contributions
    st.subheader("Add Individual Contribution")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_member = st.selectbox("Select Member", MEMBERS)
        contribution_amount = st.number_input("Contribution Amount (AUD)", min_value=0.01, value=50.0, step=0.01)
    
    with col2:
        contribution_date = st.date_input("Contribution Date", datetime.now())
    
    if st.button("Add Contribution"):
        add_contribution(selected_member, contribution_amount, contribution_date.isoformat())
        st.success(f"Added ${contribution_amount} AUD contribution for {selected_member}!")
        st.rerun()

def show_buy_crypto_page(prices):
    """Page for buying cryptocurrency with manual input"""
    st.header("🛒 Buy Cryptocurrency")
    
    # Available balance
    total_contributions = sum(calculate_total_contributions().values())
    transactions = load_json(TRANSACTIONS_FILE)
    total_spent = sum(t["total_cost"] for t in transactions if t["type"] == "buy")
    available_balance = total_contributions - total_spent
    
    st.metric("Available Balance", f"${available_balance:,.2f} AUD")
    
    if available_balance <= 0:
        st.warning("No available balance for crypto purchases. Add more contributions first!")
        return
    
    st.markdown("---")
    
    # Manual transaction input form
    st.subheader("📝 Manual Transaction Entry")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Crypto selection with option to add custom
        crypto_options = ["BTC", "ETH", "Other"]
        selected_crypto = st.selectbox("Select Cryptocurrency", crypto_options)
        
        if selected_crypto == "Other":
            custom_crypto = st.text_input("Enter Crypto Symbol (e.g., ADA, SOL)", max_chars=10)
            crypto_to_buy = custom_crypto.upper() if custom_crypto else ""
        else:
            crypto_to_buy = selected_crypto
        
        # Show current price if available
        if crypto_to_buy in prices:
            st.info(f"Current {crypto_to_buy} price: ${prices[crypto_to_buy]:,.2f} AUD")
        
        # Amount of crypto purchased
        crypto_amount = st.number_input(
            f"Amount of {crypto_to_buy if crypto_to_buy else 'crypto'} purchased",
            min_value=0.000001,
            value=0.001,
            step=0.000001,
            format="%.6f"
        )
    
    with col2:
        # Price per unit
        price_per_unit = st.number_input(
            f"Price per {crypto_to_buy if crypto_to_buy else 'crypto'} (AUD)",
            min_value=0.01,
            value=float(prices.get(crypto_to_buy, 100.0)),
            step=0.01
        )
        
        # Transaction fee
        transaction_fee = st.number_input(
            "Transaction Fee (AUD)",
            min_value=0.0,
            value=0.0,
            step=0.01
        )
        
        # Calculate totals
        subtotal = crypto_amount * price_per_unit
        total_cost = subtotal + transaction_fee
        
        st.write(f"**Subtotal:** ${subtotal:.2f} AUD")
        st.write(f"**Transaction Fee:** ${transaction_fee:.2f} AUD")
        st.write(f"**Total Cost:** ${total_cost:.2f} AUD")
    
    # Transaction date
    transaction_date = st.date_input("Transaction Date", datetime.now())
    
    # Add notes field
    notes = st.text_area("Transaction Notes (optional)", placeholder="e.g., Bought on Binance, Used DCA strategy...")
    
    # Validation and purchase button
    st.markdown("---")
    
    # Validation checks
    validation_errors = []
    if not crypto_to_buy:
        validation_errors.append("Please select or enter a cryptocurrency")
    if crypto_amount <= 0:
        validation_errors.append("Crypto amount must be greater than 0")
    if price_per_unit <= 0:
        validation_errors.append("Price per unit must be greater than 0")
    if total_cost > available_balance:
        validation_errors.append(f"Total cost (${total_cost:.2f}) exceeds available balance (${available_balance:.2f})")
    
    if validation_errors:
        for error in validation_errors:
            st.error(f"❌ {error}")
    
    # Purchase button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Record Transaction", type="primary", disabled=bool(validation_errors)):
            # Add the transaction with custom date
            add_transaction_with_date(crypto_to_buy, crypto_amount, price_per_unit, transaction_fee, transaction_date.isoformat(), notes)
            st.success(f"✅ Successfully recorded purchase of {crypto_amount:.6f} {crypto_to_buy} for ${total_cost:.2f} AUD!")
            st.rerun()

def add_transaction_with_date(crypto: str, amount: float, price: float, transaction_fee: float, date: str, notes: str = ""):
    """Add a crypto transaction with custom date and notes"""
    transactions = load_json(TRANSACTIONS_FILE)
    portfolio = load_json(PORTFOLIO_FILE)
    
    total_cost = (amount * price) + transaction_fee
    
    transaction = {
        "crypto": crypto,
        "amount": amount,
        "price": price,
        "transaction_fee": transaction_fee,
        "total_cost": total_cost,
        "type": "buy",
        "date": date,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    transactions.append(transaction)
    
    # Update portfolio
    if crypto not in portfolio:
        portfolio[crypto] = 0
    portfolio[crypto] = portfolio.get(crypto, 0) + amount
    
    save_json(TRANSACTIONS_FILE, transactions)
    save_json(PORTFOLIO_FILE, portfolio)

def show_transaction_history(transactions):
    """Display transaction history"""
    st.header("📋 Transaction History")
    
    if not transactions:
        st.info("No transactions yet.")
        return
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(transactions)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp', ascending=False)
    
    # Format for display
    display_df = df.copy()
    
    # Use custom date if available, otherwise use timestamp
    if 'date' in display_df.columns:
        display_df['Display_Date'] = display_df.apply(
            lambda row: pd.to_datetime(row['date']).strftime('%Y-%m-%d') 
            if pd.notna(row.get('date')) else row['timestamp'].strftime('%Y-%m-%d %H:%M'), 
            axis=1
        )
    else:
        display_df['Display_Date'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
    
    display_df['Crypto'] = display_df['crypto']
    display_df['Amount'] = display_df['amount'].apply(lambda x: f"{x:.6f}")
    display_df['Price'] = display_df['price'].apply(lambda x: f"${x:,.2f} AUD")
    
    # Handle transaction fees (for backward compatibility)
    if 'transaction_fee' in display_df.columns:
        display_df['Fee'] = display_df['transaction_fee'].apply(lambda x: f"${x:.2f} AUD" if pd.notna(x) else "$0.00 AUD")
    else:
        display_df['Fee'] = "$0.00 AUD"
    
    display_df['Total Cost'] = display_df['total_cost'].apply(lambda x: f"${x:,.2f} AUD")
    display_df['Type'] = display_df['type'].str.title()
    
    # Handle notes (for backward compatibility)
    if 'notes' in display_df.columns:
        display_df['Notes'] = display_df['notes'].fillna('')
    else:
        display_df['Notes'] = ''
    
    # Select columns to display
    columns_to_show = ['Display_Date', 'Type', 'Crypto', 'Amount', 'Price', 'Fee', 'Total Cost']
    if any(display_df['Notes'] != ''):
        columns_to_show.append('Notes')
    
    # Display the table
    st.dataframe(
        display_df[columns_to_show],
        use_container_width=True,
        column_config={
            "Display_Date": "Date",
            "Notes": st.column_config.TextColumn("Notes", width="medium")
        }
    )

def show_member_details(contributions):
    """Show detailed member contribution history"""
    st.header("👥 Member Details")
    
    selected_member = st.selectbox("Select Member", MEMBERS)
    
    member_contributions = contributions.get(selected_member, [])
    
    if not member_contributions:
        st.info(f"No contributions recorded for {selected_member} yet.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(member_contributions)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date', ascending=False)
    
    # Summary metrics
    total_amount = df['amount'].sum()
    avg_contribution = df['amount'].mean()
    contribution_count = len(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Contributions", f"${total_amount:,.2f} AUD")
    with col2:
        st.metric("Average Contribution", f"${avg_contribution:.2f} AUD")
    with col3:
        st.metric("Number of Contributions", contribution_count)
    
    # Contribution history chart
    fig = px.line(
        df, 
        x='date', 
        y='amount',
        title=f"{selected_member}'s Contribution History",
        labels={'amount': 'Contribution Amount (AUD)', 'date': 'Date'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Contribution table
    st.subheader("Contribution History")
    display_df = df.copy()
    display_df['Date'] = display_df['date'].dt.strftime('%Y-%m-%d')
    display_df['Amount'] = display_df['amount'].apply(lambda x: f"${x:.2f} AUD")
    
    st.dataframe(
        display_df[['Date', 'Amount']],
        use_container_width=True
    )

def show_analytics_page(prices, portfolio, contributions, transactions):
    """Display advanced analytics and visualizations"""
    st.header("📈 Advanced Analytics")
    
    if not UTILS_AVAILABLE:
        st.error("Advanced analytics unavailable. Utils module not found.")
        return
    
    if not transactions:
        st.info("No transaction data available for analytics. Make some crypto purchases first!")
        return
    
    # Portfolio trend chart
    st.subheader("📊 Portfolio Value Trend")
    trend_chart = create_portfolio_trend_chart(transactions, prices)
    st.plotly_chart(trend_chart, use_container_width=True)
    
    # ROI by cryptocurrency
    st.subheader("💹 ROI by Cryptocurrency")
    roi_data = calculate_roi_by_crypto(transactions, prices)
    
    if roi_data:
        col1, col2 = st.columns(2)
        
        for i, (crypto, data) in enumerate(roi_data.items()):
            with col1 if i % 2 == 0 else col2:
                st.metric(
                    f"{crypto} ROI",
                    f"{data['roi_percentage']:+.1f}%",
                    f"${data['current_value'] - data['invested']:+,.2f} AUD"
                )
        
        # ROI comparison chart
        crypto_names = list(roi_data.keys())
        roi_percentages = [data['roi_percentage'] for data in roi_data.values()]
        
        fig = px.bar(
            x=crypto_names,
            y=roi_percentages,
            title="ROI Comparison by Cryptocurrency",
            labels={'x': 'Cryptocurrency', 'y': 'ROI (%)'},
            color=roi_percentages,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Contribution heatmap
    st.subheader("🔥 Contribution Heatmap")
    if contributions and any(contributions.values()):
        heatmap = create_contribution_heatmap(contributions)
        st.plotly_chart(heatmap, use_container_width=True)
    else:
        st.info("No contribution data available for heatmap.")
    
    # Member streaks
    st.subheader("🏆 Contribution Streaks")
    streak_data = []
    for member in MEMBERS:
        streak = get_contribution_streak(member, contributions)
        streak_data.append({"Member": member, "Current Streak": f"{streak} weeks"})
    
    st.dataframe(pd.DataFrame(streak_data), use_container_width=True)
    
    # Export data section
    st.subheader("💾 Export Data")
    if st.button("Export All Data to CSV"):
        contrib_csv, trans_csv, portfolio_csv = export_data_to_csv(contributions, transactions, portfolio)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                "📥 Contributions CSV",
                contrib_csv,
                "contributions.csv",
                "text/csv"
            )
        with col2:
            st.download_button(
                "📥 Transactions CSV", 
                trans_csv,
                "transactions.csv",
                "text/csv"
            )
        with col3:
            st.download_button(
                "📥 Portfolio CSV",
                portfolio_csv,
                "portfolio.csv", 
                "text/csv"
            )

def show_weekly_summary_page(prices, portfolio, contributions, transactions):
    """Display weekly summary and performance metrics"""
    st.header("📋 Weekly Summary")
    
    if not UTILS_AVAILABLE:
        st.error("Weekly summary unavailable. Utils module not found.")
        return
    
    # Generate and display weekly report
    if contributions and any(contributions.values()):
        report = generate_weekly_summary_report(contributions, transactions, portfolio, prices)
        st.markdown(report)
        
        # Download report button
        st.download_button(
            "📥 Download Weekly Report",
            report,
            f"weekly_report_{datetime.now().strftime('%Y%m%d')}.md",
            "text/markdown"
        )
        
        st.markdown("---")
        
        # Weekly performance metrics
        st.subheader("📈 Weekly Performance Metrics")
        performance = calculate_weekly_performance(contributions, transactions, prices)
        
        perf_data = []
        for member, perf in performance.items():        perf_data.append({
            "Member": member,
            "Contributions Added": f"${perf['contributions_added']:.2f} AUD",
            "Ownership Change": f"{perf['ownership_change']:+.1f}%",
            "Current Ownership": f"{perf['current_ownership']:.1f}%"
        })
        
        st.dataframe(pd.DataFrame(perf_data), use_container_width=True)
        
        # Performance change visualization
        members = list(performance.keys())
        ownership_changes = [perf['ownership_change'] for perf in performance.values()]
        
        fig = px.bar(
            x=members,
            y=ownership_changes,
            title="Weekly Ownership Change by Member",
            labels={'x': 'Member', 'y': 'Ownership Change (%)'},
            color=ownership_changes,
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("No data available for weekly summary. Add some contributions first!")

if __name__ == "__main__":
    main()
