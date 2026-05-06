from flask import Flask, request, Response
from openai import OpenAI
import os
import json

app = Flask(__name__)
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ====================== RAG KNOWLEDGE BASE ======================
KNOWLEDGE_BASE = """
Aggieland Scoots - 1600 Texas Ave S, College Station, TX 77840
Phone: (979) 446-0900 | Email: info@aggielandscoots.com
Hours: Mon–Sat 10am–6pm | Closed Sunday
Aggie Owned & Operated.

We specialize in: Mopeds, Motor Scooters, Motorcycles, eScooters, eBikes (new & pre-owned).

Popular Brands: Genuine Scooter Co, Kymco, Lance, SYM, Honda, NIU, Wolf, Buddy, Lectric, etc.

Key Benefits for Customers:
- Test rides available
- Learn-to-ride help included
- Financing options
- Delivery available
- Full service & repair shop
- Warranty service

Texas Moped Law: Under 50cc needs only regular Class C driver's license. No motorcycle endorsement needed.
"""

# ====================== TOOLS ======================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Get current inventory with prices and specs",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture a qualified lead",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "interest": {"type": "string"},
                    "recommended_model": {"type": "string"},
                    "notes": {"type": "string"}
                },
                "required": ["name", "email", "phone"]
            }
        }
    }
]

SYSTEM_PROMPT = """You are the official Aggieland Scoots AI Sales Agent.
Use the knowledge base below to answer accurately.

KNOWLEDGE BASE:
""" + KNOWLEDGE_BASE + """

Be friendly, helpful, Aggie-proud, and never pushy.
Ask qualifying questions (daily commute distance, budget, gas vs electric preference).
Recommend specific models when possible.
Use tools when needed."""

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"]

    def generate():
        stream = client.chat.completions.create(
            model="grok-4.3",
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
