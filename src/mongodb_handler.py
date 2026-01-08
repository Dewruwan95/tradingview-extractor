import os
from typing import Dict, Optional
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import ssl

# Load environment variables
load_dotenv()

class MongoDBHandler:
    def __init__(self):
        self.uri = os.getenv("MONGODB_URI")
        if not self.uri:
            raise ValueError("MONGODB_URI not found in .env file")
        
        # Force connection to cse-data database
        if "/?" in self.uri:
            self.uri = self.uri.replace("/?", "/cse-data?")
        else:
            self.uri = self.uri + "cse-data"
            
        self.client = None
        self.db = None
        self.collection = None
        self.connect()

    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(
                self.uri,
                tls=True,
                tlsAllowInvalidCertificates=True  # Disable SSL verification for development
            )
            self.db = self.client.get_database()
            self.collection = self.db["companies"]
            print("Successfully connected to MongoDB (cse-data.companies)")
        except PyMongoError as e:
            print(f"Error connecting to MongoDB: {e}")
            raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

    @staticmethod
    def safe_get_first_value(data_list):
        """Safely get the first value from a list or return None if empty"""
        if data_list and len(data_list) > 0:
            return data_list[0]
        return None
    
    def update_company_financials(self, symbol: str, financial_data: Dict) -> bool:
        """
        Update company financial data in MongoDB
        Args:
            symbol: Company symbol (e.g., "AAF.N0000")
            financial_data: Dictionary from TradingView
        Returns:
            bool: True if update was successful
        """
        if not financial_data:
            print(f"No data provided for {symbol}")
            return False

        try:
            # Prepare update document
            update_doc = {
                "tradingViewData.businessSummary": financial_data.get("business_description"),
                "tradingViewData.website": financial_data.get("web_site_url"),
                "tradingViewData.totalAssets": self.safe_get_first_value(financial_data.get("total_assets_fy_h")),
                "tradingViewData.totalAssetsHistoryYearly": financial_data.get("total_assets_fy_h"),
                "tradingViewData.totalAssetsHistoryQuarterly": financial_data.get("total_assets_fq_h"),
                "tradingViewData.totalLiabilities": self.safe_get_first_value(financial_data.get("total_liabilities_fy_h")),
                "tradingViewData.totalLiabilitiesHistoryYearly": financial_data.get("total_liabilities_fy_h"),
                "tradingViewData.totalLiabilitiesHistoryQuarterly": financial_data.get("total_liabilities_fq_h"),
                "tradingViewData.totalEquity": self.safe_get_first_value(financial_data.get("total_equity_fy_h")),
                "tradingViewData.totalEquityHistoryYearly": financial_data.get("total_equity_fy_h"),
                "tradingViewData.totalEquityHistoryQuarterly": financial_data.get("total_equity_fq_h"),
                "tradingViewData.totalDebt": self.safe_get_first_value(financial_data.get("total_debt_fy_h")),
                "tradingViewData.totalDebtHistoryYearly": financial_data.get("total_debt_fy_h"),
                "tradingViewData.totalDebtHistoryQuarterly": financial_data.get("total_debt_fq_h"),
                "tradingViewData.netDebt": self.safe_get_first_value(financial_data.get("net_debt_fy_h")),
                "tradingViewData.netDebtHistoryYearly": financial_data.get("net_debt_fy_h"),
                "tradingViewData.netDebtHistoryQuarterly": financial_data.get("net_debt_fq_h"),
                "tradingViewData.financialYearHistoryYearly": financial_data.get("fiscal_period_fy_h"),
                "tradingViewData.financialYearHistoryQuarterly": financial_data.get("fiscal_period_fq_h"),
                "tradingViewData.financialYearEndHistoryYearly": financial_data.get("fiscal_period_end_fy_h"),
                "tradingViewData.financialYearEndHistoryQuarterly": financial_data.get("fiscal_period_end_fq_h"),
                "tradingViewData.numberOfShares": financial_data.get("total_shares_outstanding_fy"),
                "tradingViewData.netAssetsPerShare": self.safe_get_first_value(financial_data.get("book_value_per_share_fy_h")),
                "tradingViewData.netAssetsPerShareHistoryYearly": financial_data.get("book_value_per_share_fy_h"),
                "tradingViewData.netAssetsPerShareHistoryQuarterly": financial_data.get("book_value_per_share_fq_h"),
                "tradingViewData.priceToBookValue": self.safe_get_first_value(financial_data.get("price_book_fy_h")),
                "tradingViewData.priceToBookValueHistoryYearly": financial_data.get("price_book_fy_h"),
                "tradingViewData.priceToBookValueHistoryQuarterly": financial_data.get("price_book_fq_h"),
                "tradingViewData.earningsPerShare": self.safe_get_first_value(financial_data.get("earnings_per_share_diluted_fy_h")),
                "tradingViewData.earningsPerShareHistoryYearly": financial_data.get("earnings_per_share_diluted_fy_h"),
                "tradingViewData.earningsPerShareHistoryQuarterly": financial_data.get("earnings_per_share_diluted_fq_h"),
                "tradingViewData.priceEarningsRatio": self.safe_get_first_value(financial_data.get("price_earnings_fy_h")),
                "tradingViewData.priceEarningsRatioHistoryYearly": financial_data.get("price_earnings_fy_h"),
                "tradingViewData.priceEarningsRatioHistoryQuarterly": financial_data.get("price_earnings_fq_h"),
                "tradingViewData.dividendAvailability": financial_data.get("dividends_availability"),
                "tradingViewData.dividendPerShare": self.safe_get_first_value(financial_data.get("dividend_amount_h")),
                "tradingViewData.dividendPerShareHistory": financial_data.get("dividend_amount_h"),
                "tradingViewData.dividendXdDate": self.safe_get_first_value(financial_data.get("dividend_ex_date_h")),
                "tradingViewData.dividendXdDateHistory": financial_data.get("dividend_ex_date_h"),
                "tradingViewData.dividendPaymentDate": self.safe_get_first_value(financial_data.get("dividend_payment_date_h")),
                "tradingViewData.dividendPaymentDateHistory": financial_data.get("dividend_payment_date_h"),
                "tradingViewData.dividendYield": self.safe_get_first_value(financial_data.get("dividends_yield_fy_h")),
                "tradingViewData.dividendYieldHistoryYearly": financial_data.get("dividends_yield_fy_h"),
                "tradingViewData.dividendTypeHistory": financial_data.get("dividend_type_h"),
                "lastUpdated": datetime.utcnow()
            }

            # Remove None values
            update_doc = {k: v for k, v in update_doc.items() if v is not None}

            result = self.collection.update_one(
                {"basicInfo.symbol": symbol},
                {"$set": update_doc},
                upsert=False
            )

            if result.modified_count > 0:
                return True
            else:
                print(f"No matching company found for symbol {symbol}")
                return False

        except PyMongoError as e:
            print(f"Error updating financial data for {symbol}: {e}")
            return False