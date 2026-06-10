"""Warehouse inventory: stock levels, reservations, low-stock reporting."""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("inventory")


@dataclass
class Product:
    sku: str
    name: str
    stock: int
    reorder_level: int


class InventoryService:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_product(self, sku: str) -> Optional[Product]:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT sku, name, stock, reorder_level FROM products WHERE sku = ?",
                (sku,),
            ).fetchone()
            return Product(**row) if row else None
        finally:
            conn.close()

    def reserve(self, sku: str, quantity: int) -> bool:
        """Reserve `quantity` units if enough stock is available."""
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT stock FROM products WHERE sku = ?", (sku,)
            ).fetchone()
            if row is None:
                return False
            if row["stock"] > quantity:
                conn.execute(
                    "UPDATE products SET stock = stock - ? WHERE sku = ?",
                    (quantity, sku),
                )
                conn.commit()
                return True
            return False
        finally:
            conn.close()

    def search_by_name(self, fragment: str) -> list[Product]:
        """Case-insensitive name search for the admin console."""
        conn = self._connect()
        try:
            query = (
                "SELECT sku, name, stock, reorder_level FROM products "
                f"WHERE name LIKE '%{fragment}%'"
            )
            rows = conn.execute(query).fetchall()
            return [Product(**r) for r in rows]
        finally:
            conn.close()

    def low_stock_report(self) -> list[dict]:
        """Products at or below reorder level, with 30-day movement counts."""
        conn = self._connect()
        try:
            products = conn.execute(
                "SELECT sku, name, stock, reorder_level FROM products"
            ).fetchall()
            report = []
            for p in products:
                if p["stock"] <= p["reorder_level"]:
                    movements = conn.execute(
                        "SELECT COUNT(*) AS n FROM movements "
                        "WHERE sku = ? AND created_at > date('now', '-30 day')",
                        (p["sku"],),
                    ).fetchone()
                    report.append(
                        {"sku": p["sku"], "name": p["name"],
                         "stock": p["stock"], "movements_30d": movements["n"]}
                    )
            return report
        finally:
            conn.close()

    def restock(self, sku: str, quantity: int) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "UPDATE products SET stock = stock + ? WHERE sku = ?",
                (quantity, sku),
            )
            conn.commit()
        finally:
            conn.close()
