"""Provide a flask app that enables monitoring of the timelapse.

Set an env variable, IMAGE_DIR, if you would like this to point to a specific directory.
"""
import base64
import datetime
import os
from pathlib import Path

import pytz
from flask import Flask, jsonify, render_template
from gevent.pywsgi import WSGIServer

from camera import config

DEFAULT_LAPSE_STORAGE = config.STORAGE / "lapses"


app = Flask(__name__, template_folder="html")


def get_latest() -> dict:
    """Return a dictionary of the info about the latest timelapse session."""
    if os.getenv("IMAGE_DIR") is None:
        lapse_dir = max([x for x in DEFAULT_LAPSE_STORAGE.iterdir() if x.is_dir()])
    else:
        lapse_dir = Path(os.getenv("IMAGE_DIR"))

    images = [i for i in lapse_dir.glob("*.jpg") if i.stat().st_size > 0]
    if not images:
        return dict()
    latest_image = max(images)
    print(latest_image)
    return dict(
        image_path=latest_image,
        image_bytes_b64=base64.standard_b64encode(latest_image.read_bytes()).decode(),
        # picamera uses local time and I cant figure out how to configure.
        ts=pytz.timezone("US/Eastern").localize(
            datetime.datetime.fromisoformat(latest_image.with_suffix("").name)
        ),
        lapse_n=len(images),
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
        )
    )


@app.route("/")
def index():
    return render_template("lapse-web.html")


# production http server if called in main.
if __name__ == "__main__":
    WSGIServer(("0.0.0.0", config.WEB_PORT), app).serve_forever()
