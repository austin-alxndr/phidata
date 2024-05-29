from pathlib import Path
from textwrap import dedent
import os
from dotenv import load_dotenv
import datetime

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

####### ExaTool Prameter Config #######
def get_todays_date():
    """
    Returns today's date in the format YYYY-MM-DD.
    """
    today = datetime.date.today()
    return today.strftime("%Y-%m-%d")

exa_tool = ExaTools(
    start_published_date=get_todays_date(),
    num_results=5,
)

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o", temperature=0.3),
    description="You are a senior Fixed Income and Bonds researcher writing a news update article for our Indonesian clients.",
    instruction=[
        "You are to write an engaging, informative, and well-structured newsletter.",
        "You will analyze the Data Bond Benchmark on different benchmark bonds of 5Y, 10Y, 15Y, 20Y and 30Y. This will be INPUTTED BY THE USER.",
        "You will use Previous Day Bid Yield and Today Bid Yield to determine the change in Basis Points (bps).",
        "You will analyze the 'Total Daily Trading Volume' and 'Top 5 Volume Traded'. This will be INPUTTED BY THE USER and WILL ALWAYS be in Indonesian Rupiah (IDR).",
        "You will use 'Previous Total Daily Trading Volume' and 'Today Total Daily Trading Volume' and *calculate* the Percentage Change in Total Daily Trading Volume. This will be INPUTTED BY THE USER.",
        "You will use the Data Benchmark inputted by the user to determine if the bond for EACH benchmark bond strengenthed or weakened and if daily trading volume increased or decreased.",
        "The second section will include US Economic News and Indonesian Economic News.", 
        "Search EXA and return the top 3 link on EACH market.",
        "Focus on providing a high-level overview of each market and the key findings from the articles.",
        "Do not include any personal opinions or biases in the report.",
        "Include a references section for links to the articles used AT THE END of the report.",
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

            - *Total Daily Trading Volume: {total daily trading volume}*

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
    markdown=True,
    tools=[exa_tool],
    debug_mode=True,
    save_output_to_file=str(scratch_dir.joinpath("sucor_fi_test.md")),
)

assistant.print_response(
    """
    Bond Benchmark	Details	Previous Day Bid Price	Previous Day Ask Price	Previous Day Bid Yield	Previous Day Ask Yield	Today's Bid Price	Today's Ask Price	Today's Bid Yield	Today's Ask Yield	Change in bps
FR0101	5Y Benchmark SUN	99.95	100.05	6.88%	6.86%	100.05	100.15	6.86%	6.84%	-0.02%
FR0100	10Y Benchmark SUN	98.10	98.25	6.89%	6.87%	98.1	98.2	6.89%	6.88%	0.00%
FR0098	15Y Benchmark SUN	101.00	101.70	7.01%	6.93%	101.6	101.7	6.94%	6.93%	-0.07%
FR0097	20Y Benchmark SUN	101.35	101.60	7.00%	6.98%	101.45	101.85	6.99%	6.95%	-0.01%
FR0102	30Y Benchmark SUN	98.50	99.00	6.99%	6.95%	98.35	98.7	7.01%	6.98%	0.02%

	Previous Total Daily Trading Volume	Today Total Daily Trading Volume
Total Daily Trading Volume	12.624 tn	20.484 tn
Top 5 Bonds Traded		
FR0100	7.416 tn	
FR0101	4.655 tn	
FR0081	1.745 tn	
FR0097	662 bn	
FR0102	525 bn	
    """
)