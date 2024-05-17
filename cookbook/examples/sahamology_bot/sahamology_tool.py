import json
import os
from dotenv import load_dotenv

from phi.assistant import Assistant
# from phi.llm.groq import Groq
from phi.llm.openai import OpenAIChat

import json
import httpx
from typing import List, Dict, Any

# Load environment variables from the .env file
load_dotenv()
S_INFO_URL = os.getenv("S_INFO_URL")
S_SIGNALS_URL = os.getenv("S_SIGNALS_URL")
S_API_ID = os.getenv("S_API_ID")
S_API_KEY = os.getenv("S_API_KEY")

## Get signals status from API function ##
def get_signals_status(status: str) -> str:
    """
    Fetches the first three stock signals for a given status from the API and returns it with specific, renamed keys.
    Nominal values are in Indonesian rupiah. 

    Args:
        status (str): User status of the signal (e.g., 'fresh buy', 'fresh sell', 'positif', 'negatif').

    Returns:
        str: JSON string of the processed signals.
    """

    # Fixed desired keys with their new names
    key_mappings = {
        'kode': 'ticker',
        'plantp1': 'take-profit-1',
        'plantp2': 'take-profit-2',
        'plancl': 'cut-loss-1',
        'plancl2': 'cut-loss-2',
        'planskenario': 'scenario'
    }

    url = S_SIGNALS_URL 
    payload = {
        'id': S_API_ID,
        'key': S_API_KEY,     
        'short': 'volume',
        'status': status
    }
    headers = {}

    response = httpx.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            json_response = response.json()
            signals = json_response.get("signal", [])
            if signals:
                # Get up to the first three signals from the list
                first_three_signals = signals[:3]
                # Process each of the first three signals
                processed_signals = [
                    {new_key: signal.get(old_key, None) for old_key, new_key in key_mappings.items()}
                    for signal in first_three_signals
                ]
                return json.dumps(processed_signals)
            else:
                return json.dumps({"message": "No signals found"})
        except ValueError:  # JSONDecodeError in Python 3.5+
            return json.dumps({"error": "Error decoding JSON response"})
    else:
        return json.dumps({"error": f"API request failed with status code: {response.status_code}"})


## Get trading info of TICKER from API function ##
def get_trading_info(ticker: str) -> str:
    """
    Fetches trading information or technical analysis for a specific public company using the ticker symbol. 

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        str: JSON string of the trading information.
    """

    url = S_INFO_URL 
    payload = {
        'id': S_API_ID,      
        'key': S_API_KEY,    
        'pesan': f'#{ticker}'  
    }
    headers = {}

    response = httpx.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            json_response = response.json()
            result = json_response.get("result", "No signals found")
            return json.dumps(result)
        except ValueError as e:  # More specific exception handling
            return json.dumps({"error": f"Error decoding JSON response: {e}"})
    else:
        return json.dumps({"error": f"API request failed with status code: {response.status_code}"})

## Get investment info of TICKER from API function ## 
def get_invest_info(ticker: str) -> str:
    """
    Fetches financial ratio information and investment analysis for a specific public company.

    Args:
        ticker (str): Stock ticker symbol.

    Returns:
        str: JSON string of the investment information.
    """

    url = S_INFO_URL  
    payload = {
        'id': S_API_ID,      
        'key': S_API_KEY,    
        'pesan': f'invest #{ticker}'  
    }
    headers = {}

    response = httpx.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            json_response = response.json()
            result = json_response.get("result", "No signals found")
            return json.dumps(result)
        except ValueError as e:  # More specific exception handling
            return json.dumps({"error": f"Error decoding JSON response: {e}"})
    else:
        return json.dumps({"error": f"API request failed with status code: {response.status_code}"})

## Assistant Creation ##

assistant = Assistant(
    llm=OpenAIChat(model="gpt-3.5-turbo"),
    description='You are an AI Trading Assistant capable of helping clients with their trading goals.',
    instructions=['Also add that this is not financial advice.'],
    tools=[get_signals_status, get_trading_info, get_invest_info], 
    show_tool_calls=False, 
    markdown=True, 
    debug_mode=True
)
assistant.print_response("What is the trading information for EXCL?")
# assistant.print_response("Analisa investasi apa yang bisa diberikan dari saham Bank Central Asia?")