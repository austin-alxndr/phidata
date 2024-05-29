from pathlib import Path
from textwrap import dedent

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.exa import ExaTools

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

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

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o"),
    tools=[exa_tool],
    description="You are a senior Asset Management researcher writing a news update article for clients.",
    instruction=[
        "You are to write an engaging, informative, and well-structured newsletter.",
        "The first section will include a Data Benchmark section on different global indexes and asset classes from different countries. This will be INPUTTED BY THE USER.",
        "Make sure to include headers for the Data Benchmarks. This will be inputted BY THE USER.",
        "You will use the Data Benchmark INPUTTED BY THE USER to determine if the stock market for each Market strengenthed or weakened.",
        "The second section will also include news on US Markets, Asia Markets, and Indonesian Markets. Search for the top 1 links on EACH market.",
        "Start each sub market section with stating if the stock market strengthened or weakened."
        "Focus on providing a high-level overview of each market and the key findings from the articles.",
        "Do not include any personal opinions or biases in the report.",
        "Include a references section for links to the articles used in the report AT THE END of the report.",
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
            {Bursa US mengalami penguatan/penurunan X.XX%... }
            {provide summary and key takeaways from article regarding US market news}

            *Asia Market News*
            {Bursa Asia mengalami penguatan/penurunan X.XX%... }
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
    debug_mode=True,
    save_output_to_file=str(scratch_dir.joinpath("sucor_am_test.md")),
)

assistant.print_response(
    """
Last Price	Price Change 1 Day Percent
		PX_LAST	CHG_PCT_1D
UNITED STATES	S&P 500	 5,304.72 	0.00%
UNITED STATES	Dow Jones	 39,069.59 	0.00%
UNITED STATES	Nasdaq	 16,920.79 	0.00%
UNITED STATES	S&P 500 VIX	 12.36 	3.60%
EUROPE	Euro Stoxx 50	 5,059.20 	0.47%
EUROPE	DAX	 18,774.71 	0.44%
EUROPE	FTSE 100	 8,317.59 	0.00%
ASIA	Nikkei 225	 38,900.02 	0.66%
ASIA	Hang Seng	 18,827.35 	1.17%
ASIA	Shanghai	 3,124.04 	1.14%
INDONESIA	IDX Composite	 7,176.42 	-0.64%
INDONESIA	IDX LQ45	 889.80 	-0.68%
INDONESIA	iShares MSCI Indonesia	 20.50 	0.00%
BONDS	U.S. 10Y	 4.47 	0.00%
BONDS	Indonesia 10Y	 6.94 	0.00%
COMMODITIES & OTHERS	Crude Oil WTI	 77.72 	0.00%
COMMODITIES & OTHERS	Gold	 2,350.97 	0.73%
COMMODITIES & OTHERS	US Dollar Index	 104.60 	-0.12%
COMMODITIES & OTHERS	USD/IDR	 16,065.00 	0.45%
    """
)