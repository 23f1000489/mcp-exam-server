import crypto from "crypto";

const url = "http://localhost:3000/mcp";
const challenge = crypto.randomBytes(16).toString("hex");

const response = await fetch(url, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
    "X-Exam-Challenge": challenge,
    "X-Exam-Timestamp": Date.now().toString(),
    "X-Exam-Signature": "not-checked"
  },
  body: JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "tools/call",
    params: {
      name: "solve_challenge",
      arguments: {}
    }
  })
});

console.log("Challenge:", challenge);
console.log(await response.text());