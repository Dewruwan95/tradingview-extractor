# TradingView WebSocket Data Extractor

Last Updated : January 12, 2026

A Python tool to extract financial data from TradingView using WebSocket connections.

## Features

- Connect to TradingView's WebSocket API
- Send predefined message sequences
- Receive and parse real-time market data
- Handle large financial data messages
- Log all communication for debugging

## Prerequisites

- Python 3.7+
- pip package manager

## Installation

1. Create a virtual environment:

   `python3 -m venv venv`

2. Activate virtual environment:
   ##### On macOS/Linux:
   `source venv/bin/activate`
   ##### On Windows:
   `venv\Scripts\activate`
3. To install from an existing requirements file:

   `pip3 install -r requirements.txt`

4. To generate a new requirements file (after adding new packages):

   `pip3 freeze > requirements.txt`

5. This will scan your imports and generate a clean requirements.txt

   `pip3 install pipreqs pipreqs ./ --force`

6. Run test_financial_sync.py

   `python3 -m tests.test_financial_sync`
