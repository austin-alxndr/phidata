import os
import streamlit as st

from typing import Optional, List, Dict, Any
from textwrap import dedent
from dotenv import load_dotenv
from pathlib import Path
import datetime

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

####### ExaTool Prameter Config #######
def get_date_7_days_ago():
    """
    Returns the date 7 days ago from today.
    
    Returns:
    str: The date in the format YYYY-MM-DD.
    """
    today = datetime.date.today()
    target_date = today - datetime.timedelta(days=7)
    return target_date.strftime("%Y-%m-%d")

exa_tool = ExaTools(
    start_published_date=get_date_7_days_ago(),
)

################ Assistant ################

def get_fi_assisant(
    llm_model: str = "gpt-4o",
    user_id: Optional[str] = None,
    run_id: Optional[str] = None,
    debug_mode: bool = True,
) -> Assistant:
    """Get an FI Assistant."""

    return Assistant(
        name="auto_rag_assistant",
        run_id=run_id,
        user_id=user_id,
        llm=OpenAIChat(model=llm_model),
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
        description="You are a senior Fixed Income and Bonds researcher writing a news update article for our Indonesian clients.",
        instruction=[
        "You are to write an engaging, informative, and well-structured newsletter.",
        "You will analyze the Data Bond Benchmark on different benchmark bonds of 5Y, 10Y, 15Y, 20Y and 30Y. This will be INPUTTED BY THE USER.",
        "You will use Previous Day Bid Yield and Today Bid Yield to determine the change in Basis Points (bps).",
        "You will analyze the 'Total Daily Trading Volume' and 'Top 5 Volume Traded'. This will be INPUTTED BY THE USER and WILL ALWAYS be in Indonesian Rupiah (IDR).",
        "You will use 'Previous Total Daily Trading Volume' and 'Today Total Daily Trading Volume' and *calculate* the Percentage Change in Total Daily Trading Volume. This will be INPUTTED BY THE USER.",
        "You will use the Data Benchmark inputted by the user to determine if the bond for EACH benchmark bond strengenthed or weakened and if daily trading volume increased or decreased.",
        "The second section will include US Economic News and Indonesian Economic News.", 
        "You will only Search EXA and US and Indonesian Economic News and return FIRST top link.",
        "Focus on providing a high-level overview of each market and the key findings from the articles.",
        "Do NOT include any personal opinions or biases in the report.",
        "Do NOT include information that you have been trained on.",
        "Include a references section for links to the articles used AT THE END of the report.",
        "IMPORTANT: You will output the news article in the Bahasa Indonesia language."
        ],
        expected_output=dedent(
            """\
            Artikel yang menarik, informatif, dan terstruktur dengan baik dalam format berikut:
            <article_format>
            ## *Sucor Fixed Income News Update*
            ## *{today's date}*

            *Overview*
            {give a brief overview of the current bond market using Data Benchmark inputted}

            *Data Analysis - Obligasi*
            {input each bond benchmark data from the user here in sentences}
            - Yield FR0101 (5Y Benchmark SUN) jatuh {change in Basis Points} bps menajdi {today bid yield}.
            - Yield FR0100 (10Y Benchmark SUN) jatuh {change in Basis Points} bps menajdi {today bid yield}.
            - Yield FR0098 (15Y Benchmark SUN) jatuh {change in Basis Points} bps menajdi {today bid yield}.
            - Yield FR0097 (20Y Benchmark SUN) jatuh {change in Basis Points} bps menajdi {today bid yield}.
            - Yield FR0102 (30Y Benchmark SUN) jatuh {change in Basis Points} bps menajdi {today bid yield}.
    
            *Data Benchmark - Obligasi*
            {input the benchmark data from the user here in a nice clean bullet point format}
            {Today's Closing Price and Yield}
            - _FR0101 (5Y Benchmark SUN)_ : {today bid price} / {today ask price}
            - _FR0100 (10Y Benchmark SUN)_ : {today bid price} / {today ask price}
            - _FR0098 (15Y Benchmark SUN)_ : {today bid price} / {today ask price}
            - _FR0097 (20Y Benchmark SUN)_ : {today bid price} / {today ask price}
            - _FR0102 (30Y Benchmark SUN)_ : {today bid price} / {today ask price}

            - _FR0101 (5Y Benchmark SUN)_ : {today bid yield} / {today ask yield}
            - _FR0100 (10Y Benchmark SUN)_ : {today bid yield} / {today ask yield}
            - _FR0098 (15Y Benchmark SUN)_ : {today bid yield} / {today ask yield}
            - _FR0097 (20Y Benchmark SUN)_ : {today bid yield} / {today ask yield}
            - _FR0102 (30Y Benchmark SUN)_ : {today bid yield} / {today ask yield}

            *Total Daily Trading Volume: {total daily trading volume} {percentage change in daily trading volume vs. previous day volume}*

            {Top 5 Bonds Traded:}
            - FR0098: IDR x.xxx TN
            - FR0101: IDR x.xxx TN
            - FR0056: IDR xxx BN

            ...more bonds traded as necessary...

            *US Macroeconomic News*
            {provide summary and key takeaways from article regarding US macroeconomic news}

            *Indonesian Macroeconomic News*
            {provide summary and key takeaways from article regarding Indonesian macroeconomic news}
            
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
