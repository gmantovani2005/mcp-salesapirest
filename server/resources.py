"""Resources MCP em Português do Brasil."""
from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.client import get_client


CONTEXTO_DATASET = """\
# Contexto do Dataset de Vendas Online

Este dataset oferece uma visão abrangente das transações de vendas online em
diferentes categorias de produtos. Cada pedido (sales order) representa uma
transação única com informações detalhadas:

- **id** — identificador único do pedido
- **date** — data da transação (YYYY-MM-DD)
- **product_id** — produto vendido (ver `sales://categorias` e a tool `listar_produtos`)
- **region_id** — região geográfica do comprador (ver `sales://regioes`)
- **payment_method_id** — método de pagamento (ver `sales://metodos-pagamento`)
- **units_sold** — quantidade de unidades
- **unit_price** — preço por unidade (decimal em string)
- **total_revenue** — receita total da transação (units_sold × unit_price)

## Possibilidades de análise

1. Tendências de vendas ao longo do tempo (sazonalidade, crescimento).
2. Popularidade de categorias de produtos por região.
3. Impacto dos métodos de pagamento sobre volume e receita.
4. Identificação de produtos mais vendidos por categoria para otimizar estoque
   e marketing.
5. Avaliação de desempenho de produtos/categorias por região para campanhas
   segmentadas.

## Tools recomendadas

- `total_vendas_por_regiao`, `total_vendas_por_categoria` — visão agregada
- `top_produtos_por_receita`, `top_produtos_por_quantidade` — rankings
- `vendas_por_periodo` (granularidade `mensal` ou `diario`) — tendências
- `distribuicao_metodos_pagamento` — preferências de pagamento
- `ticket_medio` — valor médio por pedido

> Fonte: https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data
"""


def _json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, default=str)


def register(mcp: FastMCP) -> None:
    """Registra todos os resources no servidor MCP."""

    @mcp.resource(
        "sales://contexto",
        name="Contexto do Dataset de Vendas",
        description="Descrição do dataset, dos campos disponíveis e das análises possíveis (em PT-BR).",
        mime_type="text/markdown",
    )
    def contexto() -> str:
        return CONTEXTO_DATASET

    @mcp.resource(
        "sales://categorias",
        name="Categorias de Produtos",
        description="Lista atual de categorias cadastradas na Sales API (até 1000).",
        mime_type="application/json",
    )
    async def categorias() -> str:
        data = await get_client().list_categories(limit=1000)
        return _json(data)

    @mcp.resource(
        "sales://regioes",
        name="Regiões",
        description="Lista atual de regiões geográficas cadastradas na Sales API.",
        mime_type="application/json",
    )
    async def regioes() -> str:
        data = await get_client().list_regions(limit=1000)
        return _json(data)

    @mcp.resource(
        "sales://metodos-pagamento",
        name="Métodos de Pagamento",
        description="Lista atual de métodos de pagamento aceitos.",
        mime_type="application/json",
    )
    async def metodos_pagamento() -> str:
        data = await get_client().list_payment_methods(limit=1000)
        return _json(data)

    @mcp.resource(
        "sales://saude",
        name="Status da Sales API",
        description="Resposta do endpoint /health da Sales API REST.",
        mime_type="application/json",
    )
    async def saude() -> str:
        data = await get_client().health()
        return _json(data)
