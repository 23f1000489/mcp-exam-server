import express from "express";
import crypto from "crypto";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

const EMAIL = "23f1000489@ds.study.iitm.ac.in";

const app = express();
app.use(express.json());

const mcpServer = new McpServer({
  name: "exam-mcp-server",
  version: "1.0.0",
});

mcpServer.registerTool(
  "solve_challenge",
  {
    title: "Solve Challenge",
    description: "Returns the required hash for the exam challenge.",
    inputSchema: {},
  },
  async (_args, extra) => {
    const headers = extra.requestInfo?.headers ?? {};

    const challenge = String(headers["x-exam-challenge"] ?? "").trim();

    if (!/^[0-9a-f]{32}$/.test(challenge)) {
      throw new Error("Missing or invalid X-Exam-Challenge header");
    }

    const hash = crypto
      .createHash("sha256")
      .update(`${challenge}:${EMAIL}`)
      .digest("hex");

    return {
      content: [
        {
          type: "text",
          text: hash.slice(0, 16),
        },
      ],
    };
  }
);

app.post("/mcp", async (req, res) => {
  try {
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });

    res.on("close", () => {
      transport.close();
    });

    await mcpServer.connect(transport);
    await transport.handleRequest(req, res, req.body);
  } catch (error) {
    console.error(error);
    res.status(500).json({
      jsonrpc: "2.0",
      id: null,
      error: {
        code: -32603,
        message: "Internal server error",
      },
    });
  }
});

app.get("/mcp", (req, res) => {
  res.status(405).json({
    jsonrpc: "2.0",
    id: null,
    error: {
      code: -32000,
      message: "Method not allowed",
    },
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`MCP server listening on port ${PORT}`);
});