"""MCP Streamable HTTP Client"""
import os
import jwt
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
import datetime
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from dotenv import load_dotenv


load_dotenv()

class MCPClient:
    """MCP Client for interacting with an MCP Streamable HTTP server"""

    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

    async def connect_to_streamable_http_server(
        self, server_url: str, headers: Optional[dict] = None
    ):
        """Connect to an MCP server running with HTTP Streamable transport"""
        self._streams_context = streamablehttp_client(  # pylint: disable=W0201
            url=server_url,
            headers=headers or {},
        )
        read_stream, write_stream, _ = await self._streams_context.__aenter__()  # pylint: disable=E1101

        self._session_context = ClientSession(read_stream, write_stream)  # pylint: disable=W0201
        self.session: ClientSession = await self._session_context.__aenter__()  # pylint: disable=C2801

        await self.session.initialize()

    async def process_query(self, query: str):


        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

        print(available_tools)
        print(await self.session.call_tool('get_alerts',{'state':'ohaio'}))

    async def cleanup(self):
        """Properly clean up the session and streams"""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:  # pylint: disable=W0125
            await self._streams_context.__aexit__(None, None, None)  # pylint: disable=E1101

async def main():
    """Main function to run the MCP client"""
    client = MCPClient()
    payload = {
        'user_id': 123,
        'username': 'john_doe',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)  # Срок действия токена
    }
    try:
        await client.connect_to_streamable_http_server(
            os.getenv("MCP_HOST")+os.getenv("MCP_PORT")+os.getenv("MCP_PATH")
        )
        await client.process_query("lol")

    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())








# Создание JWT
token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

print("Созданный токен:", token)