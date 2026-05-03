# CLAUDE.md

Este arquivo orienta o Claude Code (claude.ai/code) ao trabalhar neste
repositório.

## Visão geral

`mcp-salesapirest` é um servidor **Model Context Protocol** em Python que
envolve a **Sales Dataset API REST** (descrita em `docs/swagger.json`).

A Sales API só expõe CRUD; **o valor deste MCP está nas tools analíticas**
de `server/tools.py`, que paginam `GET /sales-orders` com filtros e agregam
em Python (top produtos, vendas por região/categoria/período, ticket médio,
distribuição de métodos de pagamento).

> **Idioma**: todas as descrições de tools, resources, prompts e mensagens
> ao usuário devem estar em **Português do Brasil** — é uma exigência
> explícita do projeto, para alinhar com os prompts do usuário.

## Arquitetura

```
main.py                 → escolhe stdio (dev) ou sse (container) via MCP_TRANSPORT
└── server/
    ├── __init__.py     → cria FastMCP e chama prompts/resources/tools.register(mcp)
    ├── config.py       → Settings (pydantic-settings) lê .env
    ├── client.py       → SalesAPIClient (httpx.AsyncClient) + paginate()
    ├── tools.py        → @mcp.tool — consulta direta + 7 tools analíticas
    ├── resources.py    → @mcp.resource — sales://contexto, sales://categorias, ...
    └── prompts.py      → @mcp.prompt — analise_geral_de_vendas, comparar_regioes, ...
```

- **Cliente HTTP**: singleton lazy via `get_client()` em `server/client.py`.
  Use `client.paginate(path, params, page_size=1000)` para varrer todas as
  páginas — **necessário** nas tools analíticas, porque a Sales API limita
  cada chamada a 1000 itens.
- **Decimais**: `total_revenue`/`unit_price` chegam como string. Use
  `Decimal(str(value))` ao agregar para evitar erros de ponto flutuante; só
  converta para `float` no payload final (já há helpers `_to_decimal`/`_f`
  em `tools.py`).
- **Transporte SSE**: configurado por `MCP_HOST`/`MCP_PORT` na construção
  do `FastMCP` em `server/__init__.py`. Em container, `MCP_TRANSPORT=sse` é
  definido por padrão no `Dockerfile`.

## Comandos comuns

```bash
# Instalar dependências
uv sync

# Desenvolvimento — abre MCP Inspector (stdio)
uv run mcp dev main.py

# Rodar diretamente (respeita MCP_TRANSPORT do .env)
uv run main.py

# Container local (SSE em :8080)
docker compose up --build

# Kubernetes
kubectl apply -f .container/deployment.yaml -f .container/service.yaml
```

## Convenções

- **PT-BR obrigatório** em descriptions, docstrings de tool, nomes de
  parâmetros visíveis ao LLM e textos de prompt.
- Nomes de tools em **snake_case PT-BR** (`listar_categorias`,
  `total_vendas_por_regiao`, `ticket_medio`).
- Tipos: anotações modernas (`int | None`, `list[dict[str, Any]]`).
- Ao adicionar uma tool nova:
  1. Implemente em `server/tools.py` dentro de `register(mcp)`.
  2. Use `get_client()` — não instancie `SalesAPIClient` diretamente.
  3. Documente-a no `README.md` (tabela de tools).
- Ao adicionar um resource: registre em `server/resources.py` e atualize a
  tabela de resources no README.
- Ao adicionar um endpoint cliente: estenda `SalesAPIClient` em
  `server/client.py` antes de criar a tool correspondente.

## Pontos de atenção

- A Sales API **não** tem endpoints analíticos — toda agregação acontece
  no MCP. Cuidado com o tamanho dos dados: para datasets muito grandes,
  considere adicionar filtros obrigatórios de período nas tools analíticas.
- O `Settings` carrega `.env` automaticamente via `pydantic-settings`. Não
  hardcode URLs; sempre passe pelo `settings`.
- O cliente `httpx` é assíncrono; **todas** as tools precisam ser `async`.
- O `Dockerfile` usa Python 3.14 (`requires-python = ">=3.14"` no
  `pyproject.toml`). Mantenha alinhado se atualizar a versão.

## Documentação de referência

- `docs/swagger.json` — especificação OpenAPI 3.1 da Sales API.
- `docs/data-sales.md` — descrição do dataset (campos e insights).
- `docs/00-promptinicial.md` — prompt original que originou o projeto.
