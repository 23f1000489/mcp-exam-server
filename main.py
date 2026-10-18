
import hashlib
import os
import re
from contextvars import ContextVar

import uvicorn
from mcp.server.fastmcp import FastMCP

EMAIL = "23f1000489@ds.study.iitm.ac.in"

request_challenge = ContextVar("request_challenge", default=None)

mcp = FastMCP(
    "Exam Challenge Server",
    transport_security={
        "enable_dns_rebinding_protection": False
    }
)


class ChallengeHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {
            key.decode("latin-1").lower():
            value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }

        token = request_challenge.set(
            headers.get("x-exam-challenge")
        )

        try:
            await self.app(scope, receive, send)
        finally:
            request_challenge.reset(token)


@mcp.tool()
async def solve_challenge() -> str:
    """Return the hash for the HTTP challenge header."""
    challenge = request_challenge.get()

    if not challenge or not re.fullmatch(r"[0-9a-f]{32}", challenge):
        raise ValueError("Invalid or missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL.strip().lower()}"

    return hashlib.sha256(
        message.encode("utf-8")
    ).hexdigest()[:16]


app = ChallengeHeaderMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "8000"))
    )
