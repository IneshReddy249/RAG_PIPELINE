from typing import List
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings
import chromadb
import config


def initialize_vector_store():
    """
    Initialize ChromaDB and create/load collection.
    Returns the vector store instance.
    """
    print("  Initializing ChromaDB...")
    
    # Create Chroma client
    db = chromadb.PersistentClient(path=str(config.CHROMA_DB_DIR))
    
    # Get or create collection
    chroma_collection = db.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME
    )
    
    # Wrap in LlamaIndex vector store
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    print(f" ChromaDB initialized: {config.CHROMA_COLLECTION_NAME}")
    return vector_store


def embed_and_store(nodes: List) -> VectorStoreIndex:
    """
    Embed nodes using OpenAI and store in ChromaDB.
    Returns the vector store index for querying.
    """
    print("🔢 Embedding and storing documents...")
    
    # Configure global settings
    Settings.embed_model = OpenAIEmbedding(
        model=config.EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY
    )
    
    # Initialize vector store
    vector_store = initialize_vector_store()
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Create index and embed all nodes
    index = VectorStoreIndex(
        nodes=nodes,
        storage_context=storage_context,
        show_progress=True
    )
    
    print(f" Embedded and stored {len(nodes)} chunks")
    return index


def load_existing_index() -> VectorStoreIndex:
    """
    Load existing index from ChromaDB without re-embedding.
    Use this after initial ingestion.
    """
    print(" Loading existing index from ChromaDB...")
    
    # Configure embedding model
    Settings.embed_model = OpenAIEmbedding(
        model=config.EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY
    )
    
    # Load vector store
    vector_store = initialize_vector_store()
    
    # Create index from existing store
    index = VectorStoreIndex.from_vector_store(vector_store)
    
    print(" Index loaded successfully")
    return index


if __name__ == "__main__":
    from document_processor import process_documents
    
    # Process and embed documents
    nodes = process_documents()
    index = embed_and_store(nodes)
    
    print("\n Embedding pipeline complete!")
