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
        "You will analyze the Data Bond Benchmark on different benchmark bonds of 5Y, 10Y, 15Y, 20Y and 30Y and its change in bps as well as daily percentage change. This will be inputted by the user.",
        "You will analyze the volume of daily trading and the top 5 volume traded bonds. This will be inputted by the user.",
        "You will use the Data Benchmark inputted by the user to determine if the bond for each benchmark strengenthed or weakened and if daily trading volume increased or decreased.",
        "Analyze the performance of the Market and add a one sentence commentary for each Bond Benchmark. Example: Benchmark Bond 5Y (FR0101) mengalami penguatan 0.6 bps dan sekarang berada di level yield 6.70% (vs. 6.63% kemarin).",
        "The second section will include US Macroeconomic News, Asia Macroeconomic News, and Indonesian Macroeconomic News. Search for the top 1 link on EACH market.",
        "Carefully read each article and summarize a max TWO sentences for each market insight.",
        "Focus on providing a high-level overview of each market and the key findings from the articles.",
        "Do not include any personal opinions or biases in the report.",
        "Include a references section for links to the articles used in the report.",
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

            - *Total Daily Trading Volume: {total daily trading volume}*

            {Top 5 Bonds Traded:}
            - FR0098: IDR x.xxx TN
            - FR0101: IDR x.xxx TN
            - FR0056: IDR xxx BN

            ...more bonds traded as necessary...

            *US Macroeconomic News*
            {provide summary and key takeaways from article regarding US macroeconomic news}

            *Asia Macroeconomic News*
            {provide summary and key takeaways from article regarding Asia macroeconomic news}

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
        tools=[ExaTools()],
        # This setting tells the LLM to format messages in markdown
        markdown=True,
        # Adds chat history to messages
        add_chat_history_to_messages=True,
        add_datetime_to_instructions=True,
        # save_output_to_file=str(scratch_dir.joinpath("new_article.md")),
        debug_mode=debug_mode,
    )
