# Arquitetura

## Visão geral do fluxo

```
Pergunta do utilizador
        │
        ▼
┌──────────────────┐
│  crisis_check      │  Classifica risco iminente (Groq, temperatura 0,
│  (sempre primeiro) │  saída JSON estrita). Falha → assume risco=true.
└─────────┬──────────┘
          │
   risco? │ sim ──────────► crisis_response (template fixo) ──► FIM
          │
          │ não
          ▼
┌──────────────────┐
│  self_query        │  Classifica a pergunta: juridico / apoio / geral
└─────────┬──────────┘
          ▼
┌──────────────────┐
│  retrieve           │  Busca híbrida (embeddings + BM25) sobre os
│                     │  chunks de base/*.pdf, fundida por RRF
└─────────┬──────────┘
          ▼
┌──────────────────┐
│  generate           │  Groq, com RAG_SYSTEM_PROMPT (tom trauma-
│                     │  informed) + contexto recuperado
└─────────┬──────────┘
          ▼
       Resposta
```

## Porque é que a deteção de crise é um nó separado, e não uma instrução no prompt

Podíamos ter posto "se detetares risco, dá os contactos" dentro do
`RAG_SYSTEM_PROMPT` e deixar tudo correr num único passo. Não fizemos
isso por duas razões:

1. **Garantia estrutural vs. esperança comportamental.** Se a deteção de
   crise for "mais uma instrução" dentro de um prompt grande que também
   pede para citar fontes, manter tom, etc., a probabilidade de o modelo
   ignorar essa instrução numa situação real (texto ambíguo, mensagem
   longa, contexto distrativo) é maior do que se for um classificador
   dedicado, isolado, cuja única tarefa é essa decisão binária.

2. **A resposta de crise nunca é gerada livremente.** Mesmo que o
   classificador acerte, se a *resposta* em si fosse gerada pelo LLM
   "com base na instrução de ser empático", ainda haveria risco de
   alucinação ou tom inadequado exatamente no momento mais sensível.
   Por isso a resposta de crise é um template fixo (`prompt.py`,
   `CRISIS_RESPONSE_TEMPLATE`), preenchido apenas com os contactos —
   nunca texto livre do modelo.

## Falha sempre segura (fail-safe)

`crisis.py` e `self_query.py` assumem o caminho mais seguro em caso de
erro:

- `crisis.py`: se a chamada à Groq falhar, assume `risco_imediato=True`.
  Pior caso: alguém sem risco real vê contactos de apoio sem necessidade
  (custo baixo). O inverso seria muito mais grave.
- `self_query.py`: se falhar, devolve categoria `"geral"`, que não filtra
  nada — pior caso é o retrieval ser ligeiramente menos preciso, nunca
  excluir conteúdo relevante por engano.

## Privacidade

`rag/settings.py` define `LOG_USER_MESSAGE_CONTENT = False`. Isto é
intencional: por defeito, o sistema não deve persistir o conteúdo das
mensagens das pessoas. Antes de adicionar qualquer histórico de
conversas, analytics, ou logging de debugging que inclua o texto das
mensagens, a equipa deve avaliar:

- Quem pode aceder a esses dados?
- Por quanto tempo são guardados?
- Isto está coberto pela política de privacidade comunicada ao utilizador?

Numa aplicação deste tipo, um log mal protegido é um risco real para a
segurança física das pessoas que o usam.

## Limites do que o agente faz

O agente dá **informação**, não terapia nem aconselhamento jurídico
vinculativo. Isto está refletido em `RAG_SYSTEM_PROMPT`
(`rag/graph/prompt.py`) e deve ser mantido em qualquer alteração futura
ao prompt. Para apoio contínuo, a resposta deve sempre apontar para as
linhas de apoio listadas em `rag/settings.py`, nunca tentar substituí-las.

## Sobre os contactos de apoio

Os contactos em `SUPPORT_CONTACTS` (`rag/settings.py`) foram verificados
em Junho de 2026 através de pesquisa nas fontes públicas disponíveis
(UNFPA Moçambique, ReliefWeb, campanhas da Procuradoria-Geral da
República). **Antes de lançar em produção, confirmar estes números
diretamente com uma organização parceira local** — linhas de apoio podem
mudar e este é o dado mais crítico de todo o sistema.
