"""MCP client restricted to one specialist's tools and guest context."""

from types import TracebackType
from typing import Any

from mcp import Client
from mcp.types import TextContent

from hostel_concierge.mcp.client_policy import (
    GuestContext,
    ToolPolicyError,
    bind_guest_context,
    expose_tools,
)


class SpecialistToolError(RuntimeError):
    """Raised when an MCP tool returns an error result."""


class SpecialistMCPClient:
    def __init__(self, specialist: str, context: GuestContext, server: Any) -> None:
        self._specialist = specialist
        self._context = context
        self._client = Client(server)
        self._visible_tools: list[dict[str, Any]] = []

    async def __aenter__(self) -> "SpecialistMCPClient":
        await self._client.__aenter__()
        listed_tools = await self._client.list_tools()
        self._visible_tools = expose_tools(self._specialist, listed_tools.tools)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool | None:
        return await self._client.__aexit__(exc_type, exc, traceback)

    @property
    def tools(self) -> list[dict[str, Any]]:
        return list(self._visible_tools)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        if not self._visible_tools:
            raise RuntimeError("The specialist MCP client is not connected.")
        mcp_arguments = bind_guest_context(
            self._specialist,
            name,
            arguments,
            self._context,
        )
        result = await self._client.call_tool(name, mcp_arguments)
        if result.is_error:
            message = " ".join(
                block.text for block in result.content if isinstance(block, TextContent)
            )
            raise SpecialistToolError(message or f"MCP tool {name!r} failed.")
        if result.structured_content is not None:
            return result.structured_content
        return result.content


__all__ = ["SpecialistMCPClient", "SpecialistToolError", "ToolPolicyError"]