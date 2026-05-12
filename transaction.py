"""POS transaction processing and validation"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class LineItem(BaseModel):
    """Transaction line item"""

    sku: str
    quantity: int = Field(gt=0)
    unit_price: float = Field(gt=0)
    discount: float = Field(default=0, ge=0)

    @property
    def subtotal(self) -> float:
        return (self.quantity * self.unit_price) - self.discount


class Transaction(BaseModel):
    """POS transaction"""

    transaction_id: str
    store_id: str
    register_id: str
    timestamp: datetime
    items: List[LineItem] = Field(min_items=1)
    payment_method: str  # cash, card, mobile
    customer_id: Optional[str] = None
    total: Optional[float] = None

    @field_validator("transaction_id", "store_id", "register_id")
    def validate_ids(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("ID cannot be empty")
        return v.strip()

    @property
    def subtotal(self) -> float:
        return sum(item.subtotal for item in self.items)

    @property
    def tax(self) -> float:
        return round(self.subtotal * 0.1, 2)  # 10% tax

    @property
    def total_amount(self) -> float:
        return self.subtotal + self.tax


class TransactionProcessor:
    """Process and validate transactions"""

    @staticmethod
    def validate_transaction(transaction: Transaction) -> Dict:
        """Validate transaction data"""
        errors = []

        if not transaction.items:
            errors.append("Transaction must have at least one item")

        if transaction.total and abs(transaction.total - transaction.total_amount) > 0.01:
            errors.append("Total amount mismatch")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "calculated_total": transaction.total_amount,
        }

    @staticmethod
    def process_transaction(transaction: Transaction) -> Dict:
        """Process transaction and return result"""
        validation = TransactionProcessor.validate_transaction(transaction)

        if not validation["valid"]:
            return {"status": "failed", "errors": validation["errors"]}

        return {
            "status": "success",
            "transaction_id": transaction.transaction_id,
            "total": transaction.total_amount,
            "items_count": len(transaction.items),
            "timestamp": transaction.timestamp.isoformat(),
        }
