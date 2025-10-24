# app/core/vector_client.py - Implements a basic Chroma client for local embeddings.

import chromadb
from chromadb.utils import embedding_functions
from app.core.config import get_settings

def get_chroma_client():
    settings = get_settings()
    # For local persistence
    client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
    return client

def get_or_create_collection(collection_name: str):
    client = get_chroma_client()
    # Using a default embedding function for now, can be replaced with a specific one later
    # For example, SentenceTransformersEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    # For mock, we don't need a real embedding function
    if get_settings().LLM_PROVIDER == "mock":
        # Return a mock collection for dev/testing without actual embeddings
        class MockCollection:
            def add(self, documents, metadatas, ids):
                print(f"MockCollection: Added {len(documents)} documents.")
            def query(self, query_texts, n_results):
                print(f"MockCollection: Queried for {query_texts}")
                return {"documents": [["Mock document 1", "Mock document 2"]], "metadatas": [[{}, {}]], "ids": [["mock_id_1", "mock_id_2"]]}
        return MockCollection()
    else:
        # For real LLMs, we'd need a proper embedding function
        # For now, let's use a dummy one or rely on Chroma's default if available
        # A real implementation would use something like:
        # from langchain_community.embeddings import SentenceTransformerEmbeddings
        # embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        # For simplicity, we'll let Chroma use its default or raise if not configured
        try:
            collection = client.get_or_create_collection(name=collection_name)
        except Exception as e:
            print(f"Warning: Could not get/create Chroma collection with default embedding function. Error: {e}")
            print("Consider configuring a specific embedding function if you encounter issues.")
            # Fallback to a collection without a specified embedding function, might use default
            collection = client.get_or_create_collection(name=collection_name)
        return collection
