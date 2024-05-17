from phi.assistant import Assistant
# from phi.llm.openai import OpenAIChat
# from phi.llm.ollama import Ollama
from phi.llm.groq import Groq


assistant = Assistant(
    # llm=OpenAIChat(model="gpt-4o"),
    # llm=Ollama(model='llama3'),
    llm=Groq(model='llama3-70b-8192'),
    description="You help business owners figure out data analytical or business intelligence questions to ask.",
    # instructions=["Recipes should be under 5 ingredients"],
)
# -*- Print a response to the cli
assistant.print_response("Give me 3 prommpts I can ask an Pandas AI Agent", markdown=True)
