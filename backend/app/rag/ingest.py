from pathlib import Path
import textwrap

import chromadb

from app.rag.embeddings import HashEmbeddingFunction


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
GUIDELINES_DIR = DATA_DIR / "medical_guidelines"
CHROMA_DIR = DATA_DIR / "chroma"
COLLECTION_NAME = "healio_medical_guidelines"


def ingest_guidelines(force: bool = False) -> int:
    GUIDELINES_DIR.mkdir(parents=True, exist_ok=True)
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=HashEmbeddingFunction(),
        metadata={"description": "Healio local medical reference snippets"},
    )

    if collection.count() and not force:
        return collection.count()

    if force and collection.count():
        client.delete_collection(COLLECTION_NAME)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=HashEmbeddingFunction(),
            metadata={"description": "Healio local medical reference snippets"},
        )

    documents = _load_documents()
    chunks = _chunk_documents(documents)

    if not chunks:
        return 0

    collection.add(
        ids=[f"guideline-{index}" for index, _ in enumerate(chunks)],
        documents=[chunk for chunk in chunks],
        metadatas=[{"source": "local_guideline_summary"} for _ in chunks],
    )
    return collection.count()


def _load_documents() -> list[str]:
    docs = []
    for path in sorted(GUIDELINES_DIR.glob("*.txt")):
        text = path.read_text(encoding="utf-8").strip()
        if text:
            docs.append(text)
    return docs


def _chunk_documents(documents: list[str], width: int = 900) -> list[str]:
    chunks: list[str] = []
    for document in documents:
        chunks.extend(chunk.strip() for chunk in textwrap.wrap(document, width=width) if chunk.strip())
    return chunks


if __name__ == "__main__":
    count = ingest_guidelines(force=True)
    print(f"Ingested {count} guideline chunks.")

