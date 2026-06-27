# API

## `POST /chat`

Envia uma pergunta ao agente e recebe a resposta já processada pelo
grafo completo (deteção de crise → retrieval → geração).

**Request:**
```json
{ "message": "Quais são os meus direitos como vítima de violência doméstica?" }
```

**Response:**
```json
{ "answer": "..." }
```

## `GET /health`

Verifica se a API está a correr.

**Response:**
```json
{ "status": "ok" }
```

## Notas para o frontend

- Esta API não mantém histórico de conversa entre pedidos (ver
  `docs/architecture.md`, secção Privacidade). Cada pedido é
  independente. Se for necessário contexto de conversa no futuro,
  avaliar cuidadosamente como e onde esse histórico é guardado.
- Não há autenticação nesta versão — adequado para um MVP interno, mas
  reavaliar antes de expor publicamente.
