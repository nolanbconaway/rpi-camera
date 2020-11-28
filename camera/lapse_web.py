"""Provide a flask app that enables monitoring of the timelapse."""
import base64
import datetime

import pytz
from flask import Flask, jsonify, render_template
from gevent.pywsgi import WSGIServer

from camera import config

LAPSE_STORAGE = config.STORAGE / "lapses"


app = Flask(__name__, template_folder="html")


def get_latest() -> dict:
    """Return a dictionary of the info about the latest timelapse session."""
    latest_lapse_dir = max([x for x in LAPSE_STORAGE.iterdir() if x.is_dir()])
    images = [i for i in latest_lapse_dir.glob("*.jpg") if i.stat().st_size > 0]
    if not images:
        return dict()
    latest_image = max(images)
    return dict(
        image_path=latest_image,
        image_bytes_b64=base64.standard_b64encode(latest_image.read_bytes()).decode(),
        # picamera uses local time and I cant figure out how to configure.
        ts=pytz.timezone("US/Eastern").localize(
            datetime.datetime.fromisoformat(latest_image.with_suffix("").name)
        ),
        lapse_n=len(images),
        lapse_started_at=datetime.datetime.fromisoformat(
            latest_lapse_dir.with_suffix("").name
        ),
    )


@app.route("/latest-api")
def latest_api():
    """JSON API for the latest info about the latest timelapse session."""
    latest = get_latest()
    return jsonify(
        dict(
            image=latest["image_bytes_b64"],
            ts=latest["ts"],
            lapse_n=latest["lapse_n"],
            lapse_started_at=latest["lapse_started_at"],
        )
    )


@app.route("/")
def index():
    return render_template("lapse-web.html")


# production http server if called in main.
if __name__ == "__main__":
    WSGIServer(("0.0.0.0", config.WEB_PORT), app).serve_forever()
