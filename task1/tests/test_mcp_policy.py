import unittest
from types import SimpleNamespace

from hostel_concierge.mcp.client_policy import (
    GuestContext,
    ToolPolicyError,
    bind_guest_context,
    expose_tools,
)


def make_tool(name: str) -> SimpleNamespace:
    return SimpleNamespace(
        name=name,
        description=f"Description for {name}",
        input_schema={
            "type": "object",
            "properties": {
                "guest_id": {"type": "string"},
                "room": {"type": "string"},
                "action": {"type": "string"},
            },
            "required": ["guest_id", "room", "action"],
        },
    )


class MCPPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tools = [
            make_tool("booking_get_own_booking"),
            make_tool("booking_propose_action"),
            make_tool("kitchen_get_info"),
            make_tool("kitchen_propose_order"),
        ]
        self.context = GuestContext(guest_id="guest-305", room="305")

    def test_booking_specialist_cannot_see_kitchen_tools(self) -> None:
        names = {tool["name"] for tool in expose_tools("booking", self.tools)}

        self.assertEqual(names, {"booking_get_own_booking", "booking_propose_action"})

    def test_kitchen_specialist_cannot_see_booking_tools(self) -> None:
        names = {tool["name"] for tool in expose_tools("kitchen", self.tools)}

        self.assertEqual(names, {"kitchen_get_info", "kitchen_propose_order"})

    def test_guest_context_is_hidden_and_bound_by_application(self) -> None:
        visible = expose_tools("booking", self.tools)
        schema = visible[0]["input_schema"]
        arguments = bind_guest_context("booking", visible[0]["name"], {}, self.context)

        self.assertNotIn("guest_id", schema["properties"])
        self.assertNotIn("room", schema["properties"])
        self.assertEqual(arguments, {"guest_id": "guest-305", "room": "305"})

    def test_specialist_cannot_override_guest_context(self) -> None:
        with self.assertRaises(ToolPolicyError):
            bind_guest_context(
                "kitchen",
                "kitchen_get_info",
                {"room": "204"},
                self.context,
            )


if __name__ == "__main__":
    unittest.main()