from typing import Optional, List, Dict, Any
import json
import httpx
import os
from dotenv import load_dotenv

from phi.assistant import Assistant
from phi.knowledge import AssistantKnowledge
from phi.llm.openai import OpenAIChat
from phi.tools.duckduckgo import DuckDuckGo
from phi.embedder.openai import OpenAIEmbedder
from phi.vectordb.pgvector import PgVector2
from phi.knowledge.pdf import PDFUrlKnowledgeBase
from phi.knowledge.pdf import PDFKnowledgeBase
from phi.storage.assistant.postgres import PgAssistantStorage

# Load environment variables from the .env file
load_dotenv()
S_INFO_URL = os.getenv("S_INFO_URL")
S_SIGNALS_URL = os.getenv("S_SIGNALS_URL")
S_API_ID = os.getenv("S_API_ID")
S_API_KEY = os.getenv("S_API_KEY")

################ Vector Database ################

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# knowledge_base = PDFUrlKnowledgeBase(
#     urls=["https://phi-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
#     vector_db=PgVector2(collection="recipes", db_url=db_url),
# )
# # Comment out after first run
# knowledge_base.load(recreate=False)

knowledge_base = PDFKnowledgeBase(
    path="cookbook/examples/sahamology_bot/faq_nasabah.pdf",
    vector_db=PgVector2(collection="report", db_url=db_url),
    embedder=OpenAIEmbedder(model="text-embedding-ada-002", dimensions=1536),
)
# Comment out after first run
knowledge_base.load(recreate=False)

storage = PgAssistantStorage(
    table_name="pdf_assistant", 
    db_url=db_url
)


################ Custom Tools ################
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

################ Assistant ################

def get_auto_rag_assistant(
    llm_model: str = "gpt-4-turbo",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    """Get an Auto RAG Assistant."""

    return Assistant(
        name="auto_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(model=llm_model),
        # storage=PgAssistantStorage(table_name="auto_rag_assistant_openai", db_url=db_url),
        storage=storage,
        # knowledge_base=AssistantKnowledge(
        #     vector_db=PgVector2(
        #         db_url=db_url,
        #         collection="auto_rag_documents_openai",
        #         embedder=OpenAIEmbedder(model="text-embedding-3-small", dimensions=1536),
        #     ),
        #     # 3 references are added to the prompt
        #     num_documents=3,
        # ),
        knowledge_base=knowledge_base,
        description="You are a helpful Assistant called 'QuantAI' and your goal is to assist the user in the best way possible.",
        instructions=[
            "Given a user query, first ALWAYS search your knowledge base using the `search_knowledge_base` tool to see if you have relevant information.",
            "If you need to get trading signals, use the `get_signal_status` tool.",
            "If you need to get trading info of a company, use the `get_trading_info` tool.",
            "If you need to get investment or financial ratio information of a company, use the 'get_invest_info' tool.",
            "If you output any information related to financial advice, be sure to add a warning saying that this is not financial advice and should be treated with caution.",
            "If you dont find relevant information in your knowledge base, use the `duckduckgo_search` tool to search the internet.",
            "If you need to reference the chat history, use the `get_chat_history` tool.",
            "If the users question is unclear, ask clarifying questions to get more information.",
            "Carefully read the information you have gathered and provide a clear and concise answer to the user.",
            "Do not use phrases like 'based on my knowledge' or 'depending on the information'.",
        ],
        # Show tool calls in the chat
        show_tool_calls=True,
        # This setting gives the LLM a tool to search the knowledge base for information
        search_knowledge=True,
        # This setting gives the LLM a tMom ool to get chat history
        read_chat_history=True,
        tools=[DuckDuckGo(), get_signals_status, get_trading_info, get_invest_info],
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # Adds chat history to messages
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        debug_mode=debug_mode,
    )
