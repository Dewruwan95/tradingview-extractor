import os
import websocket
import json
import ssl
import _thread
import time
import re
import random
import string
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fetch_financial_data(symbol, timeout=15):
    """
    Fetches financial data for a given TradingView symbol
    Args:
        symbol (str): TradingView symbol (e.g., 'CSELK:HAYL.N0000')
        timeout (int): Maximum time to wait for data in seconds (default: 15)
    Returns:
        dict: Financial data dictionary
    """
    websocket_url = os.getenv("TRADINGVIEW_WEBSOCKET_URL")
    
    # Generate unique session ID
    session_id = f"qs_{''.join(random.choices(string.ascii_letters + string.digits, k=12))}"
    
    # Build messages with proper formatting
    def create_message(content):
        return f'~m~{len(content)}~m~{content}'
    
    messages = [
        create_message('{"m":"set_data_quality","p":["low"]}'),
        create_message('{"m":"set_auth_token","p":["unauthorized_user_token"]}'),
        create_message('{"m":"set_locale","p":["en","US"]}'),
        create_message(f'{{"m":"quote_create_session","p":["{session_id}"]}}'),
        create_message(f'{{"m":"quote_add_symbols","p":["{session_id}","{symbol}"]}}'),
        create_message(f'{{"m":"quote_fast_symbols","p":["{session_id}","{symbol}"]}}')
    ]
    
    # Data storage
    financial_data = {
        "business_description": None, #tradingViewData.businessSummary
        "web_site_url": None, #tradingViewData.website
        "total_assets_fy_h": None, #tradingViewData.totalAssetsHistoryYearly
        "total_assets_fq_h": None, #tradingViewData.totalAssetsHistoryQuarterly
        "total_liabilities_fy_h": None, #tradingViewData.totalLiabilitiesHistoryYearly
        "total_liabilities_fq_h": None, #tradingViewData.totalLiabilitiesHistoryQuarterly
        "total_equity_fy_h": None, #tradingViewData.totalEquityHistoryYearly
        "total_equity_fq_h": None, #tradingViewData.totalEquityHistoryQuarterly
        "net_debt_fy_h": None, #tradingViewData.netDebtHistoryYearly
        "net_debt_fq_h": None, #tradingViewData.netDebtHistoryQuarterly
        "fiscal_period_fy_h": None, #tradingViewData.financialYearHistoryYearly
        "fiscal_period_fq_h": None, #tradingViewData.financialYearHistoryQuarterly
        "fiscal_period_end_fy_h": None, #tradingViewData.financialYearEndHistoryYearly
        "fiscal_period_end_fq_h": None, #tradingViewData.financialYearEndHistoryQuarterly
        "total_shares_outstanding_fy": None, #tradingViewData.numberOfShares
        "book_value_per_share_fy_h": None, #tradingViewData.netAssetsPerShareHistoryYearly
        "book_value_per_share_fq_h": None, #tradingViewData.netAssetsPerShareHistoryQuarterly
        "earnings_per_share_diluted_fy_h": None, #tradingViewData.earningsPerShareHistoryYearly
        "earnings_per_share_diluted_fq_h": None, #tradingViewData.earningsPerShareHistoryQuarterly
        "price_earnings_fy_h": None, #tradingViewData.priceEarningsRatioHistoryYearly
        "price_earnings_fq_h": None, #tradingViewData.priceEarningsRatioHistoryQuarterly
        "price_book_fy_h": None, #tradingViewData.priceToBookValueHistoryYearly
        "price_book_fq_h": None, #tradingViewData.priceToBookValueHistoryQuarterly
        "dividends_availability": None, #tradingViewData.dividendsAvailability
        "dividend_type_h": None, #tradingViewData.dividendTypeHistory
        "dividend_amount_h": None, #tradingViewData.dividendPerShareHistory
        "dividends_yield_fy_h": None, #tradingViewData.dividendYieldHistoryYearly
        "dividend_payment_date_h": None, #tradingViewData.dividendPaymentDateHistory
        "dividend_ex_date_h": None, #tradingViewData.dividendXdDateHistory
        "symbol": symbol
    }
    
    # Event to signal when we're done
    done_event = threading.Event()
    
    def parse_tradingview_message(raw_message):
        segments = []
        pattern = re.compile(r'~m~(\d+)~m~')
        index = 0
        
        while index < len(raw_message):
            match = pattern.match(raw_message[index:])
            if not match:
                break
                
            length_str = match.group(1)
            try:
                length = int(length_str)
            except ValueError:
                break
                
            header_length = len(f"~m~{length_str}~m~")
            start_pos = index + header_length
            end_pos = start_pos + length
            
            if end_pos > len(raw_message):
                break
                
            content = raw_message[start_pos:end_pos]
            segments.append(content)
            index = end_pos
        
        return segments

    def on_message(ws, message):
        if message.startswith('~h~'):
            return
            
        segments = parse_tradingview_message(message)
        
        for segment in segments:
            try:
                data = json.loads(segment)
                if data.get("m") == "qsd":
                    p_data = data.get("p", [])
                    if len(p_data) >= 2 and isinstance(p_data[1], dict):
                        symbol_data = p_data[1]
                        if symbol_data.get("s") == "ok":
                            v_data = symbol_data.get("v", {})
                            for key in financial_data.keys():
                                if key in v_data:
                                    financial_data[key] = v_data[key]
            except:
                continue

    def on_error(ws, error):
        done_event.set()

    def on_close(ws, close_status_code, close_msg):
        done_event.set()

    def on_open(ws):
        def run(*args):
            for msg in messages:
                ws.send(msg)
                time.sleep(0.5)
        _thread.start_new_thread(run, ())

    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        websocket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header={
            "Origin": "https://www.tradingview.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
    )
    
    # Start WebSocket in a separate thread
    ws_thread = threading.Thread(
        target=ws.run_forever,
        kwargs={
            "sslopt": {"cert_reqs": ssl.CERT_NONE},
            "ping_interval": 20,
            "ping_timeout": 10
        },
        daemon=True
    )
    ws_thread.start()
    
    # Wait for completion or timeout
    done_event.wait(timeout=timeout)
    
    # Close connection if still open
    if ws.sock and ws.sock.connected:
        ws.close()
    
    return financial_data

def print_financial_data(data):
    """
    Prints financial data in a readable format
    Args:
        data (dict): Financial data dictionary from fetch_financial_data()
    """
    if not data:
        print("No financial data available")
        return
        
    symbol = data.get("symbol", "Unknown Symbol")
    print(f"\n{'='*50}")
    print(f"Financial Data for {symbol}")
    print(f"{'='*50}")
    
    for key, value in data.items():
        if key == "symbol":
            continue
            
        if value is None:
            print(f"{key.replace('_', ' ').title()}: Not available")
        elif isinstance(value, list):
            print(f"{key.replace('_', ' ').title()}:")
            print(f"  Periods: {len(value)}")
            if value:
                print(f"  Most Recent: {value[0]}")
                print(f"  Oldest: {value[-1]}")
        elif isinstance(value, str) and len(value) > 100:
            print(f"{key.replace('_', ' ').title()}: {value[:100]}...")
        else:
            print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"{'='*50}\n")