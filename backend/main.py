from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/chat")
def chat():
    return jsonify({"reply": "Hello from Zyra 🧠"})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=7799)