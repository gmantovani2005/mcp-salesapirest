"""Prompts MCP em Português do Brasil."""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP


def register(mcp: FastMCP) -> None:
    """Registra todos os prompts no servidor MCP."""

    @mcp.prompt(
        name="analise_geral_de_vendas",
        description="Solicita uma análise abrangente de KPIs de vendas em um período opcional.",
    )
    def analise_geral_de_vendas(periodo: str | None = None) -> str:
        janela = (
            f" no período {periodo}"
            if periodo
            else " no período mais recente disponível"
        )
        return (
            "Você é um analista de vendas. Use as tools deste servidor MCP para "
            f"produzir uma análise abrangente das vendas{janela}.\n\n"
            "Inclua, no mínimo:\n"
            "1. Receita total, número de pedidos e ticket médio (`ticket_medio`).\n"
            "2. Top 5 produtos por receita (`top_produtos_por_receita`) e por "
            "quantidade (`top_produtos_por_quantidade`).\n"
            "3. Distribuição de receita por região (`total_vendas_por_regiao`) "
            "e por categoria (`total_vendas_por_categoria`).\n"
            "4. Distribuição dos métodos de pagamento "
            "(`distribuicao_metodos_pagamento`).\n"
            "5. Tendência mensal de receita (`vendas_por_periodo` com "
            "granularidade `mensal`).\n\n"
            "Apresente os resultados em Português do Brasil, com tabelas markdown "
            "e uma conclusão executiva destacando insights acionáveis."
        )

    @mcp.prompt(
        name="comparar_regioes",
        description="Compara o desempenho de vendas entre duas regiões.",
    )
    def comparar_regioes(
        regiao_a: str,
        regiao_b: str,
        periodo: str | None = None,
    ) -> str:
        janela = f" no período {periodo}" if periodo else ""
        return (
            f"Compare o desempenho de vendas entre as regiões '{regiao_a}' e "
            f"'{regiao_b}'{janela}.\n\n"
            "Passos sugeridos:\n"
            "1. Use `listar_regioes` para descobrir os IDs das regiões "
            "informadas (procure por nome).\n"
            "2. Para cada região, calcule receita, pedidos e ticket médio "
            "(`total_vendas_por_regiao`, `ticket_medio`).\n"
            "3. Liste os 5 produtos top em cada região "
            "(`top_produtos_por_receita`).\n"
            "4. Verifique se há diferenças marcantes nos métodos de pagamento "
            "(`distribuicao_metodos_pagamento` por região).\n\n"
            "Conclua com 2 a 3 hipóteses (em PT-BR) que expliquem as diferenças."
        )

    @mcp.prompt(
        name="identificar_tendencias",
        description="Identifica tendências e sazonalidade nas vendas.",
    )
    def identificar_tendencias(granularidade: str = "mensal") -> str:
        return (
            f"Use `vendas_por_periodo` com granularidade `{granularidade}` para "
            "obter a série temporal de receita e unidades.\n\n"
            "Em seguida:\n"
            "1. Identifique picos, vales e possíveis padrões sazonais.\n"
            "2. Calcule a taxa de crescimento entre o primeiro e o último período.\n"
            "3. Cruze com `total_vendas_por_categoria` para apontar quais "
            "categorias mais influenciam a tendência.\n"
            "4. Apresente a análise em Português do Brasil, com gráficos em "
            "markdown (tabelas) e conclusões objetivas."
        )

    @mcp.prompt(
        name="recomendacoes_de_marketing",
        description="Sugere ações de marketing baseadas nos dados de vendas.",
    )
    def recomendacoes_de_marketing(
        categoria: str | None = None,
        regiao: str | None = None,
    ) -> str:
        escopo: list[str] = []
        if categoria:
            escopo.append(f"a categoria '{categoria}'")
        if regiao:
            escopo.append(f"a região '{regiao}'")
        alvo = " e ".join(escopo) if escopo else "todo o catálogo"
        return (
            "Você é um estrategista de marketing. Com base nos dados da Sales "
            f"API, gere recomendações acionáveis para {alvo}.\n\n"
            "Roteiro:\n"
            "1. Identifique os produtos mais e menos vendidos no escopo.\n"
            "2. Avalie o ticket médio e compare com o restante do catálogo.\n"
            "3. Veja a distribuição de métodos de pagamento (sugere parcerias?).\n"
            "4. Proponha 3 a 5 ações de marketing concretas em PT-BR, "
            "classificadas por impacto esperado (alto/médio/baixo) e por "
            "esforço de execução."
        )
