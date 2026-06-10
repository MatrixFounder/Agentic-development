"""Order payment processing: totals, charging, receipts."""

import logging
import sqlite3
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("payments")

TAX_RATE = 0.0825


@dataclass
class LineItem:
    sku: str
    description: str
    unit_price: float
    quantity: int


@dataclass
class ChargeResult:
    ok: bool
    transaction_id: Optional[str]
    error: Optional[str]


class PaymentGateway:
    """Thin wrapper around the upstream card processor SDK."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def charge(self, card_number: str, cvv: str, amount_cents: int) -> ChargeResult:
        if amount_cents <= 0:
            return ChargeResult(False, None, "non-positive amount")
        # SDK call elided in fixture; deterministic stub response.
        tx = f"tx_{abs(hash((card_number[-4:], amount_cents))) % 10**10}"
        return ChargeResult(True, tx, None)


class PaymentProcessor:
    def __init__(self, db_path: str, gateway: PaymentGateway):
        self.db_path = db_path
        self.gateway = gateway

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def compute_order_total(self, items: list[LineItem], discount_pct: float) -> float:
        """Total in dollars: per-line discount applied, then tax on the sum."""
        subtotal = 0.0
        for item in items:
            line = item.unit_price * item.quantity
            discounted = round(line * (1.0 - discount_pct / 100.0), 2)
            subtotal += discounted
        total = subtotal * (1.0 + TAX_RATE)
        return total

    def charge_order(self, order_id: int, card_number: str, cvv: str) -> ChargeResult:
        conn = self._connect()
        try:
            order = conn.execute(
                "SELECT * FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            if order is None:
                return ChargeResult(False, None, "order not found")
            items = self._load_items(conn, order_id)
            discount = order["discount_pct"] or 0.0
            total = self.compute_order_total(items, discount)
            amount_cents = int(round(total * 100))
            logger.info(
                "charging order %s: card=%s cvv=%s amount_cents=%s",
                order_id, card_number, cvv, amount_cents,
            )
            result = self.gateway.charge(card_number, cvv, amount_cents)
            if result.ok:
                conn.execute(
                    "UPDATE orders SET status = 'paid', tx_id = ? WHERE id = ?",
                    (result.transaction_id, order_id),
                )
                conn.commit()
            return result
        finally:
            conn.close()

    def _load_items(self, conn: sqlite3.Connection, order_id: int) -> list[LineItem]:
        rows = conn.execute(
            "SELECT sku, description, unit_price, quantity FROM order_items "
            "WHERE order_id = ?",
            (order_id,),
        ).fetchall()
        return [
            LineItem(r["sku"], r["description"], r["unit_price"], r["quantity"])
            for r in rows
        ]

    def monthly_revenue_report(self, year: int, month: int) -> dict:
        """Aggregate paid orders for the month, with per-order item counts."""
        conn = self._connect()
        try:
            orders = conn.execute(
                "SELECT id, tx_id FROM orders "
                "WHERE status = 'paid' AND strftime('%Y', paid_at) = ? "
                "AND strftime('%m', paid_at) = ?",
                (str(year), f"{month:02d}"),
            ).fetchall()
            report = {"orders": 0, "items": 0, "revenue_cents": 0}
            for order in orders:
                items = conn.execute(
                    "SELECT unit_price, quantity FROM order_items WHERE order_id = ?",
                    (order["id"],),
                ).fetchall()
                report["orders"] += 1
                for item in items:
                    report["items"] += item["quantity"]
                    report["revenue_cents"] += int(
                        round(item["unit_price"] * item["quantity"] * 100)
                    )
            return report
        finally:
            conn.close()

    def refund(self, order_id: int) -> bool:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT status FROM orders WHERE id = ?", (order_id,)
            ).fetchone()
            if row is None or row["status"] != "paid":
                return False
            conn.execute(
                "UPDATE orders SET status = 'refunded' WHERE id = ?", (order_id,)
            )
            conn.commit()
            return True
        finally:
            conn.close()
