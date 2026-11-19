"""Tool allow-lists and trusted guest-context binding for specialist clients."""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any


SPECIALIST_TOOL_ALLOWLISTS = {
    "booking": frozenset({"booking_get_own_booking", "booking_propose_action"}),
    "kitchen": frozenset({"kitchen_get_info", "kitchen_propose_order"}),
}


@dataclass(frozen=True)
class GuestContext:
    guest_id: str
    room: str


class ToolPolicyError(ValueError):
    """Raised when a specialist attempts to access a disallowed tool or context."""


def expose_tools(specialist: str, tools: list[Any]) -> list[dict[str, Any]]:
    allowed = SPECIALIST_TOOL_ALLOWLISTS[specialist]
    visible_tools = []
    for tool in tools:
        if tool.name not in allowed:
            continue
        schema = deepcopy(tool.input_schema)
        properties = schema.get("properties", {})
        properties.pop("guest_id", None)
        properties.pop("room", None)
        schema["required"] = [
            field for field in schema.get("required", []) if field not in {"guest_id", "room"}
        ]
        visible_tools.append(
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": schema,
            }
        )
    return visible_tools


def bind_guest_context(
    specialist: str,
    tool_name: str,
    arguments: dict[str, Any],
    context: GuestContext,
) -> dict[str, Any]:
    if tool_name not in SPECIALIST_TOOL_ALLOWLISTS[specialist]:
        raise ToolPolicyError(f"{specialist} specialist cannot use tool {tool_name!r}.")
    if "guest_id" in arguments or "room" in arguments:
        raise ToolPolicyError("Guest identity and room must come from app context.")
    return {**arguments, "guest_id": context.guest_id, "room": context.room}