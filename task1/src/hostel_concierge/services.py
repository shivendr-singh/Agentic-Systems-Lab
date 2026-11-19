"""Deterministic booking and kitchen rules used by the specialist agents."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from hostel_concierge.data import get_guest, get_kitchen_info


class BookingActionError(ValueError):
    """Raised when a requested booking action does not fit the booking."""


class KitchenClosedError(ValueError):
    """Raised when an order is requested while the kitchen is closed."""


class OrderRequestError(ValueError):
    """Raised when an order request is missing or contains invalid items."""


class OutOfStockError(OrderRequestError):
    """Raised when the requested quantity exceeds the available stock."""


def prepare_booking_action(
    guest_id: str,
    action: str,
    today: date | None = None,
) -> dict[str, Any]:
    guest = get_guest(guest_id)
    current_date = today or date.today()

    if action == "check-in":
        if guest["status"] != "booked":
            raise BookingActionError("Check-in is only available for a booked guest.")
        if current_date < date.fromisoformat(guest["check_in_date"]):
            raise BookingActionError("The guest's check-in date has not arrived yet.")
        proposed_status = "checked-in"
    elif action == "check-out":
        if guest["status"] != "checked-in":
            raise BookingActionError("Check-out is only available for a checked-in guest.")
        proposed_status = "checked-out"
    else:
        raise BookingActionError("Action must be 'check-in' or 'check-out'.")

    return {
        "guest_id": guest["guest_id"],
        "room": guest["room"],
        "action": action,
        "proposed_status": proposed_status,
        "approval_required": True,
    }


def prepare_order(
    guest_id: str,
    requested_items: list[dict[str, Any]],
    now: datetime | None = None,
) -> dict[str, Any]:
    guest = get_guest(guest_id)
    if not requested_items:
        raise OrderRequestError("At least one menu item is required.")

    kitchen = get_kitchen_info(now)
    if not kitchen["is_open"]:
        raise KitchenClosedError("The kitchen is currently closed.")

    menu_by_id = {item["id"]: item for item in kitchen["menu"]}
    quantities: dict[str, int] = {}
    for request in requested_items:
        item_id = request.get("item_id")
        quantity = request.get("quantity")
        if item_id not in menu_by_id:
            raise OrderRequestError(f"Unknown menu item: {item_id!r}.")
        if type(quantity) is not int or quantity < 1:
            raise OrderRequestError("Each item quantity must be a positive whole number.")
        quantities[item_id] = quantities.get(item_id, 0) + quantity

    order_items = []
    total = Decimal("0")
    for item_id, quantity in quantities.items():
        menu_item = menu_by_id[item_id]
        if quantity > menu_item["stock"]:
            raise OutOfStockError(
                f"{menu_item['name']} has only {menu_item['stock']} available."
            )
        line_total = Decimal(str(menu_item["price"])) * quantity
        total += line_total
        order_items.append(
            {
                "item_id": item_id,
                "name": menu_item["name"],
                "quantity": quantity,
                "unit_price": menu_item["price"],
                "line_total": float(line_total),
            }
        )

    return {
        "guest_id": guest["guest_id"],
        "room": guest["room"],
        "items": order_items,
        "total": float(total),
        "approval_required": True,
    }