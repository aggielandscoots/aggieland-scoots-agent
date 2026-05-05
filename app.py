from flask import Flask, request, jsonify
from openai import OpenAI
import os

app = Flask(__name__)
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

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

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "capture_lead",
            "description": "Capture a qualified lead and email it to the dealership",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"},
                    "phone": {"type": "string"},
                    "interest": {"type": "string"},
                    "recommended_model": {"type": "string"}
                },
                "required": ["name", "email", "phone"]
            }
        }
    }
]

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"]

    response = client.chat.completions.create(
        model="grok-4.3",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
        temperature=0.7,
        stream=True
    )

    # For simplicity we'll return full response here — streaming code available if you want typing effect
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_response += chunk.choices[0].delta.content

    # If tool was called, handle it (lead capture example using your email)
    # Add your actual email logic here later if needed

    return jsonify({"response": full_response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
