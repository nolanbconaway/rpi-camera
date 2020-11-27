"""Capture time lapse photos to the storage dir. 

Each lapse instance will be saved to its own directory named after the UTC isoformat
start date, with each image saved with its UTC isoformat stamp.
"""
import argparse
import datetime
import time
from fractions import Fraction

import picamera

from camera import config

LAPSE_STORAGE = config.STORAGE / "lapses"


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lapse_seconds", metavar="N", type=float, help="Capture photo every N seconds."
    )
    parser.add_argument(
        "--rot", dest="rotation", type=int, help="degrees rotation", default=0
    )
    parser.add_argument(
        "--res",
        dest="resolution",
        type=str,
        choices=tuple(config.RESOLUTION_MAPPING.keys()),
        default="480p",
        help="resolution",
    )
    parser.add_argument("--quality", type=int, help="quality specifier", default=85)
    parser.add_argument("--dark", action="store_true")

    return parser


if __name__ == "__main__":
    args = make_parser().parse_args()
    if args.lapse_seconds < 0:
        raise ValueError("Invalid lapse time.")
    if args.dark and args.lapse_seconds < 10:
        print("WARN: short lapses might not be realized in dark mode.")

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

        print("Adjusting the camera...")
        time.sleep(10 if args.dark else 2)

        storage_dir = LAPSE_STORAGE / datetime.datetime.utcnow().isoformat()
        storage_dir.mkdir(exist_ok=True)

        print("Starting captures...")
        for filename in camera.capture_continuous(
            str(storage_dir) + "/{timestamp:%Y-%m-%dT%H:%M:%S}.jpg",
            quality=args.quality,
        ):
            print(f"  captured to {filename}")
            time.sleep(args.lapse_seconds)
