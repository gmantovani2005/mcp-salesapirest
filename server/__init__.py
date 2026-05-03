"""Servidor MCP para a Sales Dataset API REST.

Cria a instância FastMCP, registra prompts/resources/tools (todos com
descrições em Português do Brasil) e expõe o objeto `mcp` para o entrypoint.
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from server import prompts, resources, tools
from server.config import settings

INSTRUCOES = (
    "Servidor MCP para análise de dados de vendas a partir da Sales Dataset "
    "API REST. Todas as tools, resources e prompts estão em Português do "
    "Brasil. Comece por `sales://contexto` para entender o dataset; depois "
    "use as tools de agregação (`total_vendas_por_regiao`, "
    "`top_produtos_por_receita`, `vendas_por_periodo`, etc.) para responder "
    "perguntas analíticas. As tools `listar_*` cobrem consultas brutas com "
    "filtros e paginação."
)

mcp = FastMCP(
    name="Sales Dataset MCP",
    instructions=INSTRUCOES,
    host=settings.mcp_host,
    port=settings.mcp_port,
)

prompts.register(mcp)
resources.register(mcp)
tools.register(mcp)

__all__ = ["mcp"]
