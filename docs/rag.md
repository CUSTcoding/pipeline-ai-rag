# RAG — Notas e fontes

## Contactos de apoio: fontes (verificado Junho 2026)

| Contacto | Fonte | Notas |
|---|---|---|
| Linha Verde 1458 | UNFPA Moçambique; relatórios mensais ReliefWeb (até Out/2025) | Originalmente lançada em 2019 para resposta humanitária, expandida para incluir apoio a violência baseada no género |
| Linha Fala Criança 116 | Boa Internet MZ (mz.goodinternet.org) | Específica para vítimas menores de idade |
| Linha 94321 | Nações Unidas em Moçambique (mozambique.un.org), lançada Jun/2025 | Parceria PGR + PRM + UNODC; mensagens de áudio gravadas |
| PRM 119 | Conhecimento geral / número de emergência nacional | Confirmar formalmente com a equipa antes de produção |

**Recomendação:** antes do lançamento, validar todos os números com uma
organização parceira local (ex.: associações de apoio a vítimas, ONU
Mulheres Moçambique, ou a própria PGR) — informação encontrada via
pesquisa web pode estar desatualizada ou incompleta.

## Categorização de documentos

`rag/ingest/extract_text.py` define `CATEGORY_MAP`, que associa cada
ficheiro PDF a uma categoria (`juridico`, `apoio`, `geral`). Esta
categoria é usada por `self_query.py` para, no futuro, permitir filtrar
o retrieval — por exemplo, perguntas práticas ("onde denuncio?") podem
priorizar documentos de categoria `apoio`, enquanto perguntas sobre
direitos priorizam `juridico`.

**Nota de implementação:** na versão atual, a categoria é calculada e
guardada no payload de cada chunk, mas o `retriever.py` ainda não aplica
o filtro automaticamente — isso é um próximo passo natural (usar
`category` devolvida por `classify_query()` como filtro no `qdrant.search`).

## Sugestões de documentos a adicionar

Para tornar o agente mais útil na categoria "apoio" (atualmente vazia),
considerar adicionar:

- Guia de procedimento de denúncia (passo a passo, em linguagem simples)
- Lista de Centros de Atendimento Integrado (CAI) por província
- Informação sobre Casas de Abrigo disponíveis
- Direitos específicos de mulheres e crianças vítimas de violência
  (ex.: Lei de Prevenção e Combate à Violência contra a Mulher, se
  aplicável — confirmar referência legal exata com a equipa jurídica)
