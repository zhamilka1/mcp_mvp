
from typing import Any
import os
import httpx
import uvicorn
import jwt
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# Initialize FastMCP server for Weather tools.
# If json_response is set to True, the server will use JSON responses instead of SSE streams
# If stateless_http is set to True, the server uses true stateless mode (new transport per request)
mcp = FastMCP(name="RKO", json_response=True, stateless_http=False)

@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get party restrictions

    Args:
        request: Two-letter US state code (e.g. CA, NY),
        role: JWT token
    """

    pass


@mcp.tool()
async def get_forecast(latitude: float, longitude: float) -> str:
    """Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
    """
    # First get the forecast grid endpoint
    pass


if __name__ == "__main__":
    uvicorn.run(mcp.streamable_http_app, host="localhost", port="8123")
