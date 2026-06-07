import chromadb

from app.rag.embeddings import HashEmbeddingFunction
from app.rag.ingest import CHROMA_DIR, COLLECTION_NAME, ingest_guidelines


def retrieve_context(query: str, limit: int = 3) -> str:
    ingest_guidelines()
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=HashEmbeddingFunction(),
    )

    if collection.count() == 0:
        return ""

    results = collection.query(query_texts=[query], n_results=min(limit, collection.count()))
    documents = results.get("documents", [[]])[0]
    return "\n\n".join(documents)

