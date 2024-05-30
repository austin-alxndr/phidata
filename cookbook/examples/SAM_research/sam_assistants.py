from pathlib import Path
from textwrap import dedent
import datetime

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.exa import ExaTools

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)


def get_todays_date():
    """
    Returns today's date in the format YYYY-MM-DD.
    """
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")

exa_tool = ExaTools(
    start_published_date=get_todays_date(),
)

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o"),
    tools=[exa_tool],
    description="You are a senior Asset Management researcher writing a news update article for clients.",
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
    add_datetime_to_instructions=True,
    expected_output=dedent(
            """\
            Artikel yang menarik, informatif, dan terstruktur dengan baik dalam format berikut:

            <article_format>
            *Sucor AM News Update*
            *{today's date}*

            *Data Benchmark*
            {input the benchmark data from the user here in a nice clean bullet point format}

            *US Market News*
            {Bursa US mengalami penguatan/penurunan X.XX%... }

            *Asia Market News*
            {Bursa Asia mengalami penguatan/penurunan X.XX%... }

            *Indonesian Market News*
            {Kemarin, JCI mengalami penurunan X.XX%... }

            <article_format>\
        """),
    markdown=True,
    save_output_to_file=str(scratch_dir.joinpath("sucor_am_test.md")),
)

assistant.print_response(
    """
Last Price Price Change 1 Day Percent PX_LAST CHG_PCT_1D UNITED STATES S&P 500 5,266.95 -0.74% UNITED STATES Dow Jones 38,441.54 -1.06% UNITED STATES Nasdaq 16,920.58 -0.58% UNITED STATES S&P 500 VIX 14.28 10.53% EUROPE Euro Stoxx 50 4,963.20 -1.33% EUROPE DAX 18,473.29 -1.10% EUROPE FTSE 100 8,183.07 -0.86% ASIA Nikkei 225 38,556.87 -0.77% ASIA Hang Seng 18,477.01 -1.83% ASIA Shanghai 3,111.02 0.05% INDONESIA IDX Composite 7,140.23 -1.56% INDONESIA IDX LQ45 886.18 -1.62% INDONESIA iShares MSCI Indonesia 19.96 -2.30% BONDS U.S. 10Y 4.61 1.36% BONDS Indonesia 10Y 6.94 0.13% COMMODITIES & OTHERS Crude Oil WTI 79.23 -0.75% COMMODITIES & OTHERS Gold 2,338.12 -0.98% COMMODITIES & OTHERS US Dollar Index 105.12 0.49% COMMODITIES & OTHERS USD/IDR 16,160.00 0.44%

    """
)