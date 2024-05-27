import streamlit as st
from pathlib import Path
from phi.assistant.python import PythonAssistant
from phi.llm.openai import OpenAIChat
from phi.file.local.csv import CsvFile
import io
import contextlib

# Initialize the assistant
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

# Helper function to capture print output
def capture_print_output(func, *args, **kwargs):
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        func(*args, **kwargs)
    return f.getvalue()

# Streamlit App Interface
st.title("CSV Analysis Assistant")

query = st.text_input("Ask a question about the CSV file:")

if st.button("Submit"):
    if query:
        response = capture_print_output(python_assistant.print_response, query, markdown=True)
        st.markdown(response)
    else:
        st.warning("Please enter a query.")
