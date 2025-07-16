# Cryptogeezas Investment Club Configuration

# Club Members (modify as needed)
MEMBERS = [
    "Charles",
    "Ross Parmenter", 
    "Jayden Kenna",
    "Brad Johnson"
]

# Investment Settings
WEEKLY_CONTRIBUTION = 75.0  # AUD per member per week
SUPPORTED_CRYPTOS = ["BTC", "ETH"]  # Supported cryptocurrencies

# API Settings
COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"
CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum"
}

# Fallback prices (used when API is unavailable) - in AUD
FALLBACK_PRICES = {
    "BTC": 97500,
    "ETH": 5250
}

# Data Storage
DATA_DIRECTORY = "data"
CONTRIBUTIONS_FILE = "contributions.json"
TRANSACTIONS_FILE = "transactions.json"
PORTFOLIO_FILE = "portfolio.json"

# UI Settings
APP_TITLE = "Cryptogeezas Investment Club"
APP_ICON = "💰"
LAYOUT = "wide"

# Chart Colors (for Plotly)
CHART_COLORS = [
    "#FF6B6B",  # Red
    "#4ECDC4",  # Teal
    "#45B7D1",  # Blue
    "#96CEB4",  # Green
    "#FFEAA7",  # Yellow
    "#DDA0DD",  # Plum
    "#98D8E8",  # Light Blue
    "#F7DC6F"   # Light Yellow
]
