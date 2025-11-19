from llama_index.llms.nvidia import NVIDIA
from llama_index.core import Settings
import config

def initialize_llm():
    """Initialize Nvidia Llama model via NIM endpoint."""
    print(f"🤖 Initializing {config.LLM_MODEL}...")
    llm = NVIDIA(
        model=config.LLM_MODEL,
        api_key=config.NVIDIA_API_KEY,
        base_url=config.LLM_BASE_URL,
        temperature=config.TEMPERATURE,
        max_tokens=config.MAX_TOKENS
    )
    Settings.llm = llm
    print("✅ LLM initialized")
    return llm

def generate_with_metadata(query: str, context: str, nodes: list, llm=None) -> dict:
    """Generate answer with metadata."""
    if llm is None:
        llm = initialize_llm()
    
    if not context:
        return {
            "answer": "I don't have enough context to answer this question.",
            "num_sources": 0,
            "avg_relevance_score": 0.0,
            "has_sufficient_context": False
        }
    
    prompt = f"""Answer the question using ONLY the context below. Be concise and cite specific parts.

Context:
{context}

Question: {query}

Answer:"""
    
    print("🤖 Generating response...")
    response = llm.complete(prompt)
    
    return {
        "answer": response.text.strip(),
        "num_sources": len(nodes),
        "avg_relevance_score": round(sum(n.score for n in nodes) / len(nodes), 4) if nodes else 0,
        "has_sufficient_context": True
    }