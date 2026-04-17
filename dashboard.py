from flask import Flask, jsonify, render_template_string
import json
import datetime

app = Flask(__name__)

REPORT_FILE = "/home/harshith-s-b/sdn_project/traffic_report.json"
HISTORY_FILE = "/home/harshith-s-b/sdn_project/traffic_history.json"

MAX_HISTORY = 30


def load_report():
    try:
        with open(REPORT_FILE) as f:
            return json.load(f)
    except:
        return None


def save_history(report):
    history = []
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
    except:
        pass

    history.append({
        "timestamp": datetime.datetime.now().isoformat(),
        "data": report
    })

    history = history[-MAX_HISTORY:]

    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_history():
    try:
        with open(HISTORY_FILE) as f:
            return json.load(f)
    except:
        return []


@app.route("/")
def index():
    with open("dashboard.html") as f:
        return render_template_string(f.read())


@app.route("/api/live")
def api_live():
    report = load_report()
    if report:
        save_history(report)
        return jsonify({"status": "ok", "data": report})
    return jsonify({"status": "no_data", "data": None})


@app.route("/api/history")
def api_history():
    return jsonify(load_history())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
