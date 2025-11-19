from typing import List, Dict
from llama_index.core import VectorStoreIndex
from llama_index.core.schema import NodeWithScore
from llama_index.core.postprocessor import LLMRerank
from llama_index.llms.nvidia import NVIDIA
import config


def retrieve_relevant_chunks(
    query: str,
    index: VectorStoreIndex,
    top_k: int = None
) -> List[NodeWithScore]:
    """Retrieve most relevant chunks using semantic search."""
    if top_k is None:
        top_k = config.TOP_K
    
    print(f"🔍 Retrieving top {top_k} chunks...")
    retriever = index.as_retriever(similarity_top_k=top_k)
    nodes = retriever.retrieve(query)
    
    print(f" Retrieved {len(nodes)} chunks")
    for i, node in enumerate(nodes, 1):
        print(f"   {i}. Score: {node.score:.4f} | Length: {len(node.text)} chars")
    
    return nodes


def rerank_with_nvidia(
    query: str,
    nodes: List[NodeWithScore],
    top_n: int = 5
) -> List[NodeWithScore]:
    """Rerank chunks using Nvidia reranker model."""
    if len(nodes) <= top_n:
        return nodes  # No need to rerank if we have few chunks
    
    print(f"🔄 Reranking {len(nodes)} chunks with Nvidia reranker...")
    
    # Initialize Nvidia reranker
    reranker = LLMRerank(
        llm=NVIDIA(
            model="nvidia/llama-3.2-nv-rerankqa-1b-v1",
            api_key=config.NVIDIA_API_KEY,
            base_url=config.LLM_BASE_URL
        ),
        top_n=top_n
    )
    
    # Rerank nodes
    reranked = reranker.postprocess_nodes(nodes, query_str=query)
    
    print(f" Reranked to top {len(reranked)} chunks")
    for i, node in enumerate(reranked, 1):
        print(f"   {i}. Score: {node.score:.4f} | Length: {len(node.text)} chars")
    
    return reranked


def format_context(nodes: List[NodeWithScore]) -> str:
    """Format chunks into context string for LLM."""
    if not nodes:
        print("  Warning: No chunks to format")
        return ""
    
    context_parts = []
    for i, node in enumerate(nodes, 1):
        context_parts.append(f"[Chunk {i}]:\n{node.text}\n")
    
    context = "\n".join(context_parts)
    print(f" Context: {len(nodes)} chunks, {len(context)} chars")
    return context


def retrieve_and_format(query: str, index: VectorStoreIndex, use_reranker: bool = True) -> Dict:
    """
    Complete retrieval pipeline with optional reranking.
    
    Args:
        query: User query
        index: Vector store index
        use_reranker: Whether to use Nvidia reranker (default: True)
    
    Returns:
        Dict with 'context' and 'nodes' keys
    """
    # Retrieve more chunks initially (cast wider net)
    initial_k = config.TOP_K * 2 if use_reranker else config.TOP_K
    nodes = retrieve_relevant_chunks(query, index, top_k=initial_k)
    
    # Rerank if enabled
    if use_reranker and len(nodes) > config.TOP_K:
        nodes = rerank_with_nvidia(query, nodes, top_n=config.TOP_K)
    
    # Format context
    context = format_context(nodes)
    
    return {
        "context": context,
        "nodes": nodes,
        "num_chunks": len(nodes)
    }
