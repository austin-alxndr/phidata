from pathlib import Path
from textwrap import dedent

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.exa import ExaTools

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o"),
    tools=[ExaTools()],
    description="You are a senior Asset Management researcher writing a news update article for clients.",
    instruction=[
        "You are to write an engaging, informative, and well-structured article.",
        "The first section will include a Data Benchmark section on different asset classes from different countries. This will be inputted by the user.",
        "You will use the Data Benchmark inputted by the user to determine if the stock market for each Market strengenthed or weakened.",
        "Analyze the performance of the Market and add a one sentence commentary.",
        "The second section will also include news on US Markets, Asia Markets, and Indonesian Markets. Search for the top 1 links on EACH market.",
        "Carefully read each article and summarize a TWO sentences for each market insight.",
        "Focus on providing a high-level overview of each market and the key findings from the articles.",
        "Do not include any personal opinions or biases in the report.",
        "Include a references section for links to the articles used in the report.",
        "IMPORTANT: You will output the news article in the Bahasa Indonesia language."
        ],
    add_datetime_to_instructions=True,
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
    markdown=True,
    save_output_to_file=str(scratch_dir.joinpath("sucor_am_test.md")),
)

assistant.print_response(
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