"""Take a single shot from the camera and save it to a directory."""
import argparse
import datetime
import subprocess
import sys
import time
from fractions import Fraction
from pathlib import Path

import picamera

from camera import config


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest", type=Path)
    parser.add_argument(
        "--rot", dest="rotation", type=int, help="degrees rotation", default=0
    )
    parser.add_argument(
        "--res",
        dest="resolution",
        type=str,
        choices=tuple(config.RESOLUTION_MAPPING.keys()),
        default="720p",
        help="resolution",
    )
    parser.add_argument("--quality", type=int, help="quality specifier", default=85)
    parser.add_argument("--dark", action="store_true")

    return parser


if __name__ == "__main__":
    args = make_parser().parse_args()

    # config the camera
    kw = dict(resolution=config.RESOLUTION_MAPPING[args.resolution])
    if args.dark:
        kw["framerate"] = Fraction(1, 6)
        kw["sensor_mode"] = 3

    with picamera.PiCamera(**kw) as camera:
        camera.rotation = args.rotation
        if args.dark:
            camera.shutter_speed = 6000000
            camera.iso = 800
            camera.exposure_mode = "off"

        time.sleep(10 if args.dark else 2)

        args.dest.mkdir(exist_ok=True)
        image_path = args.dest / (datetime.datetime.now().isoformat() + ".jpg")

        camera.capture(str(image_path))
