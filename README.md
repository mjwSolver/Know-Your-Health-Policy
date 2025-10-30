# 🤖 AI-Powered Insurance Policy Assistant: Know Your Health Policy (KYHP)

**Team ASDF (Asuransi Salju Dingin Fokus) | Metrodata Electronics**

---

## 💡 1. The Problem: A Costly Maze of Policy Confusion

Hospital and healthcare providers face significant administrative burdens in handling complex, unstructured insurance policy documents. This friction generates massive inefficiency, drives up operational costs, and degrades the patient experience.

* **Operational Bottlenecks:** Manual Eligibility & Benefit Verification (E&BV) and Prior Authorization (PA) processes require high-cost administrative staff and time.
* **Patient Risk:** The lack of clarity and speed increases the likelihood of "surprise bills" and creates frustrating, costly delays in accessing needed treatment.
* **Lost Savings:** The persistence of complex manual tasks prevents hospitals from capturing billions in potential administrative cost savings.

---

## 🎯 2. The Solution: Instant Policy Answers with KYHP

KYHP is a **Retrieval-Augmented Generation (RAG)** system built to instantly, accurately, and traceably answer complex health insurance policy questions. By transforming unstructured PDF policies into actionable knowledge, KYHP acts as a digital policy expert for administrative staff.

* **Core Functionality:** Users can select a policy and query the system using natural language, or provide a document to temporarily augment the conversation context.
* **Tailored Responses:** Individual query buttons allow users to customize the LLM's output format, such as:
    * General Summary
    * "Covered, Not Covered, or Not Mentioned" status
    * Extraction of specific hard numbers (e.g., deductible amounts).

---

## 📈 3. Expected Business Impact (The Metrics)

The KYHP solution is designed to tackle the **$18.4 billion** opportunity cost currently lost to inefficient manual transactions (2023 figures).

| Impact Area | Before KYHP (Manual) | After KYHP (Target) |
| :--- | :--- | :--- |
| **Operational Efficiency** | **E&BV** takes $\sim$12 mins / **PA** takes $\sim$14 mins per transaction. | Policy query time reduced to **seconds**, freeing up up staff time. |
| **Financial Savings** | Cost of a manual medical transaction is $\sim$USD 7.93 and rising. | Significant reduction in administrative labor costs and minimization of billing errors. |
| **Patient Care & CX** | High risk of **surprise bills** and frustrating treatment **delays**. | Clear coverage transparency, reduced administrative delays, and improved quality of human interaction. |

---

## ⚙️ 4. Technology Stack & Architecture

KYHP is a serverless, end-to-end Python RAG application running entirely within the **Snowflake Data Cloud**, maximizing security, governance, and computational efficiency.

### Snowflake Features Utilized

| Feature | Purpose | Key Usage |
| :--- | :--- | :--- |
| **Snowflake Cortex Search** | Vector Indexing and Retrieval | Provides instant, high-relevance context retrieval to ground the LLM's answers. |
| **Document AI (`PARSE_DOCUMENT`)** | Unstructured Data Extraction | Used to accurately ingest policies by extracting raw text and layout information from PDFs. |
| **`SPLIT_TEXT_MARKDOWN_HEADER`** | Smart Text Chunking | Optimizes context by intelligently splitting policy documents into relevant chunks for the search index. |
| **Streamlit in Snowflake** | User Interface & Hosting | Provides a custom, interactive, and natively hosted application interface directly in the platform. |
| **Snowpark & Python** | Orchestration & Logic | Connects the UI to the Cortex services and manages the data flow and query processing. |
| **Mistral-7b** | Generative LLM | Selected to build a **low-cost, high-performance prototype** to assess the minimal LLM requirements before scaling to larger models. |

---

## 🛠️ 5. Setup & Usage (Current State)

The application is deployed using the native **Streamlit in Snowflake** environment.

1.  **Ingestion:** Policies are manually ingested into a staged environment. The `PARSE_DOCUMENT` and chunking functions are executed via SQL to extract and prepare the text for indexing.
2.  **Cortex Service:** The `INSURANCE_RAG_SERVICE` is created and pointed at the chunked data table.
3.  **Application Launch:** The Streamlit application is run within Snowflake.
4.  **Interaction:** Users interact via the conversational interface, selecting a policy via a dropdown or uploading context, and using the prompt-tailoring buttons to ask questions.

---

## 🚀 6. Future Improvements (Next Development Angles)

The current system is a robust prototype, but future development will focus on integrating deeper workflow automation and data validation.

1.  **Improved Integration with Local Systems:**
    * Develop a strong table of references for existing treatment options to provide a basis for recommended next steps based on local facility and area data.
2.  **Expanding Functionality:**
    * Implement an **Export Feature** allowing users to save responses into different administrative templates (e.g., insurer-specific forms).
    * Create a **"Policy Completeness" Algorithm** to automatically scan policies for missing benefits, expiration dates, and other common critical elements required by regulatory bodies.
    * Develop **Dynamic Dropdowns and Lookup Tables** for proper policy selection and metadata management.

---
