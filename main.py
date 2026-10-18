
import hashlib
import os
import re

import uvicorn
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "23f1000489@ds.study.iitm.ac.in"

mcp = FastMCP(
    "Exam Challenge Server",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False
    ),
)


@mcp.tool()
async def solve_challenge() -> str:
    """Return the hash for the HTTP challenge header."""
    from mcp.server.fastmcp import get_http_request

    request = get_http_request()
    challenge = request.headers.get("x-exam-challenge", "")

    if not re.fullmatch(r"[0-9a-f]{32}", challenge):
        raise ValueError("Invalid or missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL.strip().lower()}"
    return hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]


app = mcp.streamable_http_app()


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000")),
    )

