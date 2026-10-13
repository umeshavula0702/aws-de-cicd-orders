from lambda_src.lambda_function import validate_order


def test_valid_order():
    order = {
        "order_id": "1001",
        "customer_id": "C001",
        "amount": "1200.50",
        "status": "paid",
    }
    result = validate_order(order)
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["order"]["status"] == "PAID"
    assert result["order"]["amount"] == 1200.50


def test_negative_amount():
    order = {
        "order_id": "1002",
        "customer_id": "C002",
        "amount": "-100",
        "status": "paid",
    }
    result = validate_order(order)
    assert result["valid"] is False
    assert "amount must be greater than zero" in result["errors"]


def test_invalid_status():
    order = {
        "order_id": "1003",
        "customer_id": "C003",
        "amount": "500",
        "status": "UNKNOWN",
    }
    result = validate_order(order)
    assert result["valid"] is False
    assert "invalid status: UNKNOWN" in result["errors"]


def test_missing_customer():
    order = {
        "order_id": "1004",
        "amount": "100",
        "status": "PAID",
    }
    result = validate_order(order)
    assert result["valid"] is False
    assert "customer_id is required" in result["errors"]
