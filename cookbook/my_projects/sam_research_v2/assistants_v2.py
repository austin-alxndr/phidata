import os
import streamlit as st

from typing import Optional, List, Dict, Any
from textwrap import dedent
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel, Field

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.exa import ExaTools

class WebSearchResult(BaseModel):
    title: str = Field(..., description="Title of the article.")
    summary: str = Field(..., description="Summary from the article.")
    links: List[str] = Field(..., description="Links for the article.")
    reasoning: str = Field(..., description="Clear description of why you chose this article from the results.")

class WebSearchResults(BaseModel):
    results: List[WebSearchResult] = Field(..., description="List of top search results.")

us_news = Assistant(
    name="US Market Research Analyst",
    llm=OpenAIChat(model='gpt-4o'),
    role="Get current news on US markets, specifically in regards to the S&P 500, NASDAQ, and Dow Jones.",
    tools=[
        ExaTools(),
    ],
    description="You are a economic and market research analyst tasked with producing a single paragraph of news on the US markets that covers S&P 500, NASDAQ, and Dow Jones.",
    instructions=[
        "You will search the most RECENT NEWS on the US Stock Market.",
        "Search using Exa for the top 3 most recent articles about the US Stock Market and return the 1 most recent article.",
        "You should return the article title, summary, and the content of the article.",
        "This is an important task and your output should be highly relevant and most recent to the US Stock Market.",
    ],
    output_model=WebSearchResults,
    add_datetime_to_instructions=True,
    debug_mode=True
)

newsletter_editor = Assistant(
    name="Newsletter Editor",
    llm=OpenAIChat(model='gpt-4o'),
    team=[us_news],
    description="You are a senior Asset Management newsletter editor writing a newsletter update for clients in Indonesia.",
    instructions=[
        "You are to write an engaging, informative, and well-structured article.",
        "The first section will include a Data Benchmark section on different asset classes from different countries. This will be inputted BY THE USER.",
        "Make sure to include headers for the Data Benchmarks. This will be inputted BY THE USER.",
        "You will use the Data Benchmark inputted by the user to determine if the stock market for each Market strengenthed or weakened.",
        "Analyze the performance of the Market and add a one sentence commentary.",
        "Ask the US News Market Research Analyst to provide you with a list of articles along with their summary and content.",
        "Focus on providing a high-level overview of the topic and the key findings from the articles.",
        "Do not copy the content from the articles, but use the information to generate a high-quality report.",
        "Do not include any personal opinions or biases in the report.",
        "Include a references section for links to the articles used in the report.",
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
        
        *References*
        - [Title](url)
        - [Title](url)
        - [Title](url)
        <article_format>\
        """),
    add_datetime_to_instructions=True,
    markdown=True
)

newsletter_editor.print_response(
    """
    *UNITED STATES*

S&P 500      5303.27     +0.12%
Dow Jones    40003.59    +0.34%
Nasdaq       16685.97    -0.07%
VIX Index    12.24       +2.09%


*EUROPE*

SX5E Index   5067.17     +0.06%
DAX Index    18748.83    +0.24%
UKX Index    8441.57     +0.25%


*ASIA*

NKY Index    39069.68    +0.73%
HSI Index    19598.65    +0.23%
SHCOMP Index 3171.45     +0.54%


*INDONESIA*

JCI Index    7267.78     -0.68%
LQ45 Index   910.51      -0.98%
EIDO US Eq   21.3        +1.33%


*BONDS*

USGG10YR     4.4218
GIDN10YR     6.935


*COMMODITIES & OTHERS*

CL1 Comdty   80.23
XAU Curncy   2441.57     +1.09%
DXY Curncy   104.465     +0.02%
USDIDR Curncy15975      -0.13%
    """
)