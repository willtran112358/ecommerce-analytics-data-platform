from datetime import datetime

from transaction import LineItem, Transaction, TransactionProcessor


def test_transaction_total():
    txn = Transaction(
        transaction_id="TXN_1",
        store_id="WINMART_HCM_001",
        register_id="REG_01",
        timestamp=datetime(2024, 5, 13, 10, 30),
        items=[LineItem(sku="WM_RICE_01", quantity=2, unit_price=89.99)],
        payment_method="cash",
    )
    assert txn.total_amount > txn.subtotal
    result = TransactionProcessor.process_transaction(txn)
    assert result["status"] == "success"
