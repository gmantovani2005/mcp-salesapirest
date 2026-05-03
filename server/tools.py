"""Ferramentas (tools) MCP para consulta e análise de vendas.

Todas as descrições estão em Português do Brasil para alinhar com os prompts
dos usuários, que também devem estar em PT-BR.
"""
from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from mcp.server.fastmcp import FastMCP

from server.client import get_client


def _to_decimal(value: Any) -> Decimal:
    if value is None:
        return Decimal("0")
    return Decimal(str(value))


def _f(value: Decimal) -> float:
    return float(value)


def register(mcp: FastMCP) -> None:
    """Registra todas as tools no servidor MCP."""

    # ---------------- Consulta direta -----------------------------------

    @mcp.tool(description="Lista as categorias de produtos cadastradas. Aceita filtro parcial por nome (case-insensitive) e paginação.")
    async def listar_categorias(
        nome: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """Devolve categorias de produtos da Sales API."""
        return await get_client().list_categories(name=nome, skip=skip, limit=limit)

    @mcp.tool(description="Obtém uma categoria pelo seu identificador.")
    async def obter_categoria(categoria_id: int) -> dict[str, Any]:
        return await get_client().get_category(categoria_id)

    @mcp.tool(description="Lista as regiões geográficas cadastradas. Aceita filtro parcial por nome.")
    async def listar_regioes(
        nome: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await get_client().list_regions(name=nome, skip=skip, limit=limit)

    @mcp.tool(description="Obtém uma região pelo seu identificador.")
    async def obter_regiao(regiao_id: int) -> dict[str, Any]:
        return await get_client().get_region(regiao_id)

    @mcp.tool(description="Lista os métodos de pagamento cadastrados. Aceita filtro parcial por nome.")
    async def listar_metodos_pagamento(
        nome: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await get_client().list_payment_methods(name=nome, skip=skip, limit=limit)

    @mcp.tool(description="Obtém um método de pagamento pelo seu identificador.")
    async def obter_metodo_pagamento(metodo_pagamento_id: int) -> dict[str, Any]:
        return await get_client().get_payment_method(metodo_pagamento_id)

    @mcp.tool(description="Lista produtos com filtros opcionais por nome, categoria e faixa de preço unitário.")
    async def listar_produtos(
        nome: str | None = None,
        categoria_id: int | None = None,
        preco_min: float | None = None,
        preco_max: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await get_client().list_products(
            name=nome,
            category_id=categoria_id,
            min_price=preco_min,
            max_price=preco_max,
            skip=skip,
            limit=limit,
        )

    @mcp.tool(description="Obtém um produto pelo seu identificador.")
    async def obter_produto(produto_id: int) -> dict[str, Any]:
        return await get_client().get_product(produto_id)

    @mcp.tool(
        description=(
            "Lista pedidos de venda com filtros opcionais por produto, região, "
            "método de pagamento, intervalo de datas (YYYY-MM-DD) e faixa de receita total. "
            "Use a paginação (skip/limit) para varrer grandes volumes."
        )
    )
    async def listar_pedidos_venda(
        produto_id: int | None = None,
        regiao_id: int | None = None,
        metodo_pagamento_id: int | None = None,
        data_de: str | None = None,
        data_ate: str | None = None,
        total_min: float | None = None,
        total_max: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await get_client().list_sales_orders(
            product_id=produto_id,
            region_id=regiao_id,
            payment_method_id=metodo_pagamento_id,
            date_from=data_de,
            date_to=data_ate,
            min_total=total_min,
            max_total=total_max,
            skip=skip,
            limit=limit,
        )

    @mcp.tool(description="Obtém um pedido de venda pelo seu identificador.")
    async def obter_pedido_venda(pedido_id: int) -> dict[str, Any]:
        return await get_client().get_sales_order(pedido_id)

    @mcp.tool(description="Verifica a disponibilidade da Sales API (endpoint /health).")
    async def verificar_saude_api() -> dict[str, Any]:
        return await get_client().health()

    # ---------------- Analíticas ----------------------------------------

    @mcp.tool(
        description=(
            "Agrega a receita total, a quantidade de unidades vendidas e o número de pedidos "
            "por região, opcionalmente restringindo a um intervalo de datas (YYYY-MM-DD). "
            "Útil para comparar desempenho geográfico."
        )
    )
    async def total_vendas_por_regiao(
        data_de: str | None = None,
        data_ate: str | None = None,
    ) -> list[dict[str, Any]]:
        client = get_client()
        orders = await client.all_sales_orders(date_from=data_de, date_to=data_ate)
        regions = {r["id"]: r["name"] for r in await client.list_regions(limit=1000)}

        agg: dict[int, dict[str, Any]] = defaultdict(
            lambda: {"pedidos": 0, "unidades": 0, "receita": Decimal("0")}
        )
        for o in orders:
            a = agg[o["region_id"]]
            a["pedidos"] += 1
            a["unidades"] += int(o["units_sold"])
            a["receita"] += _to_decimal(o["total_revenue"])

        result = [
            {
                "regiao_id": rid,
                "regiao": regions.get(rid, f"#{rid}"),
                "pedidos": v["pedidos"],
                "unidades": v["unidades"],
                "receita": _f(v["receita"]),
            }
            for rid, v in agg.items()
        ]
        result.sort(key=lambda x: x["receita"], reverse=True)
        return result

    @mcp.tool(
        description=(
            "Agrega receita, unidades e número de pedidos por categoria de produto, "
            "opcionalmente restringindo a um intervalo de datas (YYYY-MM-DD)."
        )
    )
    async def total_vendas_por_categoria(
        data_de: str | None = None,
        data_ate: str | None = None,
    ) -> list[dict[str, Any]]:
        client = get_client()
        orders = await client.all_sales_orders(date_from=data_de, date_to=data_ate)
        products = {p["id"]: p for p in await client.paginate("/products")}
        categories = {c["id"]: c["name"] for c in await client.list_categories(limit=1000)}

        agg: dict[int, dict[str, Any]] = defaultdict(
            lambda: {"pedidos": 0, "unidades": 0, "receita": Decimal("0")}
        )
        for o in orders:
            prod = products.get(o["product_id"])
            if prod is None:
                continue
            cid = prod["category_id"]
            a = agg[cid]
            a["pedidos"] += 1
            a["unidades"] += int(o["units_sold"])
            a["receita"] += _to_decimal(o["total_revenue"])

        result = [
            {
                "categoria_id": cid,
                "categoria": categories.get(cid, f"#{cid}"),
                "pedidos": v["pedidos"],
                "unidades": v["unidades"],
                "receita": _f(v["receita"]),
            }
            for cid, v in agg.items()
        ]
        result.sort(key=lambda x: x["receita"], reverse=True)
        return result

    @mcp.tool(
        description=(
            "Retorna os N produtos com maior receita total, opcionalmente restringindo "
            "a um intervalo de datas e/ou a uma região."
        )
    )
    async def top_produtos_por_receita(
        n: int = 10,
        data_de: str | None = None,
        data_ate: str | None = None,
        regiao_id: int | None = None,
    ) -> list[dict[str, Any]]:
        client = get_client()
        orders = await client.all_sales_orders(
            date_from=data_de, date_to=data_ate, region_id=regiao_id
        )
        products = {p["id"]: p for p in await client.paginate("/products")}

        agg: dict[int, dict[str, Any]] = defaultdict(
            lambda: {"unidades": 0, "receita": Decimal("0"), "pedidos": 0}
        )
        for o in orders:
            a = agg[o["product_id"]]
            a["unidades"] += int(o["units_sold"])
            a["receita"] += _to_decimal(o["total_revenue"])
            a["pedidos"] += 1

        ranked = sorted(agg.items(), key=lambda kv: kv[1]["receita"], reverse=True)[:n]
        return [
            {
                "produto_id": pid,
                "produto": (products.get(pid) or {}).get("name", f"#{pid}"),
                "categoria_id": (products.get(pid) or {}).get("category_id"),
                "pedidos": v["pedidos"],
                "unidades": v["unidades"],
                "receita": _f(v["receita"]),
            }
            for pid, v in ranked
        ]

    @mcp.tool(
        description=(
            "Retorna os N produtos com maior quantidade total vendida (unidades), "
            "opcionalmente restringindo a um intervalo de datas e/ou a uma região."
        )
    )
    async def top_produtos_por_quantidade(
        n: int = 10,
        data_de: str | None = None,
        data_ate: str | None = None,
        regiao_id: int | None = None,
    ) -> list[dict[str, Any]]:
        client = get_client()
        orders = await client.all_sales_orders(
            date_from=data_de, date_to=data_ate, region_id=regiao_id
        )
        products = {p["id"]: p for p in await client.paginate("/products")}

        agg: dict[int, dict[str, Any]] = defaultdict(
            lambda: {"unidades": 0, "receita": Decimal("0"), "pedidos": 0}
        )
        for o in orders:
            a = agg[o["product_id"]]
            a["unidades"] += int(o["units_sold"])
            a["receita"] += _to_decimal(o["total_revenue"])
            a["pedidos"] += 1

        ranked = sorted(agg.items(), key=lambda kv: kv[1]["unidades"], reverse=True)[:n]
        return [
            {
                "produto_id": pid,
                "produto": (products.get(pid) or {}).get("name", f"#{pid}"),
                "categoria_id": (products.get(pid) or {}).get("category_id"),
                "pedidos": v["pedidos"],
                "unidades": v["unidades"],
                "receita": _f(v["receita"]),
            }
            for pid, v in ranked
        ]

    @mcp.tool(
        description=(
            "Agrega receita e unidades por período (granularidade 'diario' ou 'mensal'), "
            "permitindo identificar tendências e sazonalidade. Filtros opcionais de data e região."
        )
    )
    async def vendas_por_periodo(
        granularidade: str = "mensal",
        data_de: str | None = None,
        data_ate: str | None = None,
        regiao_id: int | None = None,
    ) -> list[dict[str, Any]]:
        if granularidade not in ("diario", "mensal"):
            raise ValueError("granularidade deve ser 'diario' ou 'mensal'")
        client = get_client()
        orders = await client.all_sales_orders(
            date_from=data_de, date_to=data_ate, region_id=regiao_id
        )

        agg: dict[str, dict[str, Any]] = defaultdict(
            lambda: {"pedidos": 0, "unidades": 0, "receita": Decimal("0")}
        )
        for o in orders:
            data = str(o["date"])  # "YYYY-MM-DD"
            chave = data if granularidade == "diario" else data[:7]  # YYYY-MM
            a = agg[chave]
            a["pedidos"] += 1
            a["unidades"] += int(o["units_sold"])
            a["receita"] += _to_decimal(o["total_revenue"])

        return [
            {
                "periodo": k,
                "pedidos": v["pedidos"],
                "unidades": v["unidades"],
                "receita": _f(v["receita"]),
            }
            for k, v in sorted(agg.items())
        ]

    @mcp.tool(
        description=(
            "Calcula a distribuição de pedidos e receita por método de pagamento, "
            "opcionalmente restringindo a um intervalo de datas e/ou a uma região."
        )
    )
    async def distribuicao_metodos_pagamento(
        data_de: str | None = None,
        data_ate: str | None = None,
        regiao_id: int | None = None,
    ) -> list[dict[str, Any]]:
        client = get_client()
        orders = await client.all_sales_orders(
            date_from=data_de, date_to=data_ate, region_id=regiao_id
        )
        methods = {m["id"]: m["name"] for m in await client.list_payment_methods(limit=1000)}

        agg: dict[int, dict[str, Any]] = defaultdict(
            lambda: {"pedidos": 0, "receita": Decimal("0")}
        )
        for o in orders:
            a = agg[o["payment_method_id"]]
            a["pedidos"] += 1
            a["receita"] += _to_decimal(o["total_revenue"])

        total_pedidos = sum(v["pedidos"] for v in agg.values()) or 1
        total_receita = sum((v["receita"] for v in agg.values()), Decimal("0")) or Decimal("1")

        return sorted(
            [
                {
                    "metodo_pagamento_id": mid,
                    "metodo_pagamento": methods.get(mid, f"#{mid}"),
                    "pedidos": v["pedidos"],
                    "receita": _f(v["receita"]),
                    "percentual_pedidos": round(v["pedidos"] / total_pedidos * 100, 2),
                    "percentual_receita": round(_f(v["receita"] / total_receita) * 100, 2),
                }
                for mid, v in agg.items()
            ],
            key=lambda x: x["receita"],
            reverse=True,
        )

    @mcp.tool(
        description=(
            "Calcula o ticket médio (receita média por pedido) com filtros opcionais "
            "de intervalo de datas, região e categoria."
        )
    )
    async def ticket_medio(
        data_de: str | None = None,
        data_ate: str | None = None,
        regiao_id: int | None = None,
        categoria_id: int | None = None,
    ) -> dict[str, Any]:
        client = get_client()
        orders = await client.all_sales_orders(
            date_from=data_de, date_to=data_ate, region_id=regiao_id
        )
        if categoria_id is not None:
            products = {p["id"]: p for p in await client.paginate("/products")}
            orders = [
                o
                for o in orders
                if (products.get(o["product_id"]) or {}).get("category_id") == categoria_id
            ]

        n = len(orders)
        receita = sum((_to_decimal(o["total_revenue"]) for o in orders), Decimal("0"))
        unidades = sum(int(o["units_sold"]) for o in orders)
        ticket = (receita / n) if n else Decimal("0")
        receita_por_unidade = (receita / unidades) if unidades else Decimal("0")
        return {
            "pedidos": n,
            "unidades": unidades,
            "receita_total": _f(receita),
            "ticket_medio": _f(ticket),
            "receita_media_por_unidade": _f(receita_por_unidade),
        }
