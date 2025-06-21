import yfinance as yf
import pandas as pd
import os
import sys

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, project_root)

# Now import using absolute path
from agents.utils.stocknameformatter import format_stock_list

# List of NSE stocks (Yahoo format)
#stock_list = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "LT.NS"]
stock_list = ["suggested_stocks"]  # Placeholder for stocks to be filled by the stock agent
def get_stock_roe(ticker):
    try:
        stock = yf.Ticker(ticker)
        fin_data = stock.info
        
        roe = fin_data.get("returnOnEquity", None)
        if roe is not None:
            roe_percent = round(roe * 100, 2)
            return roe_percent
        else:
            return None
    except Exception as e:
        print(f"Error retrieving data for {ticker}: {e}")
        return None

def is_revenue_increasing_in_5y(ticker):
    try:
        stock = yf.Ticker(ticker)
        fin_data = stock.financials
        if 'Total Revenue' in fin_data.index:
            revenue = fin_data.loc['Total Revenue']
            # Use .iloc for positional indexing
           # print(f"Revenue data for {ticker}: {revenue}")
            return all(revenue.iloc[i] < revenue.iloc[i + 1] for i in range(len(revenue) - 1))
        return False
    except Exception as e:
        print(f"Error checking revenue for {ticker}: {e}")
        return False

def get_Dividend_History_of_5years(ticker):
    try:
        stock = yf.Ticker(ticker)
        dividends = stock.dividends
        
        if not dividends.empty:
            # Convert the index to UTC timezone to standardize comparison
            dividends.index = dividends.index.tz_localize(None)
            
            # Create timezone-naive timestamp for comparison
            current_time = pd.Timestamp.now().tz_localize(None)
            five_years_ago = current_time - pd.DateOffset(years=5)
            
            # Filter last 5 years of dividends
            last_5_years = dividends[dividends.index >= five_years_ago]
            
            # Check if dividends exist and are increasing
            has_dividends = len(last_5_years) > 0
            if has_dividends:
                # Calculate year-over-year dividend growth
                annual_dividends = last_5_years.groupby(last_5_years.index.year).sum()
                is_increasing = all(annual_dividends.diff().dropna() > 0)
                return is_increasing
            
        return False
    except Exception as e:
        print(f"Error retrieving dividend history for {ticker}: {e}")
        # Add debug information
        if 'dividends' in locals():
          #  print(f"Dividend index type: {dividends.index.dtype}")
          # print(f"Dividend timezone info: {dividends.index.tz}")
          return False

#**Return on Capital Employed (ROCE):** Evaluate the company's return on capital employed it should be >15%.
def get_roce_of_stock(ticker):
    try:
        stock = yf.Ticker(ticker)
        
        # Get financial data
        fin_data = stock.info
        balance_sheet = stock.balance_sheet
        income_stmt = stock.income_stmt if hasattr(stock, 'income_stmt') else stock.financials
        
        # Get latest values
        if not balance_sheet.empty and not income_stmt.empty:
            # Try to get EBIT or Operating Income
            try:
                ebit = income_stmt.loc['EBIT'].iloc[0]
            except KeyError:
                try:
                    # Try Operating Income if EBIT is not available
                    ebit = income_stmt.loc['Operating Income'].iloc[0]
                except KeyError:
                    try:
                        # Try Ebit as another alternative
                        ebit = income_stmt.loc['Ebit'].iloc[0]
                    except KeyError:
                        print(f"Neither EBIT nor Operating Income found for {ticker}")
                      #  print("Available fields:", income_stmt.index.tolist())
                        return None
            
            try:
                # Get Total Assets
                total_assets = balance_sheet.loc['Total Assets'].iloc[0]
            except KeyError:
                try:
                    total_assets = balance_sheet.loc['Total Asset'].iloc[0]
                except KeyError:
                    print(f"Total Assets not found for {ticker}")
                    return None
            
            try:
                # Get Current Liabilities
                current_liabilities = balance_sheet.loc['Current Liabilities'].iloc[0]
            except KeyError:
                try:
                    current_liabilities = balance_sheet.loc['Total Current Liabilities'].iloc[0]
                except KeyError:
                    print(f"Current Liabilities not found for {ticker}")
                    return None
            
            # Calculate Capital Employed
            capital_employed = total_assets - current_liabilities
            
            # Calculate ROCE
            if capital_employed != 0:
                roce = (ebit / capital_employed) * 100
                return round(roce, 2)
            else:
                print(f"Warning: Capital Employed is zero for {ticker}")
                return None
        
        return None
    except Exception as e:
        print(f"Error calculating ROCE for {ticker}: {e}")
       # print("Available Income Statement fields:", income_stmt.index.tolist() if 'income_stmt' in locals() else "No income statement available")
        #print("Available Balance Sheet fields:", balance_sheet.index.tolist() if 'balance_sheet' in locals() else "No balance sheet available")
        return None

def reviewer1_trading_tool(input_data: dict = {}) -> dict:
    """
    Analyze stocks based on financial criteria
    Args:
        input_data: Dictionary containing suggested_stocks list
    Returns:
        dict: Contains qualified stocks with their metrics
        """
        # Extract stock list from input_data
        # Extract suggested stocks from input or use default list
    raw_stocks = (input_data.get("suggested_stocks") if input_data 
                 else ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", 
                       "ICICIBANK.NS", "ITC.NS", "SBIN.NS", "LT.NS"])

    # Format stock list to ensure correct ticker symbols
    stock_list = format_stock_list(raw_stocks)
    print(f"Analyzing stocks: {stock_list}")
    qualified_stocks = []
    for stock in stock_list:
        roe = get_stock_roe(stock)
        roce = get_roce_of_stock(stock)
        print ( f"Analyzing {stock}: ROE = {roe}, ROCE = {roce}")
        if roe is not None and roe > 15:
            stock_info = {
                "symbol": stock,
                "roe": roe,
                "roce": roce,
                "increasing_revenue": is_revenue_increasing_in_5y(stock),
                "consistent_dividends": get_Dividend_History_of_5years(stock)
            }
            qualified_stocks.append(stock_info)
    # Sort by ROE descending
    qualified_stocks = sorted(qualified_stocks, key=lambda x: x["roe"], reverse=True)
   # Display results
    print("Qualified Stocks:")
    for stock in qualified_stocks:
        print(f"{stock['symbol']}: ROE = {stock['roe']}%, ROCE = {stock['roce']}%")
    
    # Return with the expected output_key
    return {
        "shortlisted_stocks": qualified_stocks
    }

if __name__ == "__main__":
    # Test with default stocks
    result1 = reviewer1_trading_tool()
    print("\nTest with default stocks:", result1)
    
    # Test with custom stocks
    test_input = {
       # "suggested_stocks": ["RELIANCE.NS", "TCS.NS"]
        "suggested_stocks":["Reliance Industries (RELIANCE)","Tata Consultancy Services (TCS)"]
    }
    result2 = reviewer1_trading_tool(test_input)
    print("\nTest with CUSTOM STOCKS:", result2)