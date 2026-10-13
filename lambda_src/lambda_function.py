import json

VALID_STATUSES = {"NEW", "PAID", "SHIPPED", "CANCELLED"}


def validate_order(order):
    errors = []
    required_fields = ["order_id", "customer_id", "amount", "status"]

    for field in required_fields:
        if field not in order or order[field] in (None, ""):
            errors.append(f"{field} is required")

    amount = None
    if "amount" in order and order["amount"] not in (None, ""):
        try:
            amount = float(order["amount"])
            if amount <= 0:
                errors.append("amount must be greater than zero")
        except (TypeError, ValueError):
            errors.append("amount must be numeric")

    status = str(order.get("status", "")).strip().upper()
    if status and status not in VALID_STATUSES:
        errors.append(f"invalid status: {status}")

    normalized_order = dict(order)
    if amount is not None:
        normalized_order["amount"] = amount
    if status:
        normalized_order["status"] = status

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "order": normalized_order,
    }


def lambda_handler(event, context):
    order = event.get("order", event)
    result = validate_order(order)

    return {
        "statusCode": 200 if result["valid"] else 400,
        "pipeline_version": "v1",
        "body": json.dumps(result),
    }
