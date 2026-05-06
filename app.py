from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app)  # Important for connecting from your website

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ====================== BASIC KNOWLEDGE BASE ======================
SYSTEM_PROMPT = """You are the official Aggieland Scoots AI Sales Agent.
You are friendly, helpful, and Aggie-proud.
Help customers with mopeds, scooters, eBikes, motorcycles, service, and lead generation."""

@app.route("/")
def home():
    return jsonify({
        "status": "✅ Aggieland Scoots AI Agent Backend is LIVE",
        "version": "1.0",
        "endpoint": "/chat"
    })

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        if not data or "messages" not in data:
            return jsonify({"error": "Missing messages"}), 400

        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + data["messages"]

        def generate():
            stream = client.chat.completions.create(
                model="grok-4.3",
                messages=messages,
                temperature=0.7,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        print("Error in /chat:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
