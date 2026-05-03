# mcp-salesapirest

Python **MCP (Model Context Protocol)** server that wraps the **Sales Dataset REST API** and exposes tools, resources, and prompts — all in **Brazilian Portuguese** — to analyze sales data from an AI assistant (Claude Desktop, Claude Code, MCP Inspector, etc.).

The Sales API described in [`docs/swagger.json`](docs/swagger.json) only offers CRUD operations for Categories, Regions, Payment Methods, Products, and Sales Orders. This MCP **aggregates** this raw data into analytical responses (top products, sales by region/category/period, average ticket, payment method distribution, etc.).

---

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.14 (automatically installed by `uv` if needed)
- An accessible instance of the Sales Dataset API (by default at `http://localhost:8000`)
- For container mode: Docker / Docker Compose or a Kubernetes cluster

---

## Installation

```bash
git clone <this-repository>
cd mcp-salesapirest
uv sync                       # creates .venv and installs dependencies
cp .env.example .env          # adjust SALES_API_BASE_URL according to your environment
```

---

## Configuration (`.env`)

| Variable             | Default                  | Description                                                  |
| -------------------- | ------------------------ | ------------------------------------------------------------ |
| `SALES_API_BASE_URL` | `http://localhost:8000`  | Sales Dataset API base URL.                                  |
| `SALES_API_TIMEOUT`  | `30`                     | HTTP timeout in seconds.                                     |
| `MCP_TRANSPORT`      | `stdio`                  | `stdio` in dev (Inspector) or `sse` in container.            |
| `MCP_HOST`           | `0.0.0.0`                | Interface to listen for SSE.                                 |
| `MCP_PORT`           | `8080`                   | SSE port.                                                    |

---

## Development Use (stdio + MCP Inspector)

```bash
uv run mcp dev main.py
```

This command opens the **MCP Inspector** in your browser. There you can list the registered **tools**, **resources**, and **prompts**, execute calls, and inspect the returned JSON.

### Connect to Claude Desktop

In `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or equivalent:

```json
{
  "mcpServers": {
    "sales-dataset": {
      "command": "uv",
      "args": ["--directory", "/path/to/mcp-salesapirest", "run", "main.py"],
      "env": {
        "SALES_API_BASE_URL": "http://localhost:8000",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Container Use (SSE)

### Docker Compose

```bash
docker compose up --build
# the MCP server is available at http://localhost:8080/sse
```

The `SALES_API_BASE_URL` variable defaults to `http://host.docker.internal:8000` (the Sales API running on the host).
Overwrite it via command line if necessary:

```bash
SALES_API_BASE_URL=https://api.example.com docker compose up
```

### Kubernetes

```bash
kubectl apply -f .container/deployment.yaml
kubectl apply -f .container/service.yaml
```

Edit the `ConfigMap` `mcp-salesapirest-config` (in `.container/deployment.yaml`) to adjust `SALES_API_BASE_URL` to the real address of the Sales API in the cluster.

---

## Available Tools

### Direct Query

| Tool                          | Description                                                              |
| ----------------------------- | ------------------------------------------------------------------------ |
| `listar_categorias`           | Lists categories (filter by name, pagination).                           |
| `obter_categoria`             | Retrieves a category by ID.                                              |
| `listar_regioes`              | Lists geographical regions.                                              |
| `obter_regiao`                | Retrieves a region by ID.                                                |
| `listar_metodos_pagamento`    | Lists payment methods.                                                   |
| `obter_metodo_pagamento`      | Retrieves a payment method by ID.                                        |
| `listar_produtos`             | Lists products (filters: name, category, price range).                   |
| `obter_produto`               | Retrieves a product by ID.                                               |
| `listar_pedidos_venda`        | Lists orders with filters (product, region, method, dates, total range). |
| `obter_pedido_venda`          | Retrieves an order by ID.                                                |
| `verificar_saude_api`         | Checks the Sales API `/health`.                                          |

### Analytics (aggregates paginated orders)

| Tool                              | Returns                                                              |
| --------------------------------- | -------------------------------------------------------------------- |
| `total_vendas_por_regiao`         | Revenue, units, and number of orders by region.                      |
| `total_vendas_por_categoria`      | Same aggregation by product category.                                |
| `top_produtos_por_receita`        | Top N products by revenue (optional date/region filters).            |
| `top_produtos_por_quantidade`     | Top N products by units sold.                                        |
| `vendas_por_periodo`              | Monthly/daily time series of revenue and units.                      |
| `distribuicao_metodos_pagamento`  | Orders and revenue by payment method, with percentages.              |
| `ticket_medio`                    | Average ticket (with date, region, and category filters).            |

---

## Available Resources

| URI                          | Description                                                     |
| ---------------------------- | --------------------------------------------------------------- |
| `sales://contexto`           | Dataset context (markdown) — initial reading recommended.       |
| `sales://categorias`         | Updated list of categories (JSON).                              |
| `sales://regioes`            | Updated list of regions (JSON).                                 |
| `sales://metodos-pagamento`  | Updated list of payment methods (JSON).                         |
| `sales://saude`              | Sales API `/health` status (JSON).                              |

---

## Available Prompts

| Prompt                         | Arguments                                 |
| ------------------------------ | ----------------------------------------- |
| `analise_geral_de_vendas`      | `periodo?`                                |
| `comparar_regioes`             | `regiao_a`, `regiao_b`, `periodo?`        |
| `identificar_tendencias`       | `granularidade` (`mensal` or `diario`)    |
| `recomendacoes_de_marketing`   | `categoria?`, `regiao?`                   |

---

## Project Structure

```
mcp-salesapirest/
├── .container/                 # Dockerfile + Kubernetes manifests
│   ├── Dockerfile
│   ├── deployment.yaml
│   └── service.yaml
├── docker-compose.yaml
├── .dockerignore
├── .env.example
├── docs/
│   ├── 00-promptinicial.md
│   ├── data-sales.md
│   └── swagger.json
├── main.py                     # entrypoint (stdio or sse)
├── pyproject.toml
└── server/
    ├── __init__.py             # FastMCP instance + registration
    ├── client.py               # Sales API HTTP client (httpx)
    ├── config.py               # Settings (pydantic-settings)
    ├── prompts.py              # prompts (PT-BR)
    ├── resources.py            # resources (PT-BR)
    └── tools.py                # query + analytics tools (PT-BR)
```

---

## License

Internal / educational use. Original dataset:
[Online Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data).
