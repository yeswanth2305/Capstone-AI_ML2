from fastapi import FastAPI
from pydantic import BaseModel, Field

from graph import app_graph
from rag import AnswerResponse


app = FastAPI(
    title="Zepto Support Assistant",
    version="1.0.0"
)


class AskRequest(BaseModel):

    query: str = Field(
        min_length=1
    )


@app.get("/")
def root():

    return {
        "service": "Zepto Support Assistant",
        "endpoint": "POST /ask"
    }


@app.post(
    "/ask",
    response_model=AnswerResponse
)
def ask(
    request: AskRequest
):

    result = app_graph.invoke({
        "query": request.query,
        "intent": "",
        "retrieved_chunks": [],
        "response": {}
    })

    return AnswerResponse.model_validate(
        result["response"]
    )