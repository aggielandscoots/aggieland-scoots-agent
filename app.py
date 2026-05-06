from flask import Flask, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})   # Allow all websites

@app.route("/")
def home():
    return jsonify({"status": "✅ LIVE - Aggieland Scoots AI Backend is running"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("messages", [{}])[-1].get("content", "")

        # Simple echo response for testing
        response_text = f"Thank you for your message: '{user_message}'. I'm your Aggieland Scoots AI Agent 🛵 How can I help you today?"

        def generate():
            yield f"data: {response_text}\n\n"

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
