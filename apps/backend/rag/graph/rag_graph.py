"""
Grafo principal do agente, usando LangGraph.

Fluxo:

    crisis_check ──risco_imediato──> crisis_response ──> END
         │
         └──sem risco imediato──> self_query ──> retrieve ──> generate ──> END

A decisão de desenho mais importante deste módulo: `crisis_check` corre
SEMPRE, em toda mensagem, como primeiro nó -- não é uma feature opcional
nem um passo que só ativa "se a pergunta parecer grave". Mensagens de
risco real raramente se anunciam como tal.
"""

from typing import TypedDict

from groq import Groq
from langgraph.graph import END, StateGraph

from rag.graph.crisis import check_crisis
from rag.graph.prompt import CRISIS_RESPONSE_TEMPLATE, RAG_SYSTEM_PROMPT, build_rag_user_prompt, format_contacts
from rag.retrieval.retriever import HybridRetriever
from rag.retrieval.self_query import classify_query
from rag.settings import EMERGENCY_NOTE, GROQ_API_KEY, GROQ_MODEL

groq_client = Groq(api_key=GROQ_API_KEY)
_retriever: HybridRetriever | None = None


def _get_retriever() -> HybridRetriever:
    """Lazy-load do retriever (carrega modelo de embeddings só quando necessário)."""
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


class AgentState(TypedDict, total=False):
    question: str
    is_crisis: bool
    crisis_reason: str
    category: str
    retrieved_chunks: list[dict]
    answer: str


def node_crisis_check(state: AgentState) -> AgentState:
    result = check_crisis(state["question"])
    return {**state, "is_crisis": result.is_immediate_risk, "crisis_reason": result.reason}


def node_crisis_response(state: AgentState) -> AgentState:
    answer = CRISIS_RESPONSE_TEMPLATE.format(
        contacts=format_contacts(), emergency_note=EMERGENCY_NOTE
    )
    return {**state, "answer": answer}


def node_self_query(state: AgentState) -> AgentState:
    result = classify_query(state["question"])
    return {**state, "category": result.category}


def node_retrieve(state: AgentState) -> AgentState:
    retriever = _get_retriever()
    chunks = retriever.retrieve(state["question"], top_k=4)
    return {**state, "retrieved_chunks": chunks}


def node_generate(state: AgentState) -> AgentState:
    chunks = state.get("retrieved_chunks", [])
    context_blocks = [f"[Fonte: {c['source']}, p.{c['page']}]\n{c['text']}" for c in chunks]
    context = "\n\n---\n\n".join(context_blocks) if context_blocks else "(sem documentos relevantes encontrados)"

    user_prompt = build_rag_user_prompt(state["question"], context)

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": RAG_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return {**state, "answer": response.choices[0].message.content}


def route_after_crisis_check(state: AgentState) -> str:
    return "crisis_response" if state.get("is_crisis") else "self_query"


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("crisis_check", node_crisis_check)
    graph.add_node("crisis_response", node_crisis_response)
    graph.add_node("self_query", node_self_query)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("generate", node_generate)

    graph.set_entry_point("crisis_check")
    graph.add_conditional_edges(
        "crisis_check",
        route_after_crisis_check,
        {"crisis_response": "crisis_response", "self_query": "self_query"},
    )
    graph.add_edge("crisis_response", END)
    graph.add_edge("self_query", "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile()


_compiled_graph = None


def run_agent(question: str) -> AgentState:
    """Ponto de entrada principal: corre o grafo completo para uma pergunta."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph.invoke({"question": question})
