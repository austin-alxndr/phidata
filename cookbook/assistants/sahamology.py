import json
import requests

from phi.assistant import Assistant
# from phi.llm.groq import Groq
from phi.llm.openai import OpenAIChat

import json
import httpx
from typing import List, Dict, Any

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

    url = "https://sucor.sahamology.id/signal" 
    payload = {
        'id': "846765",
        'key': "SUCOR-z2m5d23a-r1h6-r3o3-gw0k-wetuibdjhkjah",     
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
    

assistant = Assistant(
    llm=OpenAIChat(model="gpt-3.5-turbo"),
    description='You are an AI Trading Assistant capable of helping clients with their trading goals.',
    instructions=['Also add that this is not financial advice.'],
    tools=[get_signals_status], 
    show_tool_calls=False, 
    markdown=True, 
    debug_mode=True
)
assistant.print_response("What is today's fresh buy signalcls?")
