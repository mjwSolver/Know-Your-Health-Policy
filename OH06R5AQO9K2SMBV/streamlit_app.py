import streamlit as st
import pandas as pd
import json

# Required for providing date time warning
from datetime import datetime
import io
from PyPDF2 import PdfReader

# Required for Snowpark session, Cortex search, and LLM completion
try:
    from snowflake.core import Root
    from snowflake.cortex import Complete
    from snowflake.snowpark.context import get_active_session
except ImportError:
    st.error("Missing required Snowpark/Cortex libraries. Please ensure your environment has 'snowflake-snowpark-python' and 'snowflake-core' installed.")
    st.stop()

# --- CONFIGURATION (Match your Snowflake setup) ---
DB_NAME = "INSURANCE_HACKATHON_DB"
SCHEMA_NAME = "PROOF_OF_CONCEPT_SCHEMA"
RAG_SERVICE_NAME = "INSURANCE_RAG_SERVICE_2"

# Available Cortex LLMs for the Complete function
# Note: Llama 3 models offer excellent instruction following
MODELS = [
    "llama3-70b-8192", # Excellent choice for RAG and instruction following
    "mixtral-8x7b",
    "llama2-70b-chat",
    "mistral-7b"
]

# --- SESSION & INITIALIZATION ---

# Get active session (required for Snowpark and Core)
try:
    session = get_active_session()
except Exception as e:
    st.error("Could not get active Snowpark session. This app must be run within a Snowflake Streamlit environment.")
    st.stop()
    
# Initialize Root for accessing services
root = Root(session)

# Set model name default
if "model_name" not in st.session_state:
    st.session_state.model_name = MODELS[3]
if "num_retrieved_chunks" not in st.session_state:
    st.session_state.num_retrieved_chunks = 1

st.set_page_config(
    page_title="Indonesian Insurance RAG Chatbot",
    layout="wide",
)

st.title("📄🧑‍⚕️ AI-Powered Health Insurance Policy Analyst (RAG)")
st.caption("Grounded responses from the Industrial All Risks PDF using Snowflake Cortex Search and LLMs.")
st.caption("An Asuransi Salju Dingin Fokus (ASDF) product for the purposes of the Snowflake Partner Hackathon 2025")


def init_messages():
    """Initialize the session state for chat messages."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # If the service metadata isn't ready, don't allow clearing the conversation
    if "clear_conversation" in st.session_state and st.session_state.clear_conversation:
        st.session_state.messages = []


def init_config_options():
    """
    Initialize and display the configuration options in the Streamlit sidebar.
    """
    st.sidebar.header("Configuration")
    
    # Static display of the selected service
    st.sidebar.markdown(f"**Cortex Search Service:** `{RAG_SERVICE_NAME}`")
    st.sidebar.markdown(f"**Context Language Filter:** `Indonesian`")

    st.sidebar.toggle("Clear conversation", key="clear_conversation")
    st.sidebar.toggle("Debug (Show Prompt/Context)", key="debug", value=False)
    # Disabled chat history as this is primarily a document QA app
    # st.sidebar.toggle("Use chat history", key="use_chat_history", value=False) 

    # New UI for selecting the policy BEFORE asking a question
    st.sidebar.header("Policy Selection (Hospital Use)")

    # For now, we hardcode the ones you uploaded
    insurers_list = ["Mandiri", "BCA", "PLN", "Flakeseed", ""] 
    st.selectbox(
        "1. Select Insurer", 
        insurers_list, 
        key="selected_insurer",
        index=len(insurers_list)-1, # Default to blank
        placeholder="Select insurer..."
    )

    st.sidebar.text_input(
        "2. Enter Policy Plan Name (or leave blank for all)",
        key="selected_plan",
        placeholder="e.g., Policy_XYZ.pdf"
    )

    st.sidebar.header("Patient Context (Optional)")
    st.file_uploader(
        "Upload Patient Medical Report (PDF)",
        type="pdf",
        key="patient_file_uploader"
    )
    
    with st.sidebar.expander("Model & Chunk Options"):
        st.selectbox("Select Model:", MODELS, key="model_name")
        st.number_input(
            "Number of context chunks to retrieve (Top K)",
            value=1,
            key="num_retrieved_chunks",
            min_value=1,
            max_value=10,
        )


def query_cortex_search_service(query, columns=["chunk", "file_url", "relative_path", "INSURER", "POLICY_PLAN", "UPLOAD_DATE", "POLICY_START_DATE"]):
    """
    Query the selected cortex search service using the Python API.
    
    *** THIS FUNCTION IS NOW MODIFIED ***
    It dynamically builds a filter based on the Streamlit session state.

    Args:
        query (str): The query to search the cortex search service with.
        columns (list): The metadata columns to retrieve.

    Returns:
        tuple: The concatenated string of context documents and the list of raw results.
    """
    
    # 1. Access the Cortex Search Service (same as before)
    try:
        cortex_search_service = (
            root.databases[DB_NAME]
            .schemas[SCHEMA_NAME]
            .cortex_search_services[RAG_SERVICE_NAME]
        )
    except Exception as e:
        st.error(f"Could not find Cortex Search Service '{RAG_SERVICE_NAME}'. Please ensure it exists in your schema.")
        st.stop()
        
    # --- 2. NEW: Build the dynamic filter ---
    # Start with our mandatory language filter
    search_filters = [
        {"@eq": {"language": "Indonesian"}}
    ]
    
    # Get insurer and plan from the session state
    insurer = st.session_state.get("selected_insurer", "")
    plan = st.session_state.get("selected_plan", "")
    
    # Add filters ONLY if they have been selected
    if insurer:
        search_filters.append({"@eq": {"INSURER": insurer}})
    
    if plan:
        # Use '@ilike' for flexible matching (e.g., "Policy_XYZ" matches "Policy_XYZ.pdf")
        search_filters.append({"@ilike": {"POLICY_PLAN": f"%{plan}%"}})

    # Combine all filters using "@and"
    search_filter = {"@and": search_filters}
    
    # 3. Execute the search (with the new filter)
    try:
        context_documents = cortex_search_service.search(
            query, 
            columns=columns, 
            filter=search_filter,  # <--- Pass the new dynamic filter
            limit=st.session_state.num_retrieved_chunks
        )
        results = context_documents.results
    except Exception as e:
        # Catch errors if the filter is bad or a column is missing
        st.error(f"Error during search: {e}")
        st.error(f"Attempted search filter: {json.dumps(search_filter, indent=2)}")
        st.stop()
        
    # 4. Format the context for the LLM prompt (same as before)
    context_str = ""
    search_col = "chunk" # The column containing the text
    
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r[search_col]} \n" + "\n"

    # 5. Optional: Display context and filter in debug mode
    if st.session_state.debug:
        st.sidebar.subheader("Debug Info (Search)")
        st.sidebar.text_area("Context documents", context_str, height=200)
        st.sidebar.caption("Dynamic Search Filter JSON:")
        st.sidebar.json(search_filter)

    return context_str, results


def complete(model, prompt):
    """
    Generate a completion for the given prompt using the specified model via the Cortex API.
    """
    # Use the snowflake.cortex.Complete class wrapper
    return Complete(model, prompt)


# In your Streamlit Python file (app.py)
#
# Replace your OLD create_prompt function
# with this NEW one.


    

def format_date_warning(policy_start_date, upload_date):
    """Generates a markdown string for the policy date warning."""
    
    warning_header = "###### Informasi Polis (Policy Info)\n"
    
    try:
        if policy_start_date:
            # TODO: We haven't implemented AI extraction yet,
            # so this will be NULL for now.
            return f"{warning_header}- Status: **Aktif**\n- Tanggal Berlaku: **{policy_start_date}**\n"
        
        elif upload_date:
            # This is your fallback logic
            today = datetime.now().date()
            
            # Convert timestamp string from Snowflake (if needed)
            if isinstance(upload_date, str):
                upload_date = datetime.fromisoformat(upload_date)

            upload_date_only = upload_date.date()
            days_ago = (today - upload_date_only).days
            
            upload_str = upload_date_only.strftime('%Y-%m-%d')
            
            if days_ago == 0:
                days_str = "(hari ini)"
            elif days_ago == 1:
                days_str = "(1 hari yang lalu)"
            else:
                days_str = f"({days_ago} hari yang lalu)"
            
            return (
                f"{warning_header}"
                f"- **PERINGATAN**: Tanggal efektif polis tidak ditemukan.\n"
                f"- Dokumen diunggah: **{upload_str} {days_str}**\n"
            )
            
    except Exception as e:
        # Catch any date formatting errors
        return f"{warning_header}- Gagal memuat metadata tanggal: {e}\n"
        
    return "" # Default empty string

def get_text_from_uploaded_pdf(uploaded_file):
    """
    Reads an in-memory PDF file and returns its text content.
    """
    if uploaded_file is None:
        return ""
        
    try:
        # Read the file-like object
        pdf_content = io.BytesIO(uploaded_file.getvalue())
        
        # Use PdfReader to parse the text
        pdf_reader = PdfReader(pdf_content)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text
    except Exception as e:
        st.error(f"Error reading uploaded PDF: {e}")
        return ""

def main():
    init_config_options()
    init_messages()

    icons = {"assistant": "❄️", "user": "👤"}

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar=icons[message["role"]]):
            st.markdown(message["content"])

    # Old KYHP
    # Initialize the task state
    # if "current_task" not in st.session_state:
    #     st.session_state.current_task = "general" # Default to general questions

    if "current_agent_name" not in st.session_state:
        # NOTE: Update "GENERAL_AGENT" if you named yours differently
        st.session_state.current_agent_name = "GENERAL_AGENT"

    # Task selection buttons, replaced to adjust for Snowflake Agents
    st.write("Pilih jenis pertanyaan (Select question type):")
    cols = st.columns(3)
    with cols[0]:
        if st.button("Pertanyaan Umum (General)", use_container_width=True):
            st.session_state.current_agent_name = "GENERAL_AGENT"
    with cols[1]:
        if st.button("Cek Perlindungan (Check Coverage)", use_container_width=True):
            st.session_state.current_agent_name = "COVERAGE_AGENT"
    with cols[2]:
        if st.button("Cari Co-Pay/Biaya (Find Co-Pay)", use_container_width=True):
            st.session_state.current_agent_name = "COPAY_AGENT"

    # Dynamic chat input placeholder
    # task_placeholders = {
    #     "general": "Tanyakan sesuatu tentang polis asuransi...",
    #     "coverage": "Masukkan nama prosedur atau perawatan (e.g., 'operasi usus buntu')...",
    #     "copay": "Masukkan nama prosedur untuk cek biaya (e.g., 'kamar rawat inap')..."
    # }
    # placeholder_text = task_placeholders.get(
    #     st.session_state.current_task, 
    #     task_placeholders["general"]
    # )

    # This is new for the Snowflake Agent
    task_placeholders = {
        "GENERAL_AGENT": "Tanyakan sesuatu tentang polis asuransi...",
        "COVERAGE_AGENT": "Masukkan nama prosedur atau perawatan (e.g., 'operasi usus buntu')...",
        "COPAY_AGENT": "Masukkan nama prosedur untuk cek biaya (e.g., 'kamar rawat inap')..."
    }
    placeholder_text = task_placeholders.get(
        st.session_state.current_agent_name, 
        task_placeholders["GENERAL_AGENT"]
    )

    # Input for new question
    if question := st.chat_input(placeholder_text, key="chat_input_box"):
        
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": question})
        
        # Display user message
        with st.chat_message("user", avatar=icons["user"]):
            st.markdown(question)

        # Display assistant response
        with st.chat_message("assistant", avatar=icons["assistant"]):
            message_placeholder = st.empty()
            
            with st.spinner(f"Retrieving context and generating response using {st.session_state.model_name}..."):
                
                # 1. Create the RAG prompt and retrieve the context results
                prompt, results = create_prompt(question)
                
                # Optional: Display full prompt in debug mode
                if st.session_state.debug:
                    st.sidebar.subheader("Full LLM Prompt (Debug)")
                    st.sidebar.text_area("LLM Prompt", prompt, height=400)

                # 2. Call the LLM API
                try:
                    generated_response = complete(st.session_state.model_name, prompt)
                except Exception as e:
                    generated_response = f"Error during LLM completion: {e}"

                # 3. Building Date Warning String
                date_warning_str = ""
                if results:
                    # Get metadata from the first retrieved chunk
                    # All chunks from the same doc will have the same dates
                    first_result = results[0]
                    policy_start = first_result.get('POLICY_START_DATE')
                    upload_date = first_result.get('UPLOAD_DATE')
                    
                    # Generate the warning string using our new function
                    date_warning_str = format_date_warning(policy_start, upload_date)

                
                # 4. Build references table for citation
                markdown_table = "###### Sumber Referensi (References) \n\n| Dokumen | Link | Similarity |\n|-------|-----|------------|\n"
                
                if results:
                    for ref in results:
                        # Extract the required fields from the search result object
                        title = ref.get('relative_path', 'N/A')
                        url = ref.get('file_url', '#')
                        # Note: @scores is an object, we need to access its sub-key
                        similarity = ref.get('@scores', {}).get('cosine_similarity', 0.0)
                        
                        markdown_table += f"| {title} | [Lihat Dokumen]({url}) | {similarity:.4f} |\n"
                
                # 5. Final output
                final_output = (
                    f"{generated_response}\n\n"
                    f"---\n" # Add a horizontal line to break the contents up
                    f"{date_warning_str}\n"
                    f"{markdown_table}"
                )
                message_placeholder.markdown(final_output)
        
        # 6. Add assistant response to history
        st.session_state.messages.append(
            {"role": "assistant", "content": final_output}
        )


if __name__ == "__main__":
    main()
