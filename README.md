# TradingView WebSocket Data Extractor

Last Updated : December 29, 2025

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

1. To install from an existing requirements file:

   `pip3 install -r requirements.txt`

2. To generate a new requirements file (after adding new packages):

   `pip3 freeze > requirements.txt`

3. This will scan your imports and generate a clean requirements.txt

   `pip3 install pipreqs pipreqs ./ --force`

4. Run test_financial_sync.py

   `python3 -m tests.test_financial_sync`
