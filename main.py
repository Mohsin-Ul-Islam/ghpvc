from os import environ

from flask import Flask, make_response, Response
from redis import Redis
from requests import get

app = Flask(__name__)

client = Redis(
    host=environ["REDIS_HOST"],
    port=environ["REDIS_PORT"],
    decode_responses=True,
    db=0,
)


def github_username_exists(username: str) -> bool:
    return get(f"https://github.com/{username}").status_code == 200


def get_ghpvc_image(count: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="104" height="20" role="img" aria-label="Profile Views: {count}"><title>Profile Views: {count}</title><linearGradient id="s" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><clipPath id="r"><rect width="104" height="20" rx="3" fill="#fff"/></clipPath><g clip-path="url(#r)"><rect width="81" height="20" fill="#555"/><rect x="81" width="23" height="20" fill="#007ec6"/><rect width="104" height="20" fill="url(#s)"/></g><g fill="#fff" text-anchor="middle" font-family="Verdana,Geneva,DejaVu Sans,sans-serif" text-rendering="geometricPrecision" font-size="110"><text aria-hidden="true" x="415" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="710">Profile Views</text><text x="415" y="140" transform="scale(.1)" fill="#fff" textLength="710">Profile Views</text><text aria-hidden="true" x="915" y="150" fill="#010101" fill-opacity=".3" transform="scale(.1)" textLength="130">{count}</text><text x="915" y="140" transform="scale(.1)" fill="#fff" textLength="130">{count}</text></g></svg>'


@app.route("/", methods=["GET"])
def index() -> tuple:
    return "Github profile view counter api.", 200


@app.route("/<username>", methods=["GET"])
def get_view_count(username: str) -> Response:

    count = client.get(username)
    if count is None:

        if not github_username_exists(username):
            return "Github username not found!", 404

        count = 0

    count = int(count) + 1
    client.set(username, count)

    response = make_response(get_ghpvc_image(count), 200)

    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "max-age=0, no-cache, no-store, must-revalidate"

    return response
