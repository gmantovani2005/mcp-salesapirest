# mcp-salesapirest

Servidor **MCP (Model Context Protocol)** em Python que envolve a **Sales
Dataset API REST** e expõe ferramentas, recursos e prompts — todos em
**Português do Brasil** — para análise dos dados de vendas a partir de um
assistente de IA (Claude Desktop, Claude Code, MCP Inspector, etc.).

A Sales API descrita em [`docs/swagger.json`](docs/swagger.json) oferece
apenas operações CRUD sobre Categorias, Regiões, Métodos de Pagamento,
Produtos e Pedidos de Venda. Este MCP **agrega** esses dados brutos em
respostas analíticas (top produtos, vendas por região/categoria/período,
ticket médio, distribuição de métodos de pagamento, etc.).

---

## Pré-requisitos

- [`uv`](https://docs.astral.sh/uv/) (gerenciador de pacotes Python)
- Python 3.14 (instalado automaticamente pelo `uv` se necessário)
- Uma instância da Sales Dataset API acessível (por padrão em
  `http://localhost:8000`)
- Para o modo container: Docker / Docker Compose ou um cluster Kubernetes

---

## Instalação

```bash
git clone <este-repositorio>
cd mcp-salesapirest
uv sync                       # cria .venv e instala dependências
cp .env.example .env          # ajuste SALES_API_BASE_URL conforme seu ambiente
```

---

## Configuração (`.env`)

| Variável             | Default                  | Descrição                                                  |
| -------------------- | ------------------------ | ---------------------------------------------------------- |
| `SALES_API_BASE_URL` | `http://localhost:8000`  | URL base da Sales Dataset API.                             |
| `SALES_API_TIMEOUT`  | `30`                     | Timeout HTTP em segundos.                                  |
| `MCP_TRANSPORT`      | `stdio`                  | `stdio` em dev (Inspector) ou `sse` em container.          |
| `MCP_HOST`           | `0.0.0.0`                | Interface para escuta SSE.                                 |
| `MCP_PORT`           | `8080`                   | Porta SSE.                                                 |

---

## Uso em desenvolvimento (stdio + MCP Inspector)

```bash
uv run mcp dev main.py
```

O comando abre o **MCP Inspector** no navegador. Lá você pode listar as
**tools**, **resources** e **prompts** registradas, executar chamadas e
inspecionar o JSON retornado.

### Conectar ao Claude Desktop

Em `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) ou equivalente:

```json
{
  "mcpServers": {
    "sales-dataset": {
      "command": "uv",
      "args": ["--directory", "/caminho/para/mcp-salesapirest", "run", "main.py"],
      "env": {
        "SALES_API_BASE_URL": "http://localhost:8000",
        "MCP_TRANSPORT": "stdio"
      }
    }
  }
}
```

---

## Uso em container (SSE)

### Docker Compose

```bash
docker compose up --build
# o servidor MCP fica disponível em http://localhost:8080/sse
```

A variável `SALES_API_BASE_URL` aponta por padrão para
`http://host.docker.internal:8000` (a Sales API rodando no host).
Sobrescreva pela linha de comando se necessário:

```bash
SALES_API_BASE_URL=https://api.example.com docker compose up
```

### Kubernetes

```bash
kubectl apply -f .container/deployment.yaml
kubectl apply -f .container/service.yaml
```

Edite o `ConfigMap` `mcp-salesapirest-config` (no
`.container/deployment.yaml`) para ajustar `SALES_API_BASE_URL` ao endereço
real da Sales API no cluster.

---

## Tools disponíveis

### Consulta direta

| Tool                          | Descrição                                                                |
| ----------------------------- | ------------------------------------------------------------------------ |
| `listar_categorias`           | Lista categorias (filtro por nome, paginação).                           |
| `obter_categoria`             | Recupera uma categoria por ID.                                           |
| `listar_regioes`              | Lista regiões geográficas.                                               |
| `obter_regiao`                | Recupera uma região por ID.                                              |
| `listar_metodos_pagamento`    | Lista métodos de pagamento.                                              |
| `obter_metodo_pagamento`      | Recupera um método de pagamento por ID.                                  |
| `listar_produtos`             | Lista produtos (filtros: nome, categoria, faixa de preço).               |
| `obter_produto`               | Recupera um produto por ID.                                              |
| `listar_pedidos_venda`        | Lista pedidos com filtros (produto, região, método, datas, faixa total). |
| `obter_pedido_venda`          | Recupera um pedido por ID.                                               |
| `verificar_saude_api`         | Confere o `/health` da Sales API.                                        |

### Analíticas (agregam pedidos paginados)

| Tool                              | Devolve                                                              |
| --------------------------------- | -------------------------------------------------------------------- |
| `total_vendas_por_regiao`         | Receita, unidades e nº de pedidos por região.                        |
| `total_vendas_por_categoria`      | Mesma agregação por categoria de produto.                            |
| `top_produtos_por_receita`        | Top N produtos por receita (filtros opcionais de data/região).       |
| `top_produtos_por_quantidade`     | Top N produtos por unidades vendidas.                                |
| `vendas_por_periodo`              | Série temporal mensal/diária de receita e unidades.                  |
| `distribuicao_metodos_pagamento`  | Pedidos e receita por método de pagamento, com percentuais.          |
| `ticket_medio`                    | Ticket médio (com filtros de data, região e categoria).              |

---

## Resources disponíveis

| URI                          | Descrição                                                       |
| ---------------------------- | --------------------------------------------------------------- |
| `sales://contexto`           | Contexto do dataset (markdown) — leitura recomendada inicial.   |
| `sales://categorias`         | Lista atualizada de categorias (JSON).                          |
| `sales://regioes`            | Lista atualizada de regiões (JSON).                             |
| `sales://metodos-pagamento`  | Lista atualizada de métodos de pagamento (JSON).                |
| `sales://saude`              | Status do `/health` da Sales API (JSON).                        |

---

## Prompts disponíveis

| Prompt                         | Argumentos                                |
| ------------------------------ | ----------------------------------------- |
| `analise_geral_de_vendas`      | `periodo?`                                |
| `comparar_regioes`             | `regiao_a`, `regiao_b`, `periodo?`        |
| `identificar_tendencias`       | `granularidade` (`mensal` ou `diario`)    |
| `recomendacoes_de_marketing`   | `categoria?`, `regiao?`                   |

---

## Estrutura do projeto

```
mcp-salesapirest/
├── .container/                 # Dockerfile + manifestos Kubernetes
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
├── main.py                     # entrypoint (stdio ou sse)
├── pyproject.toml
└── server/
    ├── __init__.py             # instância FastMCP + registro
    ├── client.py               # cliente HTTP (httpx) da Sales API
    ├── config.py               # Settings (pydantic-settings)
    ├── prompts.py              # prompts (PT-BR)
    ├── resources.py            # resources (PT-BR)
    └── tools.py                # tools de consulta + analíticas (PT-BR)
```

---

## Licença

Uso interno / educacional. Dataset original:
[Online Sales Dataset (Kaggle)](https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data).
