from graph import app_graph


def run_test(query):

    result = app_graph.invoke({
        "query": query,
        "intent": "",
        "retrieved_chunks": [],
        "response": {}
    })

    print("=" * 70)
    print("QUERY:")
    print(query)

    print("\nINTENT:")
    print(result["intent"])

    print("\nRETRIEVED SOURCES:")
    print(
        [
            chunk["id"]
            for chunk in result[
                "retrieved_chunks"
            ]
        ]
    )

    print("\nRESPONSE:")
    print(result["response"])


if __name__ == "__main__":

    run_test(
        "What is the delivery fee below INR 149?"
    )

    run_test(
        "What is the capital of India?"
    )

    run_test(
        "How long can I return a damaged grocery item?"
    )

    run_test(
        "Tell me a joke."
    )