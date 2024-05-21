from typing import List
import tempfile

import nest_asyncio
import streamlit as st
from phi.assistant import Assistant
from phi.document import Document
from phi.document.reader.pdf import PDFReader
from phi.document.reader.website import WebsiteReader
from phi.utils.log import logger

from assistant import get_sam_assisant  # type: ignore

nest_asyncio.apply()
st.set_page_config(
    page_title="SAM-AI",
    page_icon="📰",
)
st.title("Daily Newsletter Assistant 📰")
st.markdown("##### Created for internal use in Sucor Asset Management only")


def restart_assistant():
    logger.debug("---*--- Restarting Assistant ---*---")
    st.session_state["auto_rag_assistant"] = None
    st.session_state["auto_rag_assistant_run_id"] = None
    if "url_scrape_key" in st.session_state:
        st.session_state["url_scrape_key"] += 1
    if "file_uploader_key" in st.session_state:
        st.session_state["file_uploader_key"] += 1
    st.rerun()


def create_newsletter(messages) -> str:
    """Generate the newsletter content based on chat messages."""
    content = "## Sucor AM News Update\n\n"

    for message in messages:
        if message["role"] == "assistant":
            content += f"{message['content']}\n\n"
    
    return content

def main() -> None:
    # Get LLM model
    llm_model = st.sidebar.selectbox("Select LLM", options=["gpt-4o", "gpt-3.5-turbo"])
    # Set assistant_type in session state
    if "llm_model" not in st.session_state:
        st.session_state["llm_model"] = llm_model
    # Restart the assistant if assistant_type has changed
    elif st.session_state["llm_model"] != llm_model:
        st.session_state["llm_model"] = llm_model
        restart_assistant()

    # Get the assistant
    auto_rag_assistant: Assistant
    if "auto_rag_assistant" not in st.session_state or st.session_state["auto_rag_assistant"] is None:
        logger.info(f"---*--- Creating {llm_model} Assistant ---*---")
        auto_rag_assistant = get_sam_assisant(llm_model=llm_model)
        st.session_state["auto_rag_assistant"] = auto_rag_assistant
    else:
        auto_rag_assistant = st.session_state["auto_rag_assistant"]

    # Create assistant run (i.e. log to database) and save run_id in session state
    try:
        st.session_state["auto_rag_assistant_run_id"] = auto_rag_assistant.create_run()
    except Exception:
        st.warning("Could not create assistant, is the database running?")
        return

    # Load existing messages
    assistant_chat_history = auto_rag_assistant.memory.get_chat_history()
    if len(assistant_chat_history) > 0:
        logger.debug("Loading chat history")
        st.session_state["messages"] = assistant_chat_history
    else:
        logger.debug("No chat history found")
        st.session_state["messages"] = [{"role": "assistant", "content": "Input today's Benchmark Data and let me do the rest of the work."}]

    # Prompt for user input
    if prompt := st.chat_input():
        st.session_state["messages"].append({"role": "user", "content": prompt})

    # Display existing chat messages
    for message in st.session_state["messages"]:
        if message["role"] == "system":
            continue
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # If last message is from a user, generate a new response
    last_message = st.session_state["messages"][-1]
    if last_message.get("role") == "user":
        question = last_message["content"]
        with st.chat_message("assistant"):
            resp_container = st.empty()
            response = ""
            for delta in auto_rag_assistant.run(question):
                response += delta  # type: ignore
                resp_container.markdown(response)
            st.session_state["messages"].append({"role": "assistant", "content": response})

    # # Load knowledge base
    # if auto_rag_assistant.knowledge_base:
    #     # -*- Add websites to knowledge base
    #     if "url_scrape_key" not in st.session_state:
    #         st.session_state["url_scrape_key"] = 0

    #     input_url = st.sidebar.text_input(
    #         "Add URL to Knowledge Base", type="default", key=st.session_state["url_scrape_key"]
    #     )
    #     add_url_button = st.sidebar.button("Add URL")
    #     if add_url_button:
    #         if input_url is not None:
    #             alert = st.sidebar.info("Processing URLs...", icon="ℹ️")
    #             if f"{input_url}_scraped" not in st.session_state:
    #                 scraper = WebsiteReader(max_links=2, max_depth=1)
    #                 web_documents: List[Document] = scraper.read(input_url)
    #                 if web_documents:
    #                     auto_rag_assistant.knowledge_base.load_documents(web_documents, upsert=True)
    #                 else:
    #                     st.sidebar.error("Could not read website")
    #                 st.session_state[f"{input_url}_uploaded"] = True
    #             alert.empty()

    #     # Add PDFs to knowledge base
    #     if "file_uploader_key" not in st.session_state:
    #         st.session_state["file_uploader_key"] = 100

    #     uploaded_file = st.sidebar.file_uploader(
    #         "Add a PDF :page_facing_up:", type="pdf", key=st.session_state["file_uploader_key"]
    #     )
    #     if uploaded_file is not None:
    #         alert = st.sidebar.info("Processing PDF...", icon="🧠")
    #         auto_rag_name = uploaded_file.name.split(".")[0]
    #         if f"{auto_rag_name}_uploaded" not in st.session_state:
    #             reader = PDFReader()
    #             auto_rag_documents: List[Document] = reader.read(uploaded_file)
    #             if auto_rag_documents:
    #                 auto_rag_assistant.knowledge_base.load_documents(auto_rag_documents, upsert=True)
    #             else:
    #                 st.sidebar.error("Could not read PDF")
    #             st.session_state[f"{auto_rag_name}_uploaded"] = True
    #         alert.empty()

    # if auto_rag_assistant.knowledge_base and auto_rag_assistant.knowledge_base.vector_db:
    #     if st.sidebar.button("Clear Knowledge Base"):
    #         auto_rag_assistant.knowledge_base.vector_db.clear()
    #         st.sidebar.success("Knowledge base cleared")

    # if auto_rag_assistant.storage:
    #     auto_rag_assistant_run_ids: List[str] = auto_rag_assistant.storage.get_all_run_ids()
    #     new_auto_rag_assistant_run_id = st.sidebar.selectbox("Run ID", options=auto_rag_assistant_run_ids)
    #     if st.session_state["auto_rag_assistant_run_id"] != new_auto_rag_assistant_run_id:
    #         logger.info(f"---*--- Loading {llm_model} run: {new_auto_rag_assistant_run_id} ---*---")
    #         st.session_state["auto_rag_assistant"] = get_sam_assisant(
    #             llm_model=llm_model, run_id=new_auto_rag_assistant_run_id
    #         )
    #         st.rerun()

    if st.sidebar.button("New Run"):
        restart_assistant()

    # if "embeddings_model_updated" in st.session_state:
    #     st.sidebar.info("Please add documents again as the embeddings model has changed.")
    #     st.session_state["embeddings_model_updated"] = False
    
    # Generate newsletter content from chat history
    newsletter_content = create_newsletter(st.session_state["messages"])

    # Save the content to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
        tmp_file.write(newsletter_content.encode("utf-8"))
        tmp_file_path = tmp_file.name

    # Provide a download button in the sidebar
    with st.sidebar:
        with open(tmp_file_path, "rb") as file:
            st.download_button(
                label="Download Newsletter",
                data=file,
                file_name="newsletter.txt",
                mime="text/plain"
            )

main()
