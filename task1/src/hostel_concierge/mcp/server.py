"""MCP server exposing the Booking and Kitchen specialist tools."""

from datetime import datetime
from typing import Any

from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import BaseModel

from hostel_concierge.data import GuestNotFoundError, get_guest, get_kitchen_info
from hostel_concierge.services import (
    BookingActionError,
    KitchenClosedError,
    OrderRequestError,
    prepare_booking_action,
    prepare_order,
)


class OrderLine(BaseModel):
    item_id: str
    quantity: int


mcp = MCPServer("sunrise-hostel")


def _validate_guest_context(guest_id: str, room: str) -> dict[str, Any]:
    try:
        guest = get_guest(guest_id)
    except GuestNotFoundError as error:
        raise ToolError(str(error)) from error
    if guest["room"] != room:
        raise ToolError("The supplied guest context does not match the booking.")
    return guest


@mcp.tool()
def booking_get_own_booking(guest_id: str, room: str) -> dict[str, Any]:
    """Show the booking associated with the app-provided guest context."""
    guest = _validate_guest_context(guest_id, room)
    return {
        key: guest[key]
        for key in ("guest_id", "name", "room", "check_in_date", "checkout_date", "status")
    }


@mcp.tool()
def booking_propose_action(guest_id: str, room: str, action: str) -> dict[str, Any]:
    """Prepare a check-in or check-out proposal; approval is required before execution."""
    _validate_guest_context(guest_id, room)
    try:
        return prepare_booking_action(guest_id, action)
    except BookingActionError as error:
        raise ToolError(str(error)) from error


@mcp.tool()
def kitchen_get_info(guest_id: str, room: str) -> dict[str, Any]:
    """Show current kitchen hours, open status, menu, stock, and allergens."""
    _validate_guest_context(guest_id, room)
    return get_kitchen_info()


@mcp.tool()
def kitchen_propose_order(
    guest_id: str,
    room: str,
    items: list[OrderLine],
) -> dict[str, Any]:
    """Prepare an order for the app-provided room; approval is required before execution."""
    _validate_guest_context(guest_id, room)
    try:
        return prepare_order(
            guest_id,
            [item.model_dump() for item in items],
            datetime.now(),
        )
    except (KitchenClosedError, OrderRequestError) as error:
        raise ToolError(str(error)) from error


if __name__ == "__main__":
    mcp.run()