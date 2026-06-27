"""
Ponto de entrada do módulo RAG. Usado pela API (apps/backend/main.py) e
também útil para testes manuais via terminal.

Uso direto (terminal):
    python -m rag.app "Quais são os meus direitos se sofri violência doméstica?"
"""

import sys

from rag.graph.rag_graph import run_agent


def ask(question: str) -> str:
    """Função principal exposta à API: recebe uma pergunta, devolve a resposta
    do agente (já passou pela verificação de crise, retrieval e geração)."""
    result = run_agent(question)
    return result.get("answer", "")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python -m rag.app \"a tua pergunta\"")
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    print(f"Pergunta: {question}\n")
    print(ask(question))
