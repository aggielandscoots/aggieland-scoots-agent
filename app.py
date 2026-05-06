from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import json

app = Flask(__name__)
CORS(app)  # This fixes the connection issue from your website

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

@app.route("/")
def home():
    return jsonify({"status": "✅ Aggieland Scoots AI Backend is LIVE and Ready"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        messages = [{"role": "system", "content": "You are a helpful Aggieland Scoots AI Agent. Be friendly and helpful."}] + data.get("messages", [])

        stream = client.chat.completions.create(
            model="grok-4.3",
            messages=messages,
            stream=True
        )

        def generate():
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
