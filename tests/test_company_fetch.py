from src.fetch_companies import fetch_all_company_codes

company_codes = fetch_all_company_codes()
if company_codes:
    print(f"Received {len(company_codes)} company codes\n")
    
    # Print first 5 company codes
    print("First 5 company codes:")
    print("-" * 40)
    for i, company in enumerate(company_codes[:5], 1):
        print(f"{i}. {company['symbol']}: {company['name']} (ID: {company['id']})")
    
    # Print last 5 company codes
    print("\nLast 5 company codes:")
    print("-" * 40)
    for i, company in enumerate(company_codes[-5:], len(company_codes) - 4):
        print(f"{i}. {company['symbol']}: {company['name']} (ID: {company['id']})")
else:
    print("Failed to fetch company codes")