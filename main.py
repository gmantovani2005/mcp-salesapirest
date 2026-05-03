"""Entrypoint do servidor MCP Sales Dataset.

- Em desenvolvimento: `uv run mcp dev main.py` abre o MCP Inspector via stdio.
- Em container: definir `MCP_TRANSPORT=sse` para servir via HTTP/SSE.
"""
from __future__ import annotations

from server import mcp
from server.config import settings


def main() -> None:
    transport = settings.mcp_transport.lower()
    if transport == "sse":
        mcp.run(transport="sse")
    elif transport == "stdio":
        mcp.run()
    else:
        raise SystemExit(
            f"MCP_TRANSPORT desconhecido: {settings.mcp_transport!r} "
            "(use 'stdio' ou 'sse')."
        )


if __name__ == "__main__":
    main()
