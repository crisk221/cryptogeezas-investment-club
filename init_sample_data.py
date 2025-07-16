"""
Sample data initialization script for testing the Cryptogeezas app.
Run this script to populate the app wit    print("📋 Summary of sample data:")
    print(f"   👥 Members: {', '.join(MEMBERS)}")
    print(f"   💰 Weekly contributions: $75 AUD per member")
    print(f"   📅 8 weeks of contribution history")
    print(f"   🪙 Sample BTC and ETH purchases (AUD prices)")
    print(f"   💼 Current portfolio with holdings")le data for demonstration.
"""

import json
import os
from datetime import datetime, timedelta
import random

# Create data directory
DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

MEMBERS = ["Charles", "Ross Parmenter", "Jayden Kenna", "Brad Johnson"]

def create_sample_contributions():
    """Create sample contribution data for the past 8 weeks"""
    contributions = {member: [] for member in MEMBERS}
    
    # Generate 8 weeks of contributions
    for week in range(8):
        date = datetime.now() - timedelta(weeks=week)
        
        for member in MEMBERS:
            # Most weeks everyone contributes, occasionally someone misses
            if random.random() > 0.1:  # 90% chance of contributing
                contributions[member].append({
                    "amount": 75.0,  # AUD
                    "date": date.isoformat(),
                    "timestamp": date.isoformat()
                })
    
    # Sort contributions by date for each member
    for member in MEMBERS:
        contributions[member].sort(key=lambda x: x["date"])
    
    with open(os.path.join(DATA_DIR, "contributions.json"), 'w') as f:
        json.dump(contributions, f, indent=2)
    
    print("✅ Sample contributions created")

def create_sample_transactions():
    """Create sample crypto purchase transactions"""
    transactions = []
    
    # Sample BTC purchases (prices in AUD)
    btc_transactions = [
        {"crypto": "BTC", "amount": 0.003456, "price": 95250, "date_offset": 6},
        {"crypto": "BTC", "amount": 0.002891, "price": 97800, "date_offset": 4},
        {"crypto": "BTC", "amount": 0.004123, "price": 94200, "date_offset": 2},
    ]
    
    # Sample ETH purchases (prices in AUD)
    eth_transactions = [
        {"crypto": "ETH", "amount": 0.142857, "price": 5250, "date_offset": 5},
        {"crypto": "ETH", "amount": 0.117647, "price": 5100, "date_offset": 3},
        {"crypto": "ETH", "amount": 0.156250, "price": 4800, "date_offset": 1},
    ]
    
    all_sample_transactions = btc_transactions + eth_transactions
    
    for tx in all_sample_transactions:
        date = datetime.now() - timedelta(weeks=tx["date_offset"])
        transactions.append({
            "crypto": tx["crypto"],
            "amount": tx["amount"],
            "price": tx["price"],
            "total_cost": tx["amount"] * tx["price"],
            "type": "buy",
            "timestamp": date.isoformat()
        })
    
    # Sort by timestamp
    transactions.sort(key=lambda x: x["timestamp"])
    
    with open(os.path.join(DATA_DIR, "transactions.json"), 'w') as f:
        json.dump(transactions, f, indent=2)
    
    print("✅ Sample transactions created")

def create_sample_portfolio():
    """Create sample portfolio based on transactions"""
    # Calculate total holdings from transactions
    btc_total = sum([0.003456, 0.002891, 0.004123])
    eth_total = sum([0.142857, 0.117647, 0.156250])
    
    portfolio = {
        "BTC": btc_total,
        "ETH": eth_total
    }
    
    with open(os.path.join(DATA_DIR, "portfolio.json"), 'w') as f:
        json.dump(portfolio, f, indent=2)
    
    print("✅ Sample portfolio created")
    print(f"   BTC Holdings: {btc_total:.6f}")
    print(f"   ETH Holdings: {eth_total:.6f}")

def main():
    print("🚀 Initializing sample data for Cryptogeezas Investment Club...")
    print()
    
    create_sample_contributions()
    create_sample_transactions()
    create_sample_portfolio()
    
    print()
    print("✨ Sample data initialization complete!")
    print("📊 You can now run 'streamlit run app.py' to see the app with sample data")
    
    # Show summary
    print("\n📋 Summary of sample data:")
    print(f"   👥 Members: {', '.join(MEMBERS)}")
    print(f"   💰 Weekly contributions: $50 per member")
    print(f"   📅 8 weeks of contribution history")
    print(f"   🪙 Sample BTC and ETH purchases")
    print(f"   💼 Current portfolio with holdings")

if __name__ == "__main__":
    main()
