from pathlib import Path
from typing import List
from llama_index.core import SimpleDirectoryReader, Document
import config


def load_documents(data_dir: Path) -> List[Document]:
    """
    Load documents from the raw data directory.
    Supports PDF, TXT, and other text formats.
    """
    if not data_dir.exists():
        raise ValueError(f"Data directory does not exist: {data_dir}")
    
    print(f"📂 Loading documents from: {data_dir}")
    
    reader = SimpleDirectoryReader(
        input_dir=str(data_dir),
        recursive=True,
        required_exts=[".pdf", ".txt", ".md"]
    )
    
    documents = reader.load_data()
    print(f"✅ Loaded {len(documents)} documents")
    
    return documents


def chunk_documents(documents: List[Document]) -> List:
    """
    Split documents into fixed-size chunks.
    Faster and cheaper than semantic chunking, still effective.
    """
    print("🔪 Chunking documents...")
    
    from llama_index.core.node_parser import SentenceSplitter
    
    splitter = SentenceSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    
    nodes = splitter.get_nodes_from_documents(documents)
    
    print(f"✅ Created {len(nodes)} chunks")
    print(f"📊 Avg chunk size: {sum(len(n.text) for n in nodes) // len(nodes)} chars")
    
    return nodes


def process_documents() -> List:
    """
    Main function: Load and chunk documents.
    Returns chunks ready for embedding.
    """
    documents = load_documents(config.RAW_DATA_DIR)
    nodes = chunk_documents(documents)
    return nodes


if __name__ == "__main__":
    nodes = process_documents()
    print(f"\n✅ Processing complete: {len(nodes)} chunks ready for embedding")