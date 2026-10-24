from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "zepto_policies"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def load_documents():
    documents = []
    ids = []
    metadatas = []

    for path in sorted(DOCS_DIR.glob("doc_*.txt")):
        text = path.read_text(encoding="utf-8").strip()

        documents.append(text)
        ids.append(path.stem)
        metadatas.append({
            "document_id": path.stem
        })

    return ids, documents, metadatas


def build_index():
    ids, documents, metadatas = load_documents()

    print(f"Loaded documents: {len(documents)}")

    model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    embeddings = model.encode(
        documents,
        normalize_embeddings=True
    ).tolist()

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # Recreate collection for deterministic runs.
    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "hnsw:space": "cosine"
        }
    )

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Indexed {collection.count()} documents."
    )

    return collection


if __name__ == "__main__":
    build_index()