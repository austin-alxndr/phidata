import json
from typing import Optional
import tempfile
import streamlit as st

from assistants import (
    SearchTerms,
    search_term_generator,
    exa_search_assistant,
    research_editor,
)  # type: ignore

st.set_page_config(
    page_title="Research Assistant",
    page_icon="📰",
)
st.title("AI Research Assistant 📰")
st.markdown("##### For internal use in [Sucor Sekuritas](https://sucorsekuritas.com) only")

def create_report(topic: str, search_terms: SearchTerms, exa_content: Optional[str] = None) -> str:
    """Generate the report content based on the topic and search results."""
    content = f"# Topic: {topic}\n\n"
    content += "## Search Terms\n\n"
    content += f"{search_terms}\n\n"
    
    if exa_content:
        content += "## Web Search Content from Exa\n\n"
        content += f"{exa_content}\n\n"
    
    return content

def main() -> None:
    # Get topic for report
    input_topic = st.sidebar.text_input(
        ":female-scientist: Enter a topic",
        value="",
    )
    # Button to generate report
    generate_report = st.sidebar.button("Generate Report")
    if generate_report:
        st.session_state["topic"] = input_topic
        st.session_state["report_generated"] = False

    # Checkboxes for search
    st.sidebar.markdown("## Assistants")
    search_exa = st.sidebar.checkbox("Exa Search", value=True)
    num_search_terms = st.sidebar.number_input(
        "Number of Search Terms", value=1, min_value=1, max_value=3, help="This will increase latency."
    )

    if "topic" in st.session_state and generate_report:
        report_topic = st.session_state["topic"]

        search_terms: Optional[SearchTerms] = None
        with st.status("Generating Search Terms", expanded=True) as status:
            with st.container():
                search_terms_container = st.empty()
                search_generator_input = {"topic": report_topic, "num_terms": num_search_terms}
                search_terms = search_term_generator.run(json.dumps(search_generator_input))
                if search_terms:
                    search_terms_container.json(search_terms.model_dump())
            status.update(label="Search Terms Generated", state="complete", expanded=False)

        if not search_terms:
            st.write("Sorry, report generation failed. Please try again.")
            return

        exa_content: Optional[str] = None
        if search_exa:
            with st.status("Searching Exa", expanded=True) as status:
                with st.container():
                    exa_container = st.empty()
                    exa_search_results = exa_search_assistant.run(search_terms.model_dump_json(indent=4))
                    if exa_search_results and len(exa_search_results.results) > 0:
                        exa_content = exa_search_results.model_dump_json(indent=4)
                        exa_container.json(exa_search_results.results)
                status.update(label="Exa Search Complete", state="complete", expanded=False)

        report_content = create_report(report_topic, search_terms, exa_content)

        with st.spinner("Generating Report"):
            final_report = ""
            final_report_container = st.empty()
            for delta in research_editor.run(report_content):
                final_report += delta  # type: ignore
                final_report_container.markdown(final_report)
            
            # Save final report to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as tmp_file:
                tmp_file.write(final_report)
                st.session_state['final_report_path'] = tmp_file.name
                st.session_state['report_generated'] = True

    # Always render the download button
    with st.sidebar:
        st.markdown("## Download Newsletter")
        if st.session_state.get('report_generated', False):
            with open(st.session_state['final_report_path'], "rb") as file:
                st.download_button(
                    label="Download Newsletter",
                    data=file,
                    file_name="newsletter.txt",
                    mime="text/plain"
                )
        else:
            st.markdown("Generate a report to enable download")

    st.sidebar.markdown("---")
    if st.sidebar.button("Restart"):
        st.session_state.clear()
        st.rerun()

main()
