import time
from typing import List, Optional
from tqdm import tqdm
from src.fetch_companies import fetch_all_company_codes
from src.mongodb_handler import MongoDBHandler
from src.fetch_tradingview_financials import fetch_financial_data


def process_all_companies(
    rate_limit: float = 5.0,  # Increased from 1.0 to 5.0
    max_companies: Optional[int] = None,
    retry_delay: float = 10.0,
    max_retries: int = 3,
):
    """Process companies with reliable single-request approach"""
    db_handler = MongoDBHandler()

    try:
        # Fetch company codes
        print("Fetching all company codes...")
        company_codes = fetch_all_company_codes()
        if not company_codes:
            print("No company codes available. Exiting.")
            return

        total_companies = (
            min(len(company_codes), max_companies)
            if max_companies
            else len(company_codes)
        )
        print(f"\nProcessing {total_companies} companies with {rate_limit}s delay...")

        processed = 0
        progress_bar = tqdm(
            company_codes[:total_companies], desc="Processing", unit="company"
        )

        for company in progress_bar:
            symbol = company["symbol"]
            tradingview_symbol = f"CSELK:{symbol}"

            # Update progress bar description
            progress_bar.set_description(f"Processing {company['name']}")

            for attempt in range(max_retries):
                try:
                    # Fetch and process data
                    tv_data = fetch_financial_data(tradingview_symbol)

                    if tv_data:
                        if db_handler.update_company_financials(symbol, tv_data):
                            processed += 1
                            progress_bar.set_postfix({"success": processed})
                            break  # Success, move to next company
                        else:
                            print(f"\nFailed to update {symbol} in MongoDB")
                    else:
                        print(f"\nNo data received for {symbol}")

                except Exception as e:
                    if attempt == max_retries - 1:
                        print(
                            f"\nFailed to process {symbol} after {max_retries} attempts"
                        )
                    else:
                        time.sleep(retry_delay * (attempt + 1))  # Exponential backoff

            # Rate limiting
            if company != company_codes[-1]:  # Don't sleep after last company
                time.sleep(rate_limit)

        print(
            f"\nCompleted. Successfully updated {processed}/{total_companies} companies."
        )

    finally:
        db_handler.close()


if __name__ == "__main__":
    process_all_companies(
        rate_limit=2.0,  # 5 seconds between requests (conservative)
        max_companies=315,
        retry_delay=10.0,  # Wait longer between retries
        max_retries=1,
    )
