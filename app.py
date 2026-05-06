from flask import Flask, request, Response
from openai import OpenAI
import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ====================== FULL WEBSITE RAG KNOWLEDGE BASE ======================
KNOWLEDGE_BASE = """
Aggieland Scoots (Scoots) - 1600 Texas Ave S, College Station, TX 77840
Phone: (979) 446-0900 | Email: info@aggielandscoots.com
Hours: Mon–Sat 10am–6pm | Aggie Owned & Operated since 2014.

SERVICES: Sales, full service/repair, rentals, test rides, learn-to-ride tutorials, financing, delivery (local + nationwide shipping).

BRANDS: Genuine, Kymco, Lance, SYM, Honda, NIU, Wolf, Buddy, Lectric, GoTrax, Chicago Scooter Co, Moto Morini, Royal Alloy, etc.

KEY UPSell POINTS (use these when customer mentions eScooter or eBike):
- Mopeds are more comfortable for longer rides.
- Mopeds have much longer range (75–140+ MPG vs 12–60 mile battery range).
- Mopeds are safer — they ride in the street where drivers are looking for traffic, while eScooters/eBikes cross driveways and intersections where people aren’t expecting them.
- Scoots is well known for excellent eScooter and eBike repairs (flat tires, error codes, brakes, batteries, etc.), so we can service anything they already own.

FAQ HIGHLIGHTS:
- Texas 50cc moped: Only needs regular Class C driver’s license.
- Helmet not required if 21+ with health insurance (but always recommended).
- Insurance usually ~$80/year liability.
- We repair almost every brand of eScooter and eBike (Ancheer, Apollo, Lectric, NIU, GoTrax, etc.).
- Oil change every 6 months or 1,000 miles.
- Test rides and learn-to-ride tutorial included.

CURRENT INVENTORY EXAMPLES (prices often on sale):
- 2024 Buddy 50: $2,349 (45+ MPH, 100 MPG)
- 2024 Go 50: $1,235 (30 MPH, 100+ MPG)
- 2024 Rugby II 150: $1,799 (50+ MPH, 75+ MPG)
- 2024 X-Cape 650: $6,999 (105 MPH)
- Many eScooters from $709, eBikes, and motorcycles available.
"""

SYSTEM_PROMPT = """You are the official Aggieland Scoots AI Sales Agent.
Use the full knowledge base above to answer accurately.

CORE GOALS:
1. Be friendly, helpful, and Aggie-proud.
2. Qualify the customer (commute distance, budget, gas vs electric, daily miles).
3. When they show interest in eScooters or eBikes, naturally upsell moped/motorcycle using the exact points: more comfortable, much longer range, safer on streets, and remind them we expertly repair eScooters/eBikes if they keep theirs.
4. Always try to capture a lead (name, email, phone) and book a test ride or quote.

When you have name + email + phone + interest → immediately call capture_lead tool."""

TOOLS = [
    {"type": "function", "function": {"name": "get_inventory", "description": "Get current inventory", "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "capture_lead",
        "description": "Capture lead and SEND REAL EMAIL to dealership",
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
    }}
]

def send_lead_email(lead_data):
    try:
        msg = MIMEMultipart()
        msg['From'] = os.getenv("EMAIL_USER")
        msg['To'] = "info@aggielandscoots.com"
        msg['Subject'] = f"NEW LEAD from AI Agent: {lead_data.get('name')} - {lead_data.get('interest','')}"

        body = f"""
New lead from Aggieland Scoots AI Agent:

Name: {lead_data.get('name')}
Email: {lead_data.get('email')}
Phone: {lead_data.get('phone')}
Interest: {lead_data.get('interest','N/A')}
Recommended Model: {lead_data.get('recommended_model','N/A')}
Notes: {lead_data.get('notes','N/A')}

Captured at {os.getenv('RENDER_EXTERNAL_URL', 'Website')}
"""
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("Email failed:", e)
        return False

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
            elif delta.tool_calls:
                for tool_call in delta.tool_calls:
                    if tool_call.function.name == "capture_lead":
                        args = json.loads(tool_call.function.arguments)
                        success = send_lead_email(args)
                        if success:
                            yield f"data: Perfect! I’ve sent your info to the team — they’ll reach out soon to schedule a test ride.\n\n"
                        else:
                            yield f"data: Thanks! I’ve captured your info.\n\n"

    return Response(generate(), mimetype="text/event-stream")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
