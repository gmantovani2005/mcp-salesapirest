"""Cliente HTTP assíncrono para a Sales Dataset API REST."""
from __future__ import annotations

from typing import Any

import httpx

from server.config import settings


class SalesAPIClient:
    """Wrapper fino sobre httpx.AsyncClient para a Sales Dataset API."""

    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self._client = httpx.AsyncClient(
            base_url=(base_url or settings.sales_api_base_url).rstrip("/"),
            timeout=timeout if timeout is not None else settings.sales_api_timeout,
            headers={"Accept": "application/json"},
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "SalesAPIClient":
        return self

    async def __aexit__(self, *_exc: object) -> None:
        await self.aclose()

    # ---------- helpers -----------------------------------------------------

    @staticmethod
    def _clean(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None}

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        resp = await self._client.get(path, params=self._clean(params or {}))
        resp.raise_for_status()
        return resp.json()

    async def paginate(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        page_size: int = 1000,
        max_pages: int = 100,
    ) -> list[dict[str, Any]]:
        """Itera todas as páginas de um endpoint de lista (limit/skip)."""
        items: list[dict[str, Any]] = []
        skip = 0
        params = dict(params or {})
        for _ in range(max_pages):
            page = await self._get(
                path,
                params={**params, "skip": skip, "limit": page_size},
            )
            if not isinstance(page, list) or not page:
                break
            items.extend(page)
            if len(page) < page_size:
                break
            skip += page_size
        return items

    # ---------- health ------------------------------------------------------

    async def health(self) -> Any:
        return await self._get("/health")

    # ---------- categories --------------------------------------------------

    async def list_categories(
        self, name: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        return await self._get(
            "/categories", {"name": name, "skip": skip, "limit": limit}
        )

    async def get_category(self, category_id: int) -> dict[str, Any]:
        return await self._get(f"/categories/{category_id}")

    # ---------- regions -----------------------------------------------------

    async def list_regions(
        self, name: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        return await self._get(
            "/regions", {"name": name, "skip": skip, "limit": limit}
        )

    async def get_region(self, region_id: int) -> dict[str, Any]:
        return await self._get(f"/regions/{region_id}")

    # ---------- payment methods --------------------------------------------

    async def list_payment_methods(
        self, name: str | None = None, skip: int = 0, limit: int = 100
    ) -> list[dict[str, Any]]:
        return await self._get(
            "/payment-methods", {"name": name, "skip": skip, "limit": limit}
        )

    async def get_payment_method(self, payment_method_id: int) -> dict[str, Any]:
        return await self._get(f"/payment-methods/{payment_method_id}")

    # ---------- products ----------------------------------------------------

    async def list_products(
        self,
        name: str | None = None,
        category_id: int | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await self._get(
            "/products",
            {
                "name": name,
                "category_id": category_id,
                "min_price": min_price,
                "max_price": max_price,
                "skip": skip,
                "limit": limit,
            },
        )

    async def get_product(self, product_id: int) -> dict[str, Any]:
        return await self._get(f"/products/{product_id}")

    # ---------- sales orders ------------------------------------------------

    async def list_sales_orders(
        self,
        product_id: int | None = None,
        region_id: int | None = None,
        payment_method_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        min_total: float | None = None,
        max_total: float | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        return await self._get(
            "/sales-orders",
            {
                "product_id": product_id,
                "region_id": region_id,
                "payment_method_id": payment_method_id,
                "date_from": date_from,
                "date_to": date_to,
                "min_total": min_total,
                "max_total": max_total,
                "skip": skip,
                "limit": limit,
            },
        )

    async def get_sales_order(self, sales_order_id: int) -> dict[str, Any]:
        return await self._get(f"/sales-orders/{sales_order_id}")

    async def all_sales_orders(
        self,
        product_id: int | None = None,
        region_id: int | None = None,
        payment_method_id: int | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> list[dict[str, Any]]:
        """Conveniência: itera todas as páginas com os filtros informados."""
        return await self.paginate(
            "/sales-orders",
            {
                "product_id": product_id,
                "region_id": region_id,
                "payment_method_id": payment_method_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )


_client: SalesAPIClient | None = None


def get_client() -> SalesAPIClient:
    """Retorna um cliente singleton lazy (criado no primeiro uso)."""
    global _client
    if _client is None:
        _client = SalesAPIClient()
    return _client


async def close_client() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
