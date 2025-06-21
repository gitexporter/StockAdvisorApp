import re

# Dictionary mapping common company names to their NSE symbols
COMPANY_TO_SYMBOL = {
    # Large Cap
    "RELIANCE INDUSTRIES": "RELIANCE",
    "TATA CONSULTANCY SERVICES": "TCS",
    "HDFC BANK": "HDFCBANK",
    "INFOSYS": "INFY",
    "ICICI BANK": "ICICIBANK",
    "STATE BANK OF INDIA": "SBIN",
    "ITC": "ITC",
    "LARSEN & TOUBRO": "LT",
    "HINDUSTAN UNILEVER": "HINDUNILVR",
    "BHARTI AIRTEL": "BHARTIARTL",
    "Maruti Suzuki":"MARUTI",
    "Sun Pharma": "SUNPHARMA",
    "HDFC": "HDFC",
    "HCL TECHNOLOGIES": "HCLTECH",
    "WIPRO": "WIPRO",
    "TECH MAHINDRA": "TECHM",
    "ASIAN PAINTS": "ASIANPAINT",
    "ULTRATECH CEMENT": "ULTRACEMCO",
    "TATA STEEL": "TATASTEEL",
    "TATA MOTORS": "TATAMOTORS",
    "POWER GRID CORPORATION": "POWERGRID",
    "NTPC": "NTPC",
    "ONGC": "ONGC",
    "ADANI GREEN ENERGY": "ADANIGREEN",
    "ADANI PORTS": "ADANIPORTS",
    "HINDALCO INDUSTRIES": "HINDALCO",
    "JSW STEEL": "JSWSTEEL",
    "BAJAJ FINANCE": "BAJFINANCE",
    "BAJAJ FINSERV": "BAJFIN",
    "KOTAK MAHINDRA BANK": "KOTAKBANK",
    "AXIS BANK": "AXISBANK",
    "MARUTI SUZUKI": "MARUTI",
    "SUN PHARMACEUTICAL INDUSTRIES": "SUNPHARMA",
    "HDFC LIFE INSURANCE": "HDFCLIFE",
    "ICICI PRUDENTIAL LIFE INSURANCE": "ICICIPRULI",
    "BHARAT PETROLEUM CORPORATION": "BPCL",
    "GAIL (INDIA)": "GAIL",
    "TATA POWER COMPANY": "TATAPOWER",
    "ADANI TRANSMISSION": "ADANITRANS",
    "DIVI'S LABORATORIES": "DIVISLAB",
    "DR REDDY'S LABORATORIES": "DRREDDY",
    "HERO MOTOCORP": "HEROMOTOCO",
    "MARICO": "MARICO",
    "PIDILITE INDUSTRIES": "PIDILITIND",
    "SHREE CEMENT": "SHREECEM",
    "TATA CONSUMER PRODUCTS": "TATACONSUMER",
    "TECH MAHINDRA": "TECHM",
    "ADANI ENTERPRISES": "ADANIENT",
    "ADANI WILMAR": "ADANIWIL",
    "HAVELLS INDIA": "HAVELLS",
    "M&M": "M&M",
    "MOTHERSON SUMI": "MOTHERSON",
    "BOSCH LIMITED": "BOSCHLTD",
    "ABB INDIA": "ABB",
    "SIEMENS": "SIEMENS",   
    # Mid Cap"
    "BANDHAN BANK": "BANDHANBNK",
    "BATA INDIA": "BATAINDIA",
    "BEL": "BEL",
    "BHEL": "BHEL",
    "CUMMINS INDIA": "CUMMINSIND",
    "DABUR INDIA": "DABUR",
    "EXIDE INDUSTRIES": "EXIDEIND",
    "GODREJ CONSUMER PRODUCTS": "GODREJCP",
    "GODREJ PROPERTIES": "GODREJPROP",
    "HINDUSTAN AERONAUTICS": "HAL",
    "JINDAL STEEL & POWER": "JINDALSTEL",
    "KARUR VYSYA BANK": "KARURVYSYA",
    "LUPIN": "LUPIN",
    "M&M FINANCIAL SERVICES": "MMFIN",
    "MARUTI SUZUKI INDIA": "MARUTI",
    "MUTHOOT FINANCE": "MUTHOOTFIN",
    "NESTLE INDIA": "NESTLEIND",
    "PAGE INDUSTRIES": "PAGEIND",
    "PERSISTENT SYSTEMS": "PERSISTENT",

    # Common variations
    "RELIANCE": "RELIANCE",
    "TCS": "TCS",
    "INFOSYS LIMITED": "INFY",
    "SBI": "SBIN",
    "L&T": "LT",
    "HUL": "HINDUNILVR",
    "AIRTEL": "BHARTIARTL",

    # Add more mappings as needed
    # Note: Ensure all symbols are in uppercase and end with .NS for NSE

    "HDFC BANK LIMITED": "HDFCBANK",
    "ICICI BANK LIMITED": "ICICIBANK",
    "ITC LIMITED": "ITC",
    "HDFC LIMITED": "HDFC",
    "HCL TECHNOLOGIES LIMITED": "HCLTECH",
    "WIPRO LIMITED": "WIPRO",
    "TECH MAHINDRA LIMITED": "TECHM",
    "ASIAN PAINTS LIMITED": "ASIANPAINT",
    "ULTRATECH CEMENT LIMITED": "ULTRACEMCO",
    "TATA STEEL LIMITED": "TATASTEEL",
    "TATA MOTORS LIMITED": "TATAMOTORS",
    "POWER GRID CORPORATION OF INDIA": "POWERGRID",
    "NTPC LIMITED": "NTPC"
}

def format_nse_ticker(stock_name: str) -> str:
    """
    Convert company name to NSE ticker symbol format (SYMBOL.NS)
    
    Args:
        stock_name: Company name or partial ticker
        
    Returns:
        Formatted NSE ticker (e.g., "SYMBOL.NS")
    """
    try:
        # Remove parentheses and their contents
        clean_name = re.sub(r'\([^)]*\)', '', stock_name).strip()
        
        # Convert to uppercase
        name_upper = clean_name.upper()
      #  print(f"Formatting ticker for: {name_upper}")
        # Try to find exact match first
        if name_upper in COMPANY_TO_SYMBOL:
            symbol = COMPANY_TO_SYMBOL[name_upper]
        else:
            # Try to find partial matches
            matches = [symbol for company, symbol in COMPANY_TO_SYMBOL.items() 
                      if company in name_upper or name_upper in company]
           # print(matches)
            if matches:
                symbol = matches[0]
            else:
                # If no match found, use the cleaned input
                # Remove spaces and special characters
                symbol = re.sub(r'[^A-Z.]', '', name_upper)
              #  print(f"No exact match found for {name_upper}, using cleaned input: {symbol}")
       # print(symbol)
        # Add .NS suffix if not present
        if not symbol.endswith('.NS'):
            symbol = f"{symbol}.NS"
            
        return symbol
    
    except Exception as e:
        print(f"Error formatting ticker for {stock_name}: {e}")
        return None

def format_stock_list(stocks: list) -> list:
    """
    Convert a list of company names to NSE ticker symbols
    
    Args:
        stocks: List of company names or partial tickers
        
    Returns:
        List of formatted NSE tickers
    """
    formatted_tickers = []
    for stock in stocks:
        ticker = format_nse_ticker(stock)
        if ticker:
            formatted_tickers.append(ticker)
    return formatted_tickers


if __name__ == "__main__":
   # Test the formatter
   test_names = ['RELIANCE.NS', 'HDFCBANK.NS', 'TCS.NS', 'INFY.NS', 'HINDUNILVR.NS', 'ITC.NS', 'ICICIBANK.NS', 'BHARTIARTL.NS', 'LT.NS', 'ASIANPAINT.NS']
   formatted_tickers = format_stock_list(test_names)
   print(formatted_tickers)