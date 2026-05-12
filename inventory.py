"""Inventory management system"""

from typing import Dict, Optional

from pydantic import BaseModel, Field


class SKUInventory(BaseModel):
    """SKU inventory record"""

    sku: str
    store_id: str
    quantity_on_hand: int = Field(ge=0)
    reorder_point: int = Field(gt=0)
    reorder_qty: int = Field(gt=0)
    unit_cost: float = Field(gt=0)
    last_updated: str


class InventoryManager:
    """Manage inventory operations"""

    def __init__(self):
        # In-memory store for demo
        self.inventory: Dict[str, SKUInventory] = {}

    def adjust_stock(self, store_id: str, sku: str, quantity_delta: int) -> Dict:
        """Adjust stock quantity"""
        key = f"{store_id}:{sku}"

        if key not in self.inventory:
            return {"status": "error", "message": "SKU not found"}

        current = self.inventory[key].quantity_on_hand
        new_qty = current + quantity_delta

        if new_qty < 0:
            return {"status": "error", "message": "Insufficient stock"}

        self.inventory[key].quantity_on_hand = new_qty

        # Check if reorder needed
        needs_reorder = new_qty <= self.inventory[key].reorder_point

        return {
            "status": "success",
            "previous_qty": current,
            "new_qty": new_qty,
            "needs_reorder": needs_reorder,
        }

    def get_low_stock_items(self, store_id: str) -> list:
        """Get items below reorder point"""
        low_stock = []

        for key, item in self.inventory.items():
            if key.startswith(f"{store_id}:"):
                if item.quantity_on_hand <= item.reorder_point:
                    low_stock.append(
                        {
                            "sku": item.sku,
                            "current_qty": item.quantity_on_hand,
                            "reorder_qty": item.reorder_qty,
                        }
                    )

        return low_stock

    def calculate_stock_value(self, store_id: str) -> float:
        """Calculate total inventory value for store"""
        total_value = 0.0

        for key, item in self.inventory.items():
            if key.startswith(f"{store_id}:"):
                total_value += item.quantity_on_hand * item.unit_cost

        return round(total_value, 2)
