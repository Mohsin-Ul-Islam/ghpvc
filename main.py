from os import environ
from ipaddress import ip_address, ip_network

from flask import Flask, make_response, Response, request
from redis import Redis
from requests import get

app = Flask(__name__)

client = Redis(
    host=environ["REDIS_HOST"],
    port=environ["REDIS_PORT"],
    decode_responses=True,
    db=0,
)

github_camo_ips = environ.get("GITHUB_CAMO_IPS", "").split(",")


def github_username_exists(username: str) -> bool:
    return get(f"https://github.com/{username}").status_code == 200


def get_ghpvc_image(count: int) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="113" height="20"><linearGradient id="b" x2="0" y2="100%"><stop offset="0" stop-color="#bbb" stop-opacity=".1"/><stop offset="1" stop-opacity=".1"/></linearGradient><mask id="a"><rect width="113" height="20" rx="3" fill="#fff"/></mask><g mask="url(#a)"><rect width="81" height="20" fill="#555"/><rect x="81" width="32" height="20" fill="#007ec6"/><rect width="113" height="20" fill="url(#b)"/></g><g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11"><text x="41.5" y="15" fill="#010101" fill-opacity=".3">Profile views</text><text x="41.5" y="14">Profile views</text><text x="96" y="15" fill="#010101" fill-opacity=".3">{count}</text><text x="96" y="14">{count}</text></g></svg>'


@app.route("/", methods=["GET"])
def index() -> tuple:
    return "Github profile view counter api.", 200


@app.route("/<username>", methods=["GET"])
def get_view_count(username: str) -> Response:

    username = username.lower()
    count = client.get(username)
    if count is None:

        if not github_username_exists(username):
            return "Github username not found!", 404

        count = 0
        client.set(username, count)

    for ip_range in github_camo_ips:
        if ip_address(request.remote_addr) in ip_network(ip_range):
            count = int(count) + 1
            client.set(username, count)
            break

    response = make_response(get_ghpvc_image(count), 200)

    response.headers["Content-Type"] = "image/svg+xml"
    response.headers["Cache-Control"] = "max-age=0, no-cache, no-store, must-revalidate"

    return response
