🤖 AI-Powered Insurance Policy Assistant: Know Your Health Policy (KYHP)
Team ASDF (Asuransi Salju Dingin Fokus) | Metrodata Electronics

💡 1. The Problem: A Costly Maze of Policy Confusion
The Pain Point: Hospital and healthcare administration is heavily burdened by manual insurance processes, creating significant friction, cost, and risk.

The Impact: This manual process directly leads to patient distress (surprise bills, delays) and massive financial inefficiency for providers.

🎯 2. The Solution: Instant Policy Answers with KYHP
Core Functionality: KYHP is a Retrieval-Augmented Generation (RAG) system built entirely on Snowflake that provides instant, specific, and referenced answers to complex health insurance policy questions.

Target Users: Hospital and clinic administrative staff (e.g., those handling Eligibility & Benefit Verification and Prior Authorization).

Key Value Proposition: Transforms multi-step, error-prone policy lookup processes into a simple, seconds-long conversational query.

----

📈 3. Expected Business Impact (The Metrics)
The KYHP solution is designed to tackle the $18.4 billion opportunity cost lost to manual transactions.

| Impact Area | Before KYHP (Manual) | After KYHP (Target) |
| :--- | :--- | :--- |
| **Operational Efficiency** | **E&BV** takes $\sim$**12 mins** / **PA** takes $\sim$**14 mins** per transaction. | Policy query time reduced to **seconds**. |
| **Financial Savings** | Cost of a manual medical transaction is $\sim$**USD 7.93** and rising. | **Significantly lower administrative costs** and fewer costly errors. |
| **Patient Care & CX** | High risk of **surprise bills** and frustrating **treatment delays**. | **Clear coverage transparency**, reduced administrative delays, and **better patient focus**. |

-----

⚙️ 4. Technology Stack & Architecture
KYHP is a Python RAG application fully hosted and executed within the Snowflake Data Cloud, leveraging its native AI/ML capabilities.

Frontend & Interface: Streamlit in Snowflake provides the custom, interactive web application, allowing users to select policies and customize their queries (e.g., tailoring responses to "covered/not covered").

AI/LLM Core: Snowflake Cortex Search Service manages the retrieval and vector embeddings. We utilize the Mistral-7b model for generation, selected for its low-cost performance and ability to establish a high-value prototype before scaling.

Data Ingestion & Processing:

Document AI: The solution uses SNOWFLAKE.CORTEX.PARSE_DOCUMENT to ingest policy files and extract raw text and layout from unstructured data (e.g., PDFs).

Chunking: The extracted text is then chunked and pre-processed using SNOWFLAKE.CORTEX.SPLIT_TEXT_MARKDOWN_HEADER before being indexed by the search service.

Backend Logic: Snowpark is utilized for orchestrating Python code, connecting the Streamlit UI to the search service and the LLM prompts.

------

🛠️ 5. Setup & Usage (Quick Start)
The application is deployed using the native Streamlit in Snowflake environment.

Data Ingestion: Policy documents are staged in Snowflake, and the ingestion/chunking process is triggered via custom SQL/Cortex functions (currently manual for initial setup).

Service Creation: The Cortex Search Service is initialized, pointing to the chunked policy data.

Application Launch: The Streamlit application file is run within Snowflake to launch the KYHP interface.

Usage: Users select a policy and ask a question. They may optionally upload a document to temporarily augment the context for a specific conversation.

------

🚀 6. Future Improvements (Next Development Angles)
The KYHP system is a high-impact prototype with significant expansion potential:

Improved Integration with Local Systems:

Develop a strong table of references for existing treatment options to provide next-step recommendations based on local facility and area data.

Expanding Functionality:

Implement an "Export Feature" allowing users to save responses into different administrative templates.

Create a "Policy Completeness" Algorithm to automatically scan policies for missing benefits, expiration dates, and other common critical elements.

Develop Dynamic Dropdowns and Lookup Tables for robust policy selection and metadata management.

