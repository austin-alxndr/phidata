from pathlib import Path

from phi.assistant.python import PythonAssistant
from phi.llm.openai import OpenAIChat
from phi.file.local.csv import CsvFile

cwd = Path(__file__).parent.resolve()
scratch_dir = cwd.joinpath("scratch")
if not scratch_dir.exists():
    scratch_dir.mkdir(exist_ok=True, parents=True)

python_assistant = PythonAssistant(
    llm=OpenAIChat(model="gpt-4o"),
    base_dir=scratch_dir,
    files=[
        CsvFile(
            path="local_files/username.csv",
            description="Contains information about Usernames.",
        )
    ],
    pip_install=True,
    show_tool_calls=True,
)

python_assistant.print_response("How many rows are there in the file?", markdown=True)
