"""
Enhanced utilities and helper functions for the Cryptogeezas Investment Club app.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json

def calculate_weekly_performance(contributions: Dict, transactions: List, prices: Dict[str, float]) -> Dict:
    """Calculate weekly performance metrics for each member"""
    
    # Get data from last week and this week
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)
    
    performance = {}
    
    for member in contributions.keys():
        # Calculate contributions up to last week vs this week
        member_contribs = contributions.get(member, [])
        
        contrib_last_week = sum(
            c["amount"] for c in member_contribs 
            if datetime.fromisoformat(c["date"]) <= one_week_ago
        )
        
        contrib_this_week = sum(c["amount"] for c in member_contribs)
        
        # Calculate portfolio share last week vs this week
        total_contrib_last_week = sum(
            sum(c["amount"] for c in member_contribs 
                if datetime.fromisoformat(c["date"]) <= one_week_ago)
            for member_contribs in contributions.values()
        )
        
        total_contrib_this_week = sum(
            sum(c["amount"] for c in member_contribs)
            for member_contribs in contributions.values()
        )
        
        # Calculate ownership percentages
        ownership_last_week = (contrib_last_week / total_contrib_last_week * 100) if total_contrib_last_week > 0 else 0
        ownership_this_week = (contrib_this_week / total_contrib_this_week * 100) if total_contrib_this_week > 0 else 0
        
        performance[member] = {
            "contributions_added": contrib_this_week - contrib_last_week,
            "ownership_change": ownership_this_week - ownership_last_week,
            "current_ownership": ownership_this_week
        }
    
    return performance

def create_portfolio_trend_chart(transactions: List, prices: Dict[str, float]) -> go.Figure:
    """Create a trend chart showing portfolio value over time"""
    
    if not transactions:
        return go.Figure()
    
    # Sort transactions by date
    sorted_transactions = sorted(transactions, key=lambda x: x["timestamp"])
    
    # Calculate cumulative portfolio value
    dates = []
    portfolio_values = []
    cumulative_btc = 0
    cumulative_eth = 0
    
    for tx in sorted_transactions:
        dates.append(datetime.fromisoformat(tx["timestamp"]))
        
        if tx["crypto"] == "BTC":
            cumulative_btc += tx["amount"]
        elif tx["crypto"] == "ETH":
            cumulative_eth += tx["amount"]
        
        # Calculate portfolio value at current prices
        portfolio_value = (cumulative_btc * prices["BTC"]) + (cumulative_eth * prices["ETH"])
        portfolio_values.append(portfolio_value)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#45B7D1', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (AUD)",
        hovermode='x unified'
    )
    
    return fig

def create_contribution_heatmap(contributions: Dict) -> go.Figure:
    """Create a heatmap showing contribution patterns by member and week"""
    
    # Prepare data for heatmap
    all_dates = []
    for member_contribs in contributions.values():
        for contrib in member_contribs:
            all_dates.append(datetime.fromisoformat(contrib["date"]).date())
    
    if not all_dates:
        return go.Figure()
    
    # Get week ranges
    min_date = min(all_dates)
    max_date = max(all_dates)
    
    # Create weekly buckets
    weeks = []
    current_date = min_date
    while current_date <= max_date:
        week_start = current_date - timedelta(days=current_date.weekday())
        weeks.append(week_start)
        current_date += timedelta(days=7)
    
    # Create matrix
    members = list(contributions.keys())
    contribution_matrix = []
    
    for member in members:
        member_row = []
        member_contribs = contributions[member]
        
        for week_start in weeks:
            week_end = week_start + timedelta(days=6)
            week_contrib = sum(
                c["amount"] for c in member_contribs
                if week_start <= datetime.fromisoformat(c["date"]).date() <= week_end
            )
            member_row.append(week_contrib)
        
        contribution_matrix.append(member_row)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=contribution_matrix,
        x=[f"Week {i+1}" for i in range(len(weeks))],
        y=members,
        colorscale='Viridis',
        hoverongaps=False,
        hovertemplate='<b>%{y}</b><br>%{x}<br>Contribution: $%{z} AUD<extra></extra>'
    ))
    
    fig.update_layout(
        title="Weekly Contribution Heatmap",
        xaxis_title="Week",
        yaxis_title="Member"
    )
    
    return fig

def calculate_roi_by_crypto(transactions: List, prices: Dict[str, float]) -> Dict:
    """Calculate ROI for each cryptocurrency"""
    
    crypto_stats = {"BTC": {"invested": 0, "amount": 0}, "ETH": {"invested": 0, "amount": 0}}
    
    for tx in transactions:
        if tx["type"] == "buy":
            crypto = tx["crypto"]
            crypto_stats[crypto]["invested"] += tx["total_cost"]
            crypto_stats[crypto]["amount"] += tx["amount"]
    
    roi_data = {}
    for crypto, stats in crypto_stats.items():
        if stats["invested"] > 0:
            current_value = stats["amount"] * prices[crypto]
            roi_percentage = ((current_value - stats["invested"]) / stats["invested"]) * 100
            roi_data[crypto] = {
                "invested": stats["invested"],
                "current_value": current_value,
                "roi_percentage": roi_percentage,
                "amount_held": stats["amount"]
            }
    
    return roi_data

def get_contribution_streak(member: str, contributions: Dict) -> int:
    """Calculate current weekly contribution streak for a member"""
    
    member_contribs = contributions.get(member, [])
    if not member_contribs:
        return 0
    
    # Sort by date
    sorted_contribs = sorted(member_contribs, key=lambda x: x["date"], reverse=True)
    
    # Check weekly streak
    streak = 0
    current_week = datetime.now().isocalendar()[1]
    current_year = datetime.now().year
    
    for contrib in sorted_contribs:
        contrib_date = datetime.fromisoformat(contrib["date"])
        contrib_week = contrib_date.isocalendar()[1]
        contrib_year = contrib_date.year
        
        expected_week = current_week - streak
        expected_year = current_year
        
        if expected_week <= 0:
            expected_week += 52
            expected_year -= 1
        
        if contrib_week == expected_week and contrib_year == expected_year:
            streak += 1
        else:
            break
    
    return streak

def export_data_to_csv(contributions: Dict, transactions: List, portfolio: Dict) -> Tuple[str, str, str]:
    """Export all data to CSV format for backup/analysis"""
    
    # Export contributions
    contrib_data = []
    for member, member_contribs in contributions.items():
        for contrib in member_contribs:
            contrib_data.append({
                "Member": member,
                "Amount": contrib["amount"],
                "Date": contrib["date"],
                "Timestamp": contrib["timestamp"]
            })
    
    contrib_df = pd.DataFrame(contrib_data)
    contrib_csv = contrib_df.to_csv(index=False)
    
    # Export transactions
    trans_df = pd.DataFrame(transactions)
    trans_csv = trans_df.to_csv(index=False)
    
    # Export portfolio
    portfolio_data = [{"Crypto": crypto, "Amount": amount} for crypto, amount in portfolio.items()]
    portfolio_df = pd.DataFrame(portfolio_data)
    portfolio_csv = portfolio_df.to_csv(index=False)
    
    return contrib_csv, trans_csv, portfolio_csv

def generate_weekly_summary_report(contributions: Dict, transactions: List, portfolio: Dict, prices: Dict[str, float]) -> str:
    """Generate a formatted weekly summary report"""
    
    performance = calculate_weekly_performance(contributions, transactions, prices)
    
    report = f"""
# 📊 Cryptogeezas Weekly Summary Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 💰 Current Portfolio Status
"""
    
    # Calculate totals
    total_contributions = sum(sum(c["amount"] for c in member_contribs) for member_contribs in contributions.values())
    portfolio_value = sum(portfolio.get(crypto, 0) * prices[crypto] for crypto in ["BTC", "ETH"])
    
    report += f"""
- **Total Invested:** ${total_contributions:,.2f} AUD
- **Current Portfolio Value:** ${portfolio_value:,.2f} AUD
- **Gain/Loss:** ${portfolio_value - total_contributions:,.2f} AUD ({((portfolio_value - total_contributions) / total_contributions * 100) if total_contributions > 0 else 0:.1f}%)

## 👥 Member Performance This Week
"""
    
    for member, perf in performance.items():
        streak = get_contribution_streak(member, contributions)
        report += f"""
### {member}
- Contributions Added: ${perf['contributions_added']:.2f} AUD
- Ownership Change: {perf['ownership_change']:+.1f}%
- Current Ownership: {perf['current_ownership']:.1f}%
- Contribution Streak: {streak} weeks
"""
    
    return report
