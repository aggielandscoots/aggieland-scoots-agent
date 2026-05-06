from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from openai import OpenAI
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # Allow your website

client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

@app.route("/")
def home():
    return jsonify({"status": "✅ LIVE - Aggieland Scoots AI Backend is running"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        messages = [{"role": "system", "content": "You are helpful Aggieland Scoots AI Agent."}] + data.get("messages", [])

        def generate():
            stream = client.chat.completions.create(
                model="grok-4.3",
                messages=messages,
                stream=True
            )
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"

        return Response(generate(), mimetype="text/event-stream")
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Internal error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
