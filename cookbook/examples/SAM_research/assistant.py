import os
import streamlit as st
import datetime

from typing import Optional, List, Dict, Any
from textwrap import dedent
from dotenv import load_dotenv
from pathlib import Path

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
# from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.exa import ExaTools

####### Path to save MD file #######

# cwd = Path(__file__).parent.resolve()
# scratch_dir = cwd.joinpath("scratch")
# if not scratch_dir.exists():
#     scratch_dir.mkdir(exist_ok=True, parents=True)

####### Enviroment Import for API Keys ######
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["EXA_API_KEY"] = st.secrets["EXA_API_KEY"]

####### ExaTool Prameter Config #######
def get_todays_date():
    """
    Returns today's date in the format YYYY-MM-DD.
    """
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")

exa_tool = ExaTools(
    start_published_date=get_todays_date(),
)

################ Assistant ################

def get_sam_assisant(
    llm_model: str = "gpt-4o",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    """Get an Auto RAG Assistant."""

    return Assistant(
        name="auto_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(model=llm_model,temperature=0),
        # storage=PgAssistantStorage(table_name="auto_rag_assistant_openai", db_url=db_url),
        # knowledge_base=AssistantKnowledge(
        #     vector_db=PgVector2(
        #         db_url=db_url,
        #         collection="auto_rag_documents_openai",
        #         embedder=OpenAIEmbedder(model="text-embedding-3-small", dimensions=1536),
        #     ),
        #     # 3 references are added to the prompt
        #     num_documents=3,
        # ),
        description="You are a senior Asset Management researcher writing a news update article for clients in Indonesia.",
        instruction=[
            "You are to write an engaging, informative, and well-structured newsletter.",
            "The first section will include a Data Benchmark section on different asset classes from different countries. This will be INPUTTED BY THE USER.",
            "Make sure to include headers for the Data Benchmarks. This will be INPUTTED BY THE USER.",
            "You will use the Data Benchmark INPUTTED BY THE USER to determine if the stock market for each Market strengthened or weakened.",
            "Start each sub market section with stating if the stock market strengthened or weakened.",
            "Do not include any personal opinions or biases in the report.",
            "Include a references section for links to the articles used AT THE END of the report.",
            "IMPORTANT: You will output the news article in the Bahasa Indonesia language."
        ],
        expected_output=dedent(
            """\
            Artikel yang menarik, informatif, dan terstruktur dengan baik dalam format berikut:

            <article_format>
            *Sucor AM News Update*
            *{today's date in written format}*

            *Data Benchmark*
            {input the benchmark data from the user here in a nice clean bullet point format}
            - *US Market*:
                - S&P 500: xxxx (-x.xx%)
                - Dow Jones: xxxx (-x.xx%)
            
            ...more indexes with headers here...

            *US Market News*
            {Bursa US mengalami penguatan/penurunan X.XX%... }

            *Asia Market News*
            {Bursa Asia mengalami penguatan/penurunan X.XX%... }

            *Indonesian Market News*
            {Kemarin, JCI mengalami penurunan X.XX%... }

            <article_format>\
        """),
        # This setting gives the LLM a tool to get chat history
        read_chat_history=True,
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # Adds chat history to messages
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        # save_output_to_file=str(scratch_dir.joinpath("new_article.md")),
        debug_mode=debug_mode,
    )
