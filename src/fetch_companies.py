import os
import requests
from datetime import datetime
from typing import List, Optional, TypedDict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TAllCompanyCodes(TypedDict):
    id: int
    name: str
    symbol: str

def fetch_all_company_codes() -> Optional[List[TAllCompanyCodes]]:
    # Check API availability
    api_url = os.getenv("CSE_ALL_COMPANY_CODES_API_URL")
    if not api_url:
        print("Error: Please define the CSE_ALL_COMPANY_CODES_API_URL environment variable")
        return None

    try:
        # Make GET request
        response = requests.get(
            api_url,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()  # Raise exception for non-2xx status

        # Log success message with alignment
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"{'All company codes data fetched successfully at':<50} {timestamp}")

        # Process and sort data
        data: List[TAllCompanyCodes] = response.json()
        sorted_data = sorted(data, key=lambda x: x['symbol'])
        return sorted_data

    except Exception as error:
        print(f"Error fetching company codes data: {error}")
        return None