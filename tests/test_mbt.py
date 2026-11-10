import pytest
import threading
import subprocess
import requests
from unittest.mock import patch, MagicMock
from wsgiref.simple_server import make_server
from hypothesis import settings, strategies as st, HealthCheck, given
from hypothesis.stateful import RuleBasedStateMachine, rule, precondition

import app
from client import APIClient


@pytest.fixture(scope="session", autouse=True)
def run_server():
    app.TEST_MODE = True
    server = make_server("127.0.0.1", 8080, app.app)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    yield
    server.shutdown()


class APIStateMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        self.client = APIClient()
        self.clients = []
        self.messages = []

    @rule(user_agent=st.text(min_size=1, max_size=20))
    def add_client(self, user_agent):
        res = self.client.rest_api_v2_add_client(user_agent)
        assert "uid" in res
        self.clients.append(res["uid"])

    @rule()
    def collect_client(self):
        self.client.rest_api_v2_collect_client()

    @rule(data=st.fixed_dictionaries({"user_agent": st.text(max_size=20)}))
    @precondition(lambda self: len(self.clients) > 0)
    def revise_client(self, data):
        uid = self.clients[-1]
        res = self.client.rest_api_v2_revise_client(uid, data)
        assert res.get("user_agent") == data["user_agent"]

    @rule(
        data=st.text(min_size=1, max_size=20),
        desc=st.text(max_size=20),
        tags=st.text(max_size=20),
        stage=st.text(max_size=20),
    )
    @precondition(lambda self: len(self.clients) > 0)
    def add_message(self, data, desc, tags, stage):
        client_id = self.clients[-1]
        res = self.client.rest_api_v2_add_message(
            data, client_id, desc, tags, stage
        )
        assert "uid" in res
        self.messages.append(res["uid"])

    @rule()
    @precondition(lambda self: len(self.clients) > 0)
    def collect_message(self):
        self.client.rest_api_v2_collect_message(self.clients[-1])

    @rule(data=st.fixed_dictionaries({"stage": st.text(max_size=20)}))
    @precondition(lambda self: len(self.messages) > 0)
    def revise_message(self, data):
        self.client.rest_api_v2_revise_message(self.messages[-1], data)

    @rule()
    @precondition(lambda self: len(self.messages) > 0)
    def collect_feedback(self):
        self.client.rest_api_v2_collect_feedback(self.messages[-1])

    @rule()
    def collect_report(self):
        self.client.rest_api_v2_collect_report()

    @rule()
    def test_bad_headers_406(self):
        res = requests.get(
            f"{self.client.base_url}/rest/api/v2/collect-client"
        )
        assert res.status_code == 406

    @rule()
    def test_bad_headers_415(self):
        res = requests.post(
            f"{self.client.base_url}/rest/api/v2/add-client?user_agent=test",
            headers={"Accept-Language": "ru-RU", "Content-Type": "text/plain"},
        )
        assert res.status_code == 415

    @rule()
    @precondition(lambda self: len(self.clients) > 0)
    def collect_client_by_uid(self):
        uid = self.clients[-1]
        res = self.client.rest_api_v2_collect_client(uid=uid)
        assert any(c["uid"] == uid for c in res)

    @rule()
    def revise_client_not_found(self):
        r = requests.put(
            f"{self.client.base_url}/rest/api/v2/revise-client/999999",
            json={"user_agent": "x"},
            headers=self.client.headers,
        )
        assert r.status_code == 404

    @rule()
    @precondition(lambda self: len(self.clients) > 0)
    def revise_client_empty_body(self):
        uid = self.clients[-1]
        r = requests.put(
            f"{self.client.base_url}/rest/api/v2/revise-client/{uid}",
            json={},
            headers=self.client.headers,
        )
        assert r.status_code == 400

    @rule()
    def add_message_no_client(self):
        r = requests.post(
            f"{self.client.base_url}/rest/api/v2/add-message?data=test",
            headers=self.client.headers,
        )
        assert r.status_code == 400

    @rule(stage=st.text(max_size=10))
    @precondition(lambda self: len(self.clients) > 0)
    def collect_message_with_stage(self, stage):
        self.client.rest_api_v2_collect_message(self.clients[-1], stage=stage)

    @rule()
    def revise_message_not_found(self):
        r = requests.put(
            f"{self.client.base_url}/rest/api/v2/revise-message/999999",
            json={"stage": "x"},
            headers=self.client.headers,
        )
        assert r.status_code == 404

    @rule()
    @precondition(lambda self: len(self.messages) > 0)
    def revise_message_empty_body(self):
        uid = self.messages[-1]
        r = requests.put(
            f"{self.client.base_url}/rest/api/v2/revise-message/{uid}",
            json={},
            headers=self.client.headers,
        )
        assert r.status_code == 400


TestAPI = APIStateMachine.TestCase
TestAPI.settings = settings(
    max_examples=50,
    stateful_step_count=20,
    suppress_health_check=[HealthCheck.too_slow],
)

_SAFE_ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"


@given(data=st.text(alphabet=_SAFE_ALPHABET, min_size=1, max_size=10))
@settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
def test_subprocess_success(data):
    res = requests.post(
        "http://127.0.0.1:8080/rest/api/v2/add-client?user_agent=t",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 200, res.text
    cid = res.json()["uid"]

    app.TEST_MODE = False
    try:
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            r = requests.post(
                f"http://127.0.0.1:8080/rest/api/v2/add-message?data={data}&client={cid}",
                headers={
                    "Accept-Language": "ru-RU",
                    "Content-Type": "application/json",
                },
            )
            assert r.status_code == 200, r.text
            assert mock_run.called
    finally:
        app.TEST_MODE = True


@given(data=st.text(alphabet=_SAFE_ALPHABET, min_size=1, max_size=10))
@settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
def test_subprocess_failure(data):
    res = requests.post(
        "http://127.0.0.1:8080/rest/api/v2/add-client?user_agent=t",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert res.status_code == 200, res.text
    cid = res.json()["uid"]

    app.TEST_MODE = False
    try:
        with patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "cmd", b"", b"error"),
        ):
            r = requests.post(
                f"http://127.0.0.1:8080/rest/api/v2/add-message?data={data}&client={cid}",
                headers={
                    "Accept-Language": "ru-RU",
                    "Content-Type": "application/json",
                },
            )
            assert r.status_code == 500
    finally:
        app.TEST_MODE = True


@given(stage=st.text(alphabet=_SAFE_ALPHABET, min_size=1, max_size=10))
@settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
def test_revise_message_success(stage):
    r1 = requests.post(
        "http://127.0.0.1:8080/rest/api/v2/add-client?user_agent=t",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    cid = r1.json()["uid"]
    r2 = requests.post(
        f"http://127.0.0.1:8080/rest/api/v2/add-message?data=x&client={cid}",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    mid = r2.json()["uid"]

    r = requests.put(
        f"http://127.0.0.1:8080/rest/api/v2/revise-message/{mid}",
        json={"stage": stage},
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert r.status_code == 200
    assert r.json()["stage"] == stage


@given(stage=st.text(alphabet=_SAFE_ALPHABET, min_size=1, max_size=10))
@settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
def test_revise_message_empty_body(stage):
    r1 = requests.post(
        "http://127.0.0.1:8080/rest/api/v2/add-client?user_agent=t",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    cid = r1.json()["uid"]
    r2 = requests.post(
        f"http://127.0.0.1:8080/rest/api/v2/add-message?data=x&client={cid}",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    mid = r2.json()["uid"]

    r = requests.put(
        f"http://127.0.0.1:8080/rest/api/v2/revise-message/{mid}",
        json={},
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert r.status_code == 400


@given(response=st.text(alphabet=_SAFE_ALPHABET, min_size=1, max_size=10))
@settings(max_examples=5, suppress_health_check=[HealthCheck.too_slow])
def test_collect_feedback_and_report(response):
    r1 = requests.post(
        "http://127.0.0.1:8080/rest/api/v2/add-client?user_agent=t",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    cid = r1.json()["uid"]
    r2 = requests.post(
        f"http://127.0.0.1:8080/rest/api/v2/add-message?data=x&client={cid}&tags=tag",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    mid = r2.json()["uid"]

    app.feedbacks.append(
        {
            "uid": 999,
            "created": int(__import__("datetime").datetime.now().timestamp()),
            "response": response,
            "message": mid,
        }
    )

    r = requests.get(
        f"http://127.0.0.1:8080/rest/api/v2/collect-feedback/{mid}",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert data[0]["response"] == response

    r = requests.get(
        "http://127.0.0.1:8080/rest/api/v2/collect-report",
        headers={
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        },
    )
    assert r.status_code == 200
    report = r.json()
    assert any(item["response"] == response for item in report)
