import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from typing import Dict, List

# Configure the page
st.set_page_config(
    page_title="CryptoGeezas Investment Club",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for dark mode
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Data files
DATA_DIR = "data"
CONTRIBUTIONS_FILE = os.path.join(DATA_DIR, "contributions.json")
TRANSACTIONS_FILE = os.path.join(DATA_DIR, "transactions.json")
PORTFOLIO_FILE = os.path.join(DATA_DIR, "portfolio.json")

# Club members
MEMBERS = ["Charles", "Ross Parmenter", "Jayden Kenna", "Brad Johnson"]
WEEKLY_CONTRIBUTION = 50  # AUD

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def apply_custom_css():
    """Apply custom CSS for dark/light mode"""
    if st.session_state.dark_mode:
        # Dark mode styles
        st.markdown("""
        <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .main-header {
            background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.3);
        }
        .metric-card {
            background: linear-gradient(135deg, #1E293B 0%, #334155 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #475569;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
            text-align: center;
            margin-bottom: 1rem;
        }
        .crypto-card {
            background: linear-gradient(135deg, #065F46 0%, #047857 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #10B981;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
            text-align: center;
            margin-bottom: 1rem;
        }
        .member-card {
            background: linear-gradient(135deg, #7C2D12 0%, #DC2626 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #EF4444;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 10px rgba(239, 68, 68, 0.2);
        }
        .success-card {
            background: linear-gradient(135deg, #14532D 0%, #16A34A 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #22C55E;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # Light mode styles
        st.markdown("""
        <style>
        .stApp {
            background-color: #FFFFFF;
            color: #1F2937;
        }
        .main-header {
            background: linear-gradient(90deg, #3B82F6 0%, #06B6D4 50%, #10B981 100%);
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
        }
        .metric-card {
            background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #CBD5E1;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            margin-bottom: 1rem;
        }
        .crypto-card {
            background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%);
            padding: 1.5rem;
            border-radius: 12px;
            border: 1px solid #10B981;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.1);
            text-align: center;
            margin-bottom: 1rem;
        }
        .member-card {
            background: linear-gradient(135deg, #FEF2F2 0%, #FECACA 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #F87171;
            margin-bottom: 0.5rem;
            box-shadow: 0 2px 10px rgba(248, 113, 113, 0.1);
        }
        .success-card {
            background: linear-gradient(135deg, #F0FDF4 0%, #BBFFA3 100%);
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #22C55E;
            margin: 1rem 0;
        }
        </style>
        """, unsafe_allow_html=True)

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
        st.error(f"❌ Failed to fetch crypto prices: {e}")
        return {"BTC": 97500, "ETH": 5250}

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

def calculate_portfolio_value(portfolio: Dict[str, float], prices: Dict[str, float]) -> float:
    """Calculate total portfolio value"""
    total_value = 0
    for crypto, amount in portfolio.items():
        if amount > 0 and crypto in prices:
            total_value += amount * prices[crypto]
    return total_value

def main():
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize data files
    init_data_files()
    
    # Header with logo and dark mode toggle
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="main-header">
            <h1 style="color: white; margin: 0; font-size: 3rem;">🚀 CryptoGeezas</h1>
            <p style="color: #E5E7EB; margin: 0.5rem 0 0 0; font-size: 1.2rem;">Investment Club Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 🌙")
        dark_mode = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            st.rerun()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 📱 Navigation")
        page = st.radio(
            "Choose a section:",
            ["🧾 Dashboard", "➕ Add Contributions", "🛒 Record Purchases"],
            label_visibility="collapsed"
        )
    
    # Get current data
    prices = get_crypto_prices()
    portfolio = load_json(PORTFOLIO_FILE)
    contributions = load_json(CONTRIBUTIONS_FILE)
    transactions = load_json(TRANSACTIONS_FILE)
    
    # Route to appropriate page
    if page == "🧾 Dashboard":
        show_dashboard(prices, portfolio, contributions, transactions)
    elif page == "➕ Add Contributions":
        show_add_contributions()
    elif page == "🛒 Record Purchases":
        show_record_purchases(prices)

def show_dashboard(prices, portfolio, contributions, transactions):
    """Main dashboard view"""
    
    # Calculate key metrics
    portfolio_value = calculate_portfolio_value(portfolio, prices)
    total_contributions = calculate_total_contributions()
    ownership_percentages = calculate_ownership_percentages()
    total_invested = sum(total_contributions.values())
    gain_loss = portfolio_value - total_invested
    gain_loss_pct = (gain_loss / total_invested * 100) if total_invested > 0 else 0
    
    # Top metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #3B82F6;">💰 Portfolio Value</h3>
            <h2 style="margin: 0.5rem 0;">${portfolio_value:,.2f} AUD</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: #10B981;">📈 Total Invested</h3>
            <h2 style="margin: 0.5rem 0;">${total_invested:,.2f} AUD</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        gain_color = "#22C55E" if gain_loss >= 0 else "#EF4444"
        gain_icon = "📈" if gain_loss >= 0 else "📉"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="margin: 0; color: {gain_color};">{gain_icon} Gain/Loss</h3>
            <h2 style="margin: 0.5rem 0; color: {gain_color};">${gain_loss:,.2f} AUD</h2>
            <p style="margin: 0; color: {gain_color};">({gain_loss_pct:+.1f}%)</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current crypto prices
    st.markdown("### 💱 Live Crypto Prices")
    
    col1, col2 = st.columns(2)
    with col1:
        btc_change = "📈" if prices["BTC"] > 95000 else "📉"  # Rough baseline
        st.markdown(f"""
        <div class="crypto-card">
            <h3 style="margin: 0; color: #F7931A;">{btc_change} Bitcoin (BTC)</h3>
            <h2 style="margin: 0.5rem 0;">${prices['BTC']:,.0f} AUD</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        eth_change = "📈" if prices["ETH"] > 5000 else "📉"  # Rough baseline
        st.markdown(f"""
        <div class="crypto-card">
            <h3 style="margin: 0; color: #627EEA;">{eth_change} Ethereum (ETH)</h3>
            <h2 style="margin: 0.5rem 0;">${prices['ETH']:,.0f} AUD</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Portfolio composition
    if portfolio_value > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥧 Portfolio Breakdown")
            crypto_values = {}
            for crypto, amount in portfolio.items():
                if amount > 0 and crypto in prices:
                    crypto_values[crypto] = amount * prices[crypto]
            
            if crypto_values:
                fig = px.pie(
                    values=list(crypto_values.values()),
                    names=list(crypto_values.keys()),
                    title="Holdings by Cryptocurrency",
                    color_discrete_sequence=["#F7931A", "#627EEA", "#06B6D4", "#10B981"]
                )
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    font_size=14
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### 👥 Member Equity Share")
            if any(ownership_percentages.values()):
                fig = px.pie(
                    values=list(ownership_percentages.values()),
                    names=list(ownership_percentages.keys()),
                    title="Ownership Distribution",
                    color_discrete_sequence=["#EF4444", "#F59E0B", "#10B981", "#3B82F6"]
                )
                fig.update_layout(
                    showlegend=True,
                    height=400,
                    font_size=14
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # Member details
    st.markdown("### 👥 Member Details")
    for member in MEMBERS:
        total_contrib = total_contributions.get(member, 0)
        ownership_pct = ownership_percentages.get(member, 0)
        portfolio_share = (ownership_pct / 100) * portfolio_value if portfolio_value > 0 else 0
        
        st.markdown(f"""
        <div class="member-card">
            <h4 style="margin: 0; color: white;">{member}</h4>
            <p style="margin: 0.2rem 0; color: #FCA5A5;">
                💰 Contributed: ${total_contrib:,.0f} AUD | 
                📊 Owns: {ownership_pct:.1f}% | 
                💎 Value: ${portfolio_share:,.0f} AUD
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    if transactions:
        st.markdown("### 📋 Recent Activity")
        recent_transactions = sorted(transactions, key=lambda x: x["timestamp"], reverse=True)[:3]
        
        for tx in recent_transactions:
            date = datetime.fromisoformat(tx["timestamp"]).strftime("%b %d, %Y")
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.1); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.5rem; border-left: 4px solid #3B82F6;">
                🛒 Bought {tx['amount']:.6f} {tx['crypto']} for ${tx['total_cost']:,.0f} AUD on {date}
            </div>
            """, unsafe_allow_html=True)

def show_add_contributions():
    """Add weekly contributions page"""
    
    st.markdown("### ➕ Weekly Contributions")
    st.markdown("Add $50 AUD weekly contributions for each member")
    
    # Quick add all members
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💰 Add $50 for All Members", type="primary", use_container_width=True):
            contributions = load_json(CONTRIBUTIONS_FILE)
            timestamp = datetime.now().isoformat()
            
            for member in MEMBERS:
                if member not in contributions:
                    contributions[member] = []
                
                contributions[member].append({
                    "amount": 50.0,
                    "date": timestamp,
                    "timestamp": timestamp
                })
            
            save_json(CONTRIBUTIONS_FILE, contributions)
            
            st.markdown("""
            <div class="success-card">
                <h4 style="margin: 0; color: white;">✅ Success!</h4>
                <p style="margin: 0.5rem 0 0 0; color: #BBF7D0;">Added $50 AUD contribution for all members!</p>
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
    
    st.markdown("---")
    
    # Individual member contributions
    st.markdown("### 👤 Individual Contributions")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_member = st.selectbox("Select Member", MEMBERS)
        contribution_amount = st.number_input("Amount (AUD)", min_value=0.01, value=50.0, step=0.01)
    
    with col2:
        contribution_date = st.date_input("Date", datetime.now())
        st.markdown("")  # Spacing
        if st.button("Add Contribution", type="secondary", use_container_width=True):
            contributions = load_json(CONTRIBUTIONS_FILE)
            
            if selected_member not in contributions:
                contributions[selected_member] = []
            
            contributions[selected_member].append({
                "amount": contribution_amount,
                "date": contribution_date.isoformat(),
                "timestamp": datetime.now().isoformat()
            })
            
            save_json(CONTRIBUTIONS_FILE, contributions)
            st.success(f"Added ${contribution_amount} AUD for {selected_member}!")
            st.rerun()
    
    # Show recent contributions
    contributions = load_json(CONTRIBUTIONS_FILE)
    all_contributions = []
    for member, member_contribs in contributions.items():
        for contrib in member_contribs[-3:]:  # Last 3 per member
            all_contributions.append({
                "Member": member,
                "Amount": f"${contrib['amount']:.0f} AUD",
                "Date": datetime.fromisoformat(contrib["date"]).strftime("%b %d, %Y")
            })
    
    if all_contributions:
        st.markdown("### 📊 Recent Contributions")
        df = pd.DataFrame(sorted(all_contributions, key=lambda x: x["Date"], reverse=True)[:6])
        st.dataframe(df, use_container_width=True, hide_index=True)

def show_record_purchases(prices):
    """Record crypto purchases page"""
    
    st.markdown("### 🛒 Record Crypto Purchase")
    
    # Available balance
    total_contributions = sum(calculate_total_contributions().values())
    transactions = load_json(TRANSACTIONS_FILE)
    total_spent = sum(t["total_cost"] for t in transactions)
    available_balance = total_contributions - total_spent
    
    st.markdown(f"""
    <div class="metric-card">
        <h3 style="margin: 0; color: #10B981;">💳 Available Balance</h3>
        <h2 style="margin: 0.5rem 0;">${available_balance:,.2f} AUD</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if available_balance <= 0:
        st.warning("⚠️ No available balance. Add contributions first!")
        return
    
    # Purchase form
    col1, col2 = st.columns(2)
    
    with col1:
        # Crypto selection
        crypto_options = ["BTC", "ETH", "Other"]
        selected_crypto = st.selectbox("Cryptocurrency", crypto_options)
        
        if selected_crypto == "Other":
            custom_crypto = st.text_input("Custom Symbol (e.g., ADA)", max_chars=10)
            crypto_symbol = custom_crypto.upper() if custom_crypto else ""
        else:
            crypto_symbol = selected_crypto
        
        # Show current price
        if crypto_symbol in prices:
            st.info(f"💱 Current {crypto_symbol}: ${prices[crypto_symbol]:,.0f} AUD")
        
        # Amount of crypto
        crypto_amount = st.number_input(
            f"Amount of {crypto_symbol or 'crypto'}",
            min_value=0.000001,
            value=0.001,
            step=0.000001,
            format="%.6f"
        )
    
    with col2:
        # Price and fees
        price_per_unit = st.number_input(
            f"Price per {crypto_symbol or 'unit'} (AUD)",
            min_value=0.01,
            value=float(prices.get(crypto_symbol, 100.0)),
            step=0.01
        )
        
        transaction_fee = st.number_input(
            "Transaction Fee (AUD)",
            min_value=0.0,
            value=0.0,
            step=0.01
        )
        
        # Calculate total
        subtotal = crypto_amount * price_per_unit
        total_cost = subtotal + transaction_fee
        
        st.markdown(f"""
        **Subtotal:** ${subtotal:.2f} AUD  
        **Fee:** ${transaction_fee:.2f} AUD  
        **Total:** ${total_cost:.2f} AUD
        """)
    
    # Purchase date and notes
    purchase_date = st.date_input("Purchase Date", datetime.now())
    notes = st.text_area("Notes (optional)", placeholder="Exchange used, strategy, etc...")
    
    # Validation and record button
    can_purchase = (
        crypto_symbol and 
        crypto_amount > 0 and 
        price_per_unit > 0 and 
        total_cost <= available_balance
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Record Purchase", type="primary", disabled=not can_purchase, use_container_width=True):
            # Record the transaction
            transactions = load_json(TRANSACTIONS_FILE)
            portfolio = load_json(PORTFOLIO_FILE)
            
            transaction = {
                "crypto": crypto_symbol,
                "amount": crypto_amount,
                "price": price_per_unit,
                "transaction_fee": transaction_fee,
                "total_cost": total_cost,
                "type": "buy",
                "date": purchase_date.isoformat(),
                "notes": notes,
                "timestamp": datetime.now().isoformat()
            }
            
            transactions.append(transaction)
            
            # Update portfolio
            if crypto_symbol not in portfolio:
                portfolio[crypto_symbol] = 0
            portfolio[crypto_symbol] += crypto_amount
            
            save_json(TRANSACTIONS_FILE, transactions)
            save_json(PORTFOLIO_FILE, portfolio)
            
            st.markdown(f"""
            <div class="success-card">
                <h4 style="margin: 0; color: white;">🎉 Purchase Recorded!</h4>
                <p style="margin: 0.5rem 0 0 0; color: #BBF7D0;">
                    Bought {crypto_amount:.6f} {crypto_symbol} for ${total_cost:.2f} AUD
                </p>
            </div>
            """, unsafe_allow_html=True)
            st.rerun()
    
    if not can_purchase:
        if not crypto_symbol:
            st.error("❌ Please select a cryptocurrency")
        elif crypto_amount <= 0:
            st.error("❌ Amount must be greater than 0")
        elif total_cost > available_balance:
            st.error(f"❌ Total cost exceeds available balance")

if __name__ == "__main__":
    main()
