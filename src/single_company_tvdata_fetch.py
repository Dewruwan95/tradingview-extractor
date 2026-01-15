import os
import websocket
import json
import ssl
import random
import string
import re
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
    session_id = (
        f"qs_{''.join(random.choices(string.ascii_letters + string.digits, k=12))}"
    )

    # Build messages with proper formatting
    def create_message(content):
        return f"~m~{len(content)}~m~{content}"

    messages = [
        create_message('{"m":"set_data_quality","p":["low"]}'),
        create_message('{"m":"set_auth_token","p":["unauthorized_user_token"]}'),
        create_message('{"m":"set_locale","p":["en","US"]}'),
        create_message(f'{{"m":"quote_create_session","p":["{session_id}"]}}'),
        create_message(f'{{"m":"quote_add_symbols","p":["{session_id}","{symbol}"]}}'),
        create_message(f'{{"m":"quote_fast_symbols","p":["{session_id}","{symbol}"]}}'),
    ]

    # Data storage
    financial_data = {
        "business_description": None,
        "web_site_url": None,
        "total_assets_fy_h": None,
        "total_assets_fq_h": None,
        "total_liabilities_fy_h": None,
        "total_liabilities_fq_h": None,
        "total_equity_fy_h": None,
        "total_equity_fq_h": None,
        "net_debt_fy_h": None,
        "net_debt_fq_h": None,
        "fiscal_period_fy_h": None,
        "fiscal_period_fq_h": None,
        "fiscal_period_end_fy_h": None,
        "fiscal_period_end_fq_h": None,
        "total_shares_outstanding_fy": None,
        "book_value_per_share_fy_h": None,
        "book_value_per_share_fq_h": None,
        "earnings_per_share_diluted_fy_h": None,
        "earnings_per_share_diluted_fq_h": None,
        "price_earnings_fy_h": None,
        "price_earnings_fq_h": None,
        "price_book_fy_h": None,
        "price_book_fq_h": None,
        "dividends_availability": None,
        "dividend_type_h": None,
        "dividend_amount_h": None,
        "dividends_yield_fy_h": None,
        "dividend_payment_date_h": None,
        "dividend_ex_date_h": None,
        "symbol": symbol,
    }

    received_data = False

    def parse_tradingview_message(raw_message):
        segments = []
        pattern = re.compile(r"~m~(\d+)~m~")
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
        nonlocal received_data
        if message.startswith("~h~"):
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
                            received_data = True
                            ws.close()
            except:
                continue

    def on_error(ws, error):
        print(f"WebSocket error: {error}")

    def on_close(ws, close_status_code, close_msg):
        pass

    def on_open(ws):
        for msg in messages:
            ws.send(msg)

    # Create WebSocket connection
    ws = websocket.WebSocketApp(
        websocket_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        header={
            "Origin": "https://www.tradingview.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        },
    )

    # Run WebSocket
    ws.run_forever(
        sslopt={"cert_reqs": ssl.CERT_NONE}, ping_interval=20, ping_timeout=10
    )

    return financial_data if received_data else None


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
    print(f"\n{'=' * 50}")
    print(f"Financial Data for {symbol}")
    print(f"{'=' * 50}")

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

    print(f"{'=' * 50}\n")


# Simple test function
def test_financial_data(symbol):
    """
    Simple function to fetch and print company data
    """
    print(f"Fetching data for {symbol}...")
    data = fetch_financial_data(symbol)
    print_financial_data(data)


# Example usage
if __name__ == "__main__":
    # Test with a symbol
    test_financial_data("CSELK:AAF.N0000")
