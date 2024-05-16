from pathlib import Path
from textwrap import dedent

from phi.assistant import Assistant
from phi.llm.openai import OpenAIChat
from phi.tools.yfinance import YFinanceTools

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

assistant = Assistant(
    llm=OpenAIChat(model="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True, company_news=True)],
    # show_tool_calls=True,
    markdown=True,
    save_output_to_file=str(scratch_dir.joinpath("new_report.md"))
)
# assistant.print_response("What is the stock price of NVDA")
assistant.print_response("Write a comparison between NVDA and AMD, use all tools available.")
