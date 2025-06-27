from flask import Flask, render_template, request, jsonify
import json
import os

CONFIG_PATH = "config.json"

app = Flask(__name__)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(cfg):
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


@app.route("/")
def index():
    config = load_config()
    return render_template("index.html", config=config)


@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "POST":
        cfg = request.json
        save_config(cfg)
        return jsonify({"status": "ok"})
    return jsonify(load_config())


@app.route("/set_livestream", methods=["POST"])
def set_livestream():
    import requests
    config = load_config()
    pi_zero_addr = config.get("pi_zero_ip", "127.0.0.1")
    payload = request.json
    try:
        r = requests.post(f"http://{pi_zero_addr}:5001/set", json=payload, timeout=2)
        return r.json()
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)
