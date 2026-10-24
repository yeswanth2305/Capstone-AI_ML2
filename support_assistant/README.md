# Module 3 — Support Assistant

## Overview

This module implements a retrieval-augmented customer support assistant for Zepto policy questions.

The system follows:

```text
Policy Documents
      ↓
Document Ingestion
      ↓
SentenceTransformer Embeddings
      ↓
ChromaDB Vector Store
      ↓
User Query
      ↓
LangGraph Intent Classification
      ↓
 ┌──────────────────────┐
 │                      │
policy_question   general_question
 │                      │
 ↓                      ↓
Retrieve Context    Direct Answer
 │                      │
 └──────────┬───────────┘
            ↓
      Pydantic Response
            ↓
        FastAPI /ask
```

The required graded execution path uses `MOCK_LLM=1`, which provides deterministic responses without requiring an API key.

---

## Project Structure

```text
support_assistant/
│
├── docs/
│   ├── doc_01.txt
│   ├── doc_02.txt
│   ├── doc_03.txt
│   ├── doc_04.txt
│   ├── doc_05.txt
│   ├── doc_06.txt
│   ├── doc_07.txt
│   └── doc_08.txt
│
├── chroma_db/
├── ingest.py
├── rag.py
├── graph.py
├── main.py
├── test_app.py
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 1. Policy Corpus

The knowledge base contains eight Zepto policy documents:

| Document     | Topic                              |
| ------------ | ---------------------------------- |
| `doc_01.txt` | Delivery                           |
| `doc_02.txt` | Returns and refunds                |
| `doc_03.txt` | Membership tiers                   |
| `doc_04.txt` | Rider tracking                     |
| `doc_05.txt` | Order cancellation                 |
| `doc_06.txt` | Damaged, spoiled, or missing items |
| `doc_07.txt` | Gift cards                         |
| `doc_08.txt` | Customer support                   |

The documents are stored as plain-text files in `docs/`.

---

## 2. Document Ingestion

`ingest.py` loads the eight policy documents and creates embeddings using:

```text
all-MiniLM-L6-v2
```

The resulting embeddings are stored in a persistent ChromaDB collection:

```text
zepto_policies
```

The ChromaDB collection uses cosine similarity for vector retrieval.

Each policy document is stored with its document identifier as metadata, allowing retrieved sources to be returned with the final answer.

Run ingestion with:

```bash
python ingest.py
```

Expected result:

```text
Loaded documents: 8
Indexed 8 documents.
```

---

## 3. Retrieval

`rag.py` embeds an incoming query using the same:

```text
all-MiniLM-L6-v2
```

embedding model.

The query is searched against the ChromaDB collection using cosine similarity.

The top three relevant documents are retrieved.

Each retrieved result contains:

```text
document_id
document text
similarity distance
```

The retrieved document IDs are returned as the `sources` field of the final response.

---

## 4. LangGraph Architecture

The workflow is implemented using LangGraph and contains three required nodes:

```text
classify_intent
retrieve_and_answer
direct_answer
```

### `classify_intent`

Determines whether the query is:

```text
policy_question
```

or:

```text
general_question
```

### `retrieve_and_answer`

Used for policy questions.

It:

1. Embeds the query.
2. Retrieves the most relevant policy documents from ChromaDB.
3. Generates the structured response.
4. Returns the retrieved document IDs as sources.

### `direct_answer`

Used for general questions.

In mock mode it returns a deterministic response explaining that the assistant currently answers Zepto policy questions.

### Conditional routing

The graph follows:

```text
START
  ↓
classify_intent
  ↓
 ┌──────────────────────┐
 │                      │
policy_question   general_question
 │                      │
 ↓                      ↓
retrieve_and_answer   direct_answer
 │                      │
 └──────────┬───────────┘
            ↓
           END
```

---

## 5. Structured Response

The API response is validated using Pydantic.

The response schema is:

```json
{
  "answer": "string",
  "sources": ["document_id"],
  "confidence": 0.0
}
```

`confidence` is constrained to the range:

```text
0.0 <= confidence <= 1.0
```

---

## 6. Prompt Template

The real-LLM path contains a structured prompt with the following components:

* Role
* Context
* Task
* Format
* Length constraint
* Negative constraint
* Few-shot example
* User question
* Retrieved context

The negative constraint instructs the model not to invent Zepto policies and to answer only from retrieved policy context.

The real LLM path is optional. The required deterministic graded path uses `MOCK_LLM=1`.

---

## 7. MOCK_LLM Mode

The application supports:

```text
MOCK_LLM=1
```

This is the deterministic baseline used for grading.

Set it in PowerShell:

```powershell
$env:MOCK_LLM="1"
```

The mock mode:

* Does not require an API key.
* Uses the same embedding and ChromaDB retrieval pipeline.
* Returns deterministic structured responses.
* Allows reproducible testing.

---

## 8. Running the Application

Install dependencies:

```bash
pip install -r requirements.txt
```

Build the vector index:

```bash
python ingest.py
```

Set mock mode:

```powershell
$env:MOCK_LLM="1"
```

Start FastAPI:

```bash
python -m uvicorn main:app --reload
```

The API is available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 9. API Endpoint

### POST `/ask`

Request:

```json
{
  "query": "What is the delivery fee below INR 149?"
}
```

Response:

```json
{
  "answer": "...",
  "sources": ["doc_01"],
  "confidence": 1.0
}
```

---

## 10. Example Policy Query

Query:

```text
What is the delivery fee below INR 149?
```

Actual application output:

```json
Based on the retrieved context: Zepto delivers grocery and household essentials to serviceable pin codes within 10...
```

This query demonstrates the policy-question branch and ChromaDB retrieval.

---

## 11. Example General Query

Query:

```text
What is the capital of India?
```

Actual application output:

```json
answer                                                      sources confidence
------                                                      ------- ----------
I can only answer questions about Zepto policies right now. {}             1.0
```

This query demonstrates the general-question branch and does not perform policy retrieval.

---

## 12. Docker

A Dockerfile is provided for local container execution.

Build:

```bash
docker build -t zepto-support .
```

Run:

```bash
docker run --rm -p 7860:7860 zepto-support
```

The container defaults to:

```text
MOCK_LLM=1
```

so the required baseline does not require an external API key.

The Docker image exposes port:

```text
7860
```

The container can then be queried using:

```text
POST http://localhost:7860/ask
```

---

## 13. Testing

The basic LangGraph workflow can be tested with:

```bash
python test_app.py
```

The test script exercises both:

```text
policy_question
general_question
```

and prints the detected intent, retrieved sources, and structured response.

---

## 14. Reproducibility

The required workflow is deterministic through `MOCK_LLM=1`.

No paid API or API key is required for the graded baseline.

The complete flow is:

```text
8 Policy Documents
        ↓
SentenceTransformer
        ↓
ChromaDB
        ↓
User Query
        ↓
LangGraph
        ↓
Intent Classification
        ↓
Retrieval or Direct Answer
        ↓
Pydantic Validation
        ↓
FastAPI JSON Response
```
