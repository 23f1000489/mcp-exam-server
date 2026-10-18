
import hashlib
from contextvars import ContextVar

import uvicorn
from mcp.server.fastmcp import FastMCP

EMAIL = "23f1000489@ds.study.iitm.ac.in"

# Holds the challenge for the current HTTP request.
request_challenge = ContextVar("request_challenge", default=None)

mcp = FastMCP("Exam Challenge Server")


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

        challenge = headers.get("x-exam-challenge")
        token = request_challenge.set(challenge)

        try:
            await self.app(scope, receive, send)
        finally:
            request_challenge.reset(token)


@mcp.tool()
def solve_challenge() -> str:
    """Solve the challenge supplied in the HTTP request header."""
    challenge = request_challenge.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    normalized_email = EMAIL.strip().lower()
    message = f"{challenge}:{normalized_email}"

    return hashlib.sha256(message.encode("utf-8")).hexdigest()[:16]


# The MCP SDK handles initialization, tool listing,
# JSON-RPC requests, and tool-call responses.
app = ChallengeHeaderMiddleware(mcp.streamable_http_app())


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
