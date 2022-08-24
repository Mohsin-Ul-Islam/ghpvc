from os import environ

from flask import Flask
from redis import Redis

app = Flask(__name__)

client = Redis(
    host=environ["REDIS_HOST"],
    port=environ["REDIS_PORT"],
    decode_responses=True,
    db=0,
)


@app.route("/", methods=["GET"])
def index() -> tuple:
    return "Github profile view counter api.", 200


@app.route("/<username>/count", methods=["GET"])
def get_view_count(username: str) -> dict:

    count = client.get(username)
    if count is None:
        count = 0

    count = int(count) + 1
    client.set(username, count)

    return {"count": count}
