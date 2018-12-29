"""Example views for our Flask Application."""
import uuid

import flask
import structlog

import limiterapp

time_format = "%Y-%m-%dT%H:%M:%S.%f%z"
logger = structlog.get_logger()
app = limiterapp.app


@app.route("/", methods=["GET", "POST"])
def home():
    """Serve up our root request path."""
    log = logger.new(request_id=str(uuid.uuid4()), path="/", view="home")
    request = flask.request
    throttle = limiterapp.anonymous_throttle
    auth = request.authorization
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    username = "anonymous"
    response = flask.Response()

    if auth and auth.username and auth.password:
        throttle = limiterapp.authenticated_throttle
        username = auth.username
        log.info("sent credentials", username=auth.username)

    userkey = f"{username}@{ip_address}"
    result = throttle.check(key=userkey, quantity=1)
    response.headers.extend(
        [
            ("X-RateLimit-Limit", result.limit),
            ("X-RateLimit-Remaining", result.remaining),
            ("X-RateLimit-Reset", result.resets_at().strftime(time_format)),
            ("X-RateLimit-Retry", result.retry_at().strftime(time_format)),
        ]
    )
    response.headers["Content-Type"] = "text/plain"
    if result.limited:
        log.info("ratelimited", username=username)
        response.status_code = 403
    else:
        response.status_code = 200
        response.data = f"Hello from home, {username}"
    log.info("completed request", status_code=response.status_code)
    return response
