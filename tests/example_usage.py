from src.fetch_tradingview_financials import fetch_financial_data, print_financial_data
from src.mongodb_handler import MongoDBHandler
import time

def extract_symbol_without_exchange(full_symbol):
    """
    Extract just the symbol part without the exchange prefix
    Example: "CSELK:HAYL.N0000" -> "HAYL.N0000"
    """
    if ":" in full_symbol:
        return full_symbol.split(":")[1]
    return full_symbol

if __name__ == "__main__":
    # Initialize MongoDB connection
    try:
        db_handler = MongoDBHandler()
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        exit(1)
    
    # List of company symbols to fetch
    companies = [
        "CSELK:AAF.N0000"
    ]
    
    for full_symbol in companies:
        try:
            # Extract the symbol without exchange prefix for MongoDB lookup
            db_symbol = extract_symbol_without_exchange(full_symbol)
            
            print(f"\nFetching data for {full_symbol} (DB symbol: {db_symbol})")
            start_time = time.time()
            
            # Fetch financial data using the full symbol
            data = fetch_financial_data(full_symbol, timeout=15)
            
            fetch_time = time.time() - start_time
            print(f"Data retrieved in {fetch_time:.2f} seconds")
            
            # Print formatted results
            print_financial_data(data)
            
            # Store data in MongoDB using the symbol without exchange prefix
            print(f"Storing data for {db_symbol} in MongoDB...")
            success = db_handler.update_company_financials(db_symbol, data)
            
            if success:
                print(f"Successfully stored data for {db_symbol} in MongoDB")
            else:
                print(f"Failed to store data for {db_symbol} in MongoDB")
            
        except Exception as e:
            print(f"Error processing {full_symbol}: {e}")
        
        # Brief pause between requests
        time.sleep(1)
    
    # Close MongoDB connection
    db_handler.close()
    print("\nAll company data processed and stored")