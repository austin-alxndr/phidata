import os
import streamlit as st

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
# os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
# os.environ["EXA_API_KEY"] = st.secrets["EXA_API_KEY"]

# ---- ExaTool Config ----
import datetime

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
        llm=OpenAIChat(model=llm_model, temperature=0),
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
            "You are to write an engaging, informative, and well-structured article.",
            "The first section will include a Data Benchmark section on different asset classes from different countries. This will be inputted BY THE USER.",
            "Make sure to include headers for the Data Benchmarks. This will be inputted BY THE USER.",
            "You will use the Data Benchmark inputted by the user to determine if the stock market for each Market strengenthed or weakened.",
            "Analyze the performance of the Market and add a one sentence commentary.",
            "The second section will also include news on US Markets, Asia Markets, and Indonesian Markets. Search for the top 10 links on EACH market.",
            "Return 1 link and it should be the MOST RECENT link to date.",
            "The article should be the MOST recent article based on today's date.",
            "Carefully read each article and summarize a TWO sentences for each market insight.",
            "Focus on providing a high-level overview of each market and the key findings from the articles.",
            "Do not include any personal opinions or biases in the report.",
            "Include a references section for links to the articles used in the report.",
            "IMPORTANT: You will output the news article in the Bahasa Indonesia language."
        ],
        expected_output=dedent(
        """\
        Artikel yang menarik, informatif, dan terstruktur dengan baik dalam format berikut:
        <article_format>
        ## *Sucor AM News Update*
        ## *{today's date}*

        *Data Benchmark*
        {input the benchmark data from the user here in a nice clean bullet point format}

        *US Market News*
        {Bursa US menguat... }
        {provide summary and key takeaways from article regarding US market news}

        *Asia Market News*
        {Bursa Asia menguat... }
        {provide summary and key takeaways from article regarding Asia market news}

        *Indonesian Market News*
        {Kemarin, JCI mengalami penurunan X.XX%... }
        {provide summary and key takeaways from article regarding Indonesian market news}
        
        *References*
        - [Title](url)
        - [Title](url)
        - [Title](url)
        <article_format>\
        """),
        # This setting gives the LLM a tMom ool to get chat history
        read_chat_history=True,
        tools=[exa_tool],
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # Adds chat history to messages
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        # save_output_to_file=str(scratch_dir.joinpath("new_article.md")),
        debug_mode=debug_mode,
    )
