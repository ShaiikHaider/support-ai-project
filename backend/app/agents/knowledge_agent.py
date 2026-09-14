"""
Knowledge Retrieval Agent
--------------------------
Searches the FAQ / product documentation / support policy knowledge base
(RAG over ChromaDB). Output is explicitly retrieved information — it is
never presented to the customer as-is; the Resolution Agent turns it into
guidance, and the Reviewer Agent checks it was used correctly.
"""
from app.agents.state import SupportGraphState
from app.agents.tracing import trace_step
from app.core.llm_client import chat_completion
from app.rag.vector_store import retrieve

SYNTHESIS_PROMPT = """You are the Knowledge Retrieval Agent. You are given
raw excerpts retrieved from the support knowledge base (FAQs, product docs,
policies). Write a short, neutral synthesis (3-5 sentences) of what these
sources say that is relevant to the customer's issue. Do NOT recommend
what to do yet — that is the Resolution Agent's job. Just summarize facts
and policy from the retrieved sources."""


async def run_knowledge_agent(state: SupportGraphState) -> SupportGraphState:
    query = state["intent_summary"] or state["customer_query"]
    category = state.get("category")

    with trace_step(state, "Knowledge Retrieval Agent", input_summary=query) as trace:
        chunks = retrieve(query=query, category_hint=category, top_k=4)

        retrieved_chunks = [
            {
                "id": c.id,
                "title": c.title,
                "category": c.category,
                "content": c.content,
                "relevance_score": c.relevance_score,
            }
            for c in chunks
        ]
        state["retrieved_chunks"] = retrieved_chunks

        if not chunks:
            state["knowledge_synthesis"] = "No directly relevant knowledge-base entries were found."
            trace["output_summary"] = "0 chunks retrieved."
            return state

        sources_text = "\n\n".join(f"[{c.title}] ({c.category}): {c.content}" for c in chunks)
        synthesis = await chat_completion(
            system_prompt=SYNTHESIS_PROMPT,
            user_prompt=f"Customer issue: {query}\n\nRetrieved sources:\n{sources_text}",
        )
        state["knowledge_synthesis"] = synthesis
        trace["output_summary"] = f"{len(chunks)} chunks retrieved; synthesis: {synthesis[:200]}"

    return state
