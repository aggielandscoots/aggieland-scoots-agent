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
Aggieland Scoots (Scoots) - 1600 Texas Ave S, College Station, TX 77840
Phone: (979) 446-0900 | Email: info@aggielandscoots.com
Hours: Mon–Sat 10am–6pm
Aggie Owned & Operated since 2014.

We sell: Mopeds, Motor Scooters, Motorcycles, eScooters, eBikes (new & pre-owned).
Brands: Genuine Scooter Co, Kymco, Lance, SYM, Honda, NIU, Wolf, Buddy, Lectric, GoTrax, etc.

Key Benefits:
- Test rides available on most models
- Learn-to-ride tutorial included
- Labor warranty on all new eScooters & eBikes
- Delivery available (local + nationwide shipping)
- Financing available
- Full service & repair department (warranty + non-warranty)

Popular Models (Current Pricing):
- 2024 Buddy 50: $2,349 (45+ MPH, 100 MPG)
- 2024 Go 50: $1,235 (30 MPH, 100+ MPG)
- 2024 Rugby II 150: $1,799 (50+ MPH, 75+ MPG)
- 2024 X-Cape 650: $6,999 (105 MPH, 45+ MPG)
- A7 eScooter: $709 (20+ MPH, 28+ mile range)
- Many more — use get_inventory tool for full list.

Texas Laws: Mopeds (under 50cc) only need Class C driver's license.
Service: We service almost all brands including Honda, Yamaha, Vespa.
"""

# ====================== TOOLS ======================
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_inventory",
            "description": "Get current scooter/moped inventory with prices",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture and email a qualified lead",
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
Aggie-owned & operated in College Station, TX (1600 Texas Ave S).
We sell new & pre-owned mopeds, motor scooters, eScooters, eBikes & motorcycles.
Brands: Genuine Scooter Co, Kymco, Lance, SYM, Honda, NIU, Wolf, Buddy, etc.
Services: sales, service, rentals, test rides, financing, delivery.

Your job:
1. Answer questions about our products, MPG, range, speed, warranties, rentals.
2. Ask smart questions about their commute (distance, daily miles, parking, budget, gas vs electric preference).
3. Recommend the BEST matching scooter/bike with reasons and price.
4. Always try to capture a lead (name, email, phone, best time for test ride/quote).

Be friendly, Texas proud, concise, and action-oriented. Never pushy. End with a clear next step."""

KNOWLEDGE BASE:
{KNOWLEDGE_BASE}

Be friendly, helpful, Aggie-proud, concise, and sales-oriented but never pushy.
Ask qualifying questions about commute, budget, gas/electric preference.
Recommend 1-2 best matches when possible.
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
            delta = chunk.choices[0].delta
            if delta.content:
                yield f"data: {delta.content}\n\n"
            # Tool handling can be expanded later

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
