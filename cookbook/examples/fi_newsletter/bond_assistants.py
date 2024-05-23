from pathlib import Path
from textwrap import dedent
import os
from dotenv import load_dotenv

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.exa import ExaTools

# load_dotenv()

# os.environ["OPENAI_API_KEY"] = os.getenv["OPENAI_API_KEY"]
# os.environ["EXA_API_KEY"] = os.getenv["EXA_API_KEY"]

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o"),
    tools=[ExaTools()],
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
    add_datetime_to_instructions=True,
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
    markdown=True,
    save_output_to_file=str(scratch_dir.joinpath("sucor_fi_test.md")),
)

assistant.print_response(
    """
    Bond Benchmark	Details	Previous Day Bid Price	Previous Day Ask Price	Previous Day Bid Yield	Previous Day Ask Yield	Today's Bid Price	Today's Ask Price	Today's Bid Yield	Today's Ask Yield
FR0101	5Y Benchmark SUN	101.30	101.35	6.57%	6.55%	101.35	101.4	6.56%	6.53%
FR0100	10Y Benchmark SUN	99.70	99.85	6.67%	6.64%	99.75	99.9	6.65%	6.62%
FR0098	15Y Benchmark SUN	102.40	102.50	6.86%	6.85%	102.45	102.55	6.85%	6.83%
FR0097	20Y Benchmark SUN	102.00	102.30	6.93%	6.91%	102.05	102.35	6.91%	6.89%
FR0102	30Y Benchmark SUN	99.35	99.50	6.93%	6.91%	99.4	99.55	6.91%	6.89%

Total Daily Trading Volume	IDR 10.93 tn
Top 5 Bonds Traded	
FR0098	1.175 tn
FR0101	1.152 tn
FR0056	762 bn
FR0100	396 bn
FR0081	350 bn

    """
)