import json
import time
import subprocess
import sys
import argparse
import os
from datetime import datetime
from bottle import Bottle, request, response, run, HTTPResponse

app = Bottle()

TEST_MODE = False

clients = []
messages = []
feedbacks = []

uid_counters = {"client": 1, "message": 1, "feedback": 1}


def get_next_uid(entity_type):
    uid = uid_counters[entity_type]
    uid_counters[entity_type] += 1
    return uid


@app.hook("before_request")
def check_headers():
    if request.method in ("POST", "PUT", "PATCH"):
        content_type = request.get_header("Content-Type", "")
        if not content_type.startswith("application/json"):
            raise HTTPResponse(status=415, body="Unsupported Media Type")

    accept_lang = request.get_header("Accept-Language", "")
    if accept_lang != "ru-RU":
        raise HTTPResponse(status=406, body="Not Acceptable")


@app.post("/rest/api/v2/add-client")
def add_client():
    user_agent = request.query.get("user_agent", "")
    uid = get_next_uid("client")
    created = int(datetime.now().timestamp())

    client = {"uid": uid, "created": created, "user_agent": user_agent}
    clients.append(client)

    response.content_type = "application/json"
    return json.dumps(client)


@app.get("/rest/api/v2/collect-client")
def collect_client():
    res = clients
    uid = request.query.get("uid")
    if uid:
        res = [c for c in res if str(c["uid"]) == str(uid)]

    response.content_type = "application/json"
    return json.dumps(res)


@app.put("/rest/api/v2/revise-client/<uid:int>")
def revise_client(uid):
    data = request.json
    if not data:
        raise HTTPResponse(status=400, body="Invalid JSON")

    for c in clients:
        if c["uid"] == uid:
            c.update(data)
            response.content_type = "application/json"
            return json.dumps(c)
    raise HTTPResponse(status=404, body="Client not found")


@app.post("/rest/api/v2/add-message")
def add_message():
    data_val = request.query.get("data", "")
    client_id = request.query.get("client")
    description = request.query.get("description", "")
    tags = request.query.get("tags", "")
    stage = request.query.get("stage", "")

    if not client_id:
        raise HTTPResponse(status=400, body="Missing client id")
    client_id = int(client_id)

    if not TEST_MODE:
        try:
            process = subprocess.run(
                [sys.executable, "main.py"],
                input=data_val.encode("utf-8"),
                capture_output=True,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            raise HTTPResponse(
                status=500,
                body=f"CLI execution failed: {e.stderr.decode('utf-8')}",
            )

    uid = get_next_uid("message")
    created = int(datetime.now().timestamp())

    message = {
        "uid": uid,
        "created": created,
        "data": data_val,
        "client": client_id,
        "description": description,
        "tags": tags,
        "stage": stage,
    }
    messages.append(message)

    response.content_type = "application/json"
    return json.dumps(message)


@app.get("/rest/api/v2/collect-message/<client:int>")
def collect_message(client):
    res = [m for m in messages if m["client"] == client]
    stage = request.query.get("stage")
    if stage:
        res = [m for m in res if m["stage"] == stage]
    response.content_type = "application/json"
    return json.dumps(res)


@app.put("/rest/api/v2/revise-message/<uid:int>")
def revise_message(uid):
    data = request.json
    if not data:
        raise HTTPResponse(status=400, body="Invalid JSON")
    for m in messages:
        if m["uid"] == uid:
            m.update(data)
            response.content_type = "application/json"
            return json.dumps(m)
    raise HTTPResponse(status=404, body="Message not found")


@app.get("/rest/api/v2/collect-feedback/<message:int>")
def collect_feedback(message):
    res = [f for f in feedbacks if f["message"] == message]
    response.content_type = "application/json"
    return json.dumps(res)


@app.get("/rest/api/v2/collect-report")
def collect_report():
    now = int(datetime.now().timestamp())
    time_threshold = now - 5 * 60
    report_data = []

    for c in clients:
        for m in messages:
            if m["client"] == c["uid"] and m["created"] > time_threshold:
                for f in feedbacks:
                    if f["message"] == m["uid"]:
                        report_data.append(
                            {
                                "user_agent": c["user_agent"],
                                "response": f["response"],
                                "tags": m["tags"],
                            }
                        )
    response.content_type = "application/json"
    return json.dumps(report_data)


def load_seed_data(filepath: str):  # pragma: no cover

    if not os.path.exists(filepath):
        return

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    now = int(datetime.now().timestamp())

    for c in data.get("clients", []):
        clients.append(
            {
                "uid": get_next_uid("client"),
                "created": now - int(c.get("age_sec", 0)),
                "user_agent": c.get("user_agent", ""),
            }
        )

    for m in data.get("messages", []):
        messages.append(
            {
                "uid": get_next_uid("message"),
                "created": now - int(m.get("age_sec", 0)),
                "data": m.get("data", ""),
                "client": int(m.get("client", 0)),
                "description": m.get("description", ""),
                "tags": m.get("tags", ""),
                "stage": m.get("stage", ""),
            }
        )

    for fb in data.get("feedbacks", []):
        feedbacks.append(
            {
                "uid": get_next_uid("feedback"),
                "created": now - int(fb.get("age_sec", 0)),
                "response": fb.get("response", ""),
                "message": int(fb.get("message", 0)),
            }
        )


if __name__ == "__main__":  # pragma: no cover
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-mode", action="store_true")
    parser.add_argument("--seed-file", type=str, default=None)
    args = parser.parse_args()

    TEST_MODE = args.test_mode

    if args.seed_file:
        load_seed_data(args.seed_file)

    print(f"Запуск сервера на http://127.0.0.1:8080")
    run(app, host="0.0.0.0", port=8080, reloader=False)
