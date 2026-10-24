import json
import os
from pathlib import Path
from typing import List

import chromadb
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


class AnswerResponse(BaseModel):
    answer: str
    sources: List[str] = Field(default_factory=list)
    confidence: float = Field(
        ge=0.0,
        le=1.0
    )


# Required structured prompt.
# It is used by the optional real-LLM path.
PROMPT_TEMPLATE = """
ROLE:
You are Zepto's customer support policy assistant.

CONTEXT:
Answer only using the Zepto policy context supplied below.

TASK:
Answer the user's question accurately and concisely using the provided context.

FORMAT:
Return valid JSON with exactly these fields:
{
  "answer": "string",
  "sources": ["document_id"],
  "confidence": 0.0
}

LENGTH:
Keep the answer concise and directly answer the user's question.

NEGATIVE CONSTRAINT:
Do not answer using information that is not present in the provided context.
Do not invent or assume Zepto policies.

FEW-SHOT EXAMPLE:

User question:
"What is the standard delivery fee for an order below INR 149?"

Context:
"Standard delivery is free on orders over INR 149; orders below this threshold incur a flat INR 25 delivery fee."

Correct response:
{
  "answer": "Orders below INR 149 incur a flat INR 25 standard delivery fee.",
  "sources": ["doc_01"],
  "confidence": 1.0
}

USER QUESTION:
{query}

RETRIEVED CONTEXT:
{context}
"""


def is_mock_mode():
    return os.getenv(
        "MOCK_LLM",
        "1"
    ) != "0"


class Retriever:

    def __init__(self):
        self.model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DIR)
        )

        self.collection = (
            self.client.get_collection(
                COLLECTION_NAME
            )
        )

    def retrieve(self, query, top_k=3):

        query_embedding = (
            self.model.encode(
                [query],
                normalize_embeddings=True
            )[0]
            .tolist()
        )

        result = self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        documents = result["documents"][0]
        metadatas = result["metadatas"][0]
        distances = result["distances"][0]

        chunks = []

        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances
        ):
            chunks.append({
                "id": metadata["document_id"],
                "document": document,
                "distance": distance
            })

        return chunks


retriever = Retriever()


def mock_policy_answer(chunks):

    top_chunk = chunks[0]

    snippet = top_chunk["document"][:200]

    return AnswerResponse(
        answer=(
            "Based on the retrieved context: "
            + snippet
        ),
        sources=[
            chunk["id"]
            for chunk in chunks
        ],
        confidence=1.0
    )


def mock_general_answer():

    return AnswerResponse(
        answer=(
            "I can only answer questions "
            "about Zepto policies right now."
        ),
        sources=[],
        confidence=1.0
    )


def generate_real_llm_answer(
    query,
    chunks
):

    from groq import Groq

    client = Groq(
        api_key=os.getenv(
            "GROQ_API_KEY"
        )
    )

    context = "\n\n".join(
        [
            (
                f"[{chunk['id']}]\n"
                f"{chunk['document']}"
            )
            for chunk in chunks
        ]
    )

    prompt = PROMPT_TEMPLATE.format(
        query=query,
        context=context
    )

    last_error = None

    for attempt in range(3):

        try:

            corrective = ""

            if attempt > 0:
                corrective = """
Your previous response failed schema validation.
Return ONLY valid JSON containing:
answer, sources, confidence.
"""

            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "user",
                        "content":
                            prompt + corrective
                    }
                ],
                temperature=0
            )

            raw = (
                response
                .choices[0]
                .message
                .content
            )

            data = json.loads(raw)

            return AnswerResponse.model_validate(
                data
            )

        except Exception as exc:
            last_error = exc

    return AnswerResponse(
        answer=(
            "ERROR: Unable to produce a "
            "valid structured response."
        ),
        sources=[],
        confidence=0.0
    )