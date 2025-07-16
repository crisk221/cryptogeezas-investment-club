# Cryptogeezas Investment Club App 💰

A Streamlit web application for managing a crypto investment club with 4 members: Charles, Ross Parmenter, Jayden Kenna, and Brad Johnson.

## Features

### 📊 Dashboard
- Real-time portfolio value tracking
- Live crypto prices (BTC & ETH) from CoinGecko API
- Portfolio composition charts
- Member ownership breakdown
- Gain/loss calculations

### 💰 Contribution Management
- Track weekly $75 AUD contributions per member
- Quick-add all members' contributions
- Individual contribution tracking
- Contribution history by member

### 🛒 Crypto Trading
- Buy BTC and ETH using the group investment pot
- Real-time price fetching
- Transaction recording
- Available balance tracking

### 📋 History & Analytics
- Complete transaction history
- Member contribution details
- Visual charts and graphs
- Ownership percentage calculations

## Setup Instructions

1. **Install Python** (3.8 or higher)

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Open your browser** and navigate to the URL shown in the terminal (usually `http://localhost:8501`)

## Usage Guide

### Getting Started
1. **Add Initial Contributions**: Go to "Add Contributions" and use "Add $75 AUD for All Members" to get started
2. **Buy Crypto**: Navigate to "Buy Crypto" to purchase BTC or ETH with the group pot
3. **Monitor Dashboard**: View real-time portfolio performance and member ownership

### Weekly Routine
1. Add weekly contributions for all members ($75 AUD each)
2. Decide on crypto purchases as a group
3. Monitor portfolio performance on the dashboard

### Data Persistence
- All data is stored in JSON files in the `data/` directory
- Files are automatically created on first run
- Data persists between app sessions

## File Structure
```
Cryptogeezas/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── data/              # Data storage (auto-created)
    ├── contributions.json   # Member contributions
    ├── transactions.json    # Crypto purchases
    └── portfolio.json       # Current holdings
```

## API Usage
- Uses CoinGecko's free API for real-time crypto prices in AUD
- No API key required
- Fallback prices if API is unavailable

## Member Information
- **Charles**: Investment club member
- **Ross Parmenter**: Investment club member  
- **Jayden Kenna**: Investment club member
- **Brad Johnson**: Investment club member

Each member contributes $75 AUD weekly to the shared investment pot.

## Technical Details
- Built with Streamlit for the web interface
- Plotly for interactive charts and visualizations
- Pandas for data manipulation
- JSON files for simple data persistence
- Real-time crypto price integration

## Troubleshooting

### Common Issues
1. **Import Errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
2. **API Errors**: If crypto prices don't load, check your internet connection
3. **Data Issues**: Delete the `data/` folder to reset all data if needed

### Resetting Data
To start fresh, simply delete the `data/` directory and restart the app.

## Future Enhancements
- Add more cryptocurrencies
- Implement profit/loss tracking over time
- Add email notifications for contributions
- Integration with real exchanges
- Mobile-responsive design improvements
