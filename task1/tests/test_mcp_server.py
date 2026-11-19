import asyncio
import unittest

from mcp import Client

from hostel_concierge.mcp.client_policy import GuestContext, ToolPolicyError
from hostel_concierge.mcp.server import mcp
from hostel_concierge.mcp.specialist_client import SpecialistMCPClient


class MCPServerTests(unittest.TestCase):
    def test_server_registers_tools_and_checks_guest_context(self) -> None:
        async def exercise_server() -> None:
            async with Client(mcp, raise_exceptions=True) as client:
                listed = await client.list_tools()
                tool_names = {tool.name for tool in listed.tools}
                self.assertEqual(
                    tool_names,
                    {
                        "booking_get_own_booking",
                        "booking_propose_action",
                        "kitchen_get_info",
                        "kitchen_propose_order",
                    },
                )

                booking = await client.call_tool(
                    "booking_get_own_booking",
                    {"guest_id": "guest-305", "room": "305"},
                )
                self.assertFalse(booking.is_error)
                self.assertIn("305", str(booking.structured_content or booking.content))

                mismatched_context = await client.call_tool(
                    "booking_get_own_booking",
                    {"guest_id": "guest-305", "room": "204"},
                )
                self.assertTrue(mismatched_context.is_error)

        asyncio.run(exercise_server())

    def test_specialist_clients_expose_only_their_tools_and_bind_context(self) -> None:
        async def exercise_clients() -> None:
            context = GuestContext(guest_id="guest-305", room="305")
            async with SpecialistMCPClient("booking", context, mcp) as booking:
                booking_names = {tool["name"] for tool in booking.tools}
                self.assertEqual(
                    booking_names,
                    {"booking_get_own_booking", "booking_propose_action"},
                )
                self.assertNotIn("guest_id", booking.tools[0]["input_schema"]["properties"])
                result = await booking.call_tool("booking_get_own_booking", {})
                self.assertEqual(result["room"], "305")
                with self.assertRaises(ToolPolicyError):
                    await booking.call_tool("kitchen_get_info", {})

            async with SpecialistMCPClient("kitchen", context, mcp) as kitchen:
                kitchen_names = {tool["name"] for tool in kitchen.tools}
                self.assertEqual(
                    kitchen_names,
                    {"kitchen_get_info", "kitchen_propose_order"},
                )
                self.assertNotIn("booking_get_own_booking", kitchen_names)

        asyncio.run(exercise_clients())


if __name__ == "__main__":
    unittest.main()