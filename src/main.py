import contextlib
import io
import sys
from datetime import datetime


def assign_uid(list_type):
    if len(uid_list[list_type]) == 1:
        uid = uid_list[list_type][0]
        uid_list[list_type][0] += 1
    else:
        uid = uid_list[list_type].pop()
    uid_list[list_type + 3].append(uid)
    return uid


class Feedback:
    def __init__(self, response: str, stage: str, failure: str, message: int):
        self.uid = assign_uid(0)
        self.created = int((datetime.now()).timestamp())
        self.response = response
        self.stage = stage
        self.failure = failure
        self.message = int(message)


class Message:
    def __init__(
        self, data: str, client: int, description: str, tags: str, stage: str
    ):
        self.uid = assign_uid(1)
        self.created = int((datetime.now()).timestamp())
        self.data = data
        self.client = int(client)
        self.description = description
        self.tags = tags
        self.stage = stage


class Client:
    def __init__(self, user_agent: str):
        self.uid = assign_uid(2)
        self.created = int((datetime.now()).timestamp())
        self.user_agent = user_agent


uid_list = [[0], [0], [0], [], [], []]

feedback_list = []
message_list = []
client_list = []


def run_task(code: str) -> str:
    buffer = io.StringIO()
    try:
        with contextlib.redirect_stdout(buffer):
            try:
                result = eval(code)
            except SyntaxError:
                exec(code)
    except Exception:
        return code
    printed = buffer.getvalue().rstrip("\n")
    if printed:
        return printed
    if result is not None:
        return str(result)
    return code


def main(argv: list) -> int:
    with open(argv[1], "r", encoding="utf-8-sig") as task_file:
        code = task_file.read()

    print(run_task(code))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as error:
        print(error, file=sys.stderr)
        sys.exit(1)
