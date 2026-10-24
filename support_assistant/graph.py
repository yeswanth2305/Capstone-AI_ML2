import os
from typing import TypedDict

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from rag import (
    AnswerResponse,
    retriever,
    is_mock_mode,
    mock_policy_answer,
    mock_general_answer,
    generate_real_llm_answer
)


POLICY_KEYWORDS = [
    "delivery",
    "return",
    "refund",
    "membership",
    "tracking",
    "cancel",
    "gift card",
    "support hours"
]


class GraphState(TypedDict):

    query: str

    intent: str

    retrieved_chunks: list

    response: dict


def classify_intent(
    state: GraphState
):

    query = state["query"].lower()

    if is_mock_mode():

        intent = (
            "policy_question"
            if any(
                keyword in query
                for keyword in POLICY_KEYWORDS
            )
            else
            "general_question"
        )

    else:

        # Optional real-LLM extension.
        # Mock mode is the graded path.
        from groq import Groq

        client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )

        prompt = f"""
Classify this user query into exactly one
of these labels:

policy_question
general_question

Use policy_question if the query concerns
Zepto policies.

Query:
{state["query"]}

Return only the label.
"""

        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        raw = (
            result
            .choices[0]
            .message
            .content
            .strip()
        )

        intent = (
            "policy_question"
            if raw == "policy_question"
            else "general_question"
        )

    return {
        **state,
        "intent": intent
    }


def retrieve_and_answer(
    state: GraphState
):

    chunks = retriever.retrieve(
        state["query"],
        top_k=3
    )

    if is_mock_mode():

        response = mock_policy_answer(
            chunks
        )

    else:

        response = generate_real_llm_answer(
            state["query"],
            chunks
        )

    return {
        **state,
        "retrieved_chunks": chunks,
        "response": response.model_dump()
    }


def direct_answer(
    state: GraphState
):

    if is_mock_mode():

        response = mock_general_answer()

    else:

        # Optional real-LLM extension.
        from groq import Groq

        client = Groq(
            api_key=os.getenv(
                "GROQ_API_KEY"
            )
        )

        prompt = f"""
Answer this general question concisely:

{state["query"]}

Do not claim to have access to
Zepto policy information.
"""

        result = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0
        )

        response = AnswerResponse(
            answer=(
                result
                .choices[0]
                .message
                .content
            ),
            sources=[],
            confidence=0.8
        )

    return {
        **state,
        "retrieved_chunks": [],
        "response": response.model_dump()
    }


def route_intent(
    state: GraphState
):

    if state["intent"] == "policy_question":
        return "retrieve_and_answer"

    return "direct_answer"


def build_graph():

    graph = StateGraph(
        GraphState
    )

    graph.add_node(
        "classify_intent",
        classify_intent
    )

    graph.add_node(
        "retrieve_and_answer",
        retrieve_and_answer
    )

    graph.add_node(
        "direct_answer",
        direct_answer
    )

    graph.add_edge(
        START,
        "classify_intent"
    )

    graph.add_conditional_edges(
        "classify_intent",
        route_intent,
        {
            "retrieve_and_answer":
                "retrieve_and_answer",

            "direct_answer":
                "direct_answer"
        }
    )

    graph.add_edge(
        "retrieve_and_answer",
        END
    )

    graph.add_edge(
        "direct_answer",
        END
    )

    return graph.compile()


app_graph = build_graph()