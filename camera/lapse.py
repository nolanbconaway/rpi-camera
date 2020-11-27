"""Capture time lapse photos to the storage dir. 

Each lapse instance will be saved to its own directory named after the UTC isoformat
start date, with each image saved with its UTC isoformat stamp.
"""

import argparse
import datetime
import time

import picamera

from camera import config


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "lapse_seconds", metavar="N", type=int, help="Capture photo every N seconds."
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

    return parser


if __name__ == "__main__":
    args = make_parser().parse_args()
    with picamera.PiCamera(
        resolution=config.RESOLUTION_MAPPING[args.resolution]
    ) as camera:
        camera.rotation = args.rotation
        time.sleep(2)

        storage_dir = config.STORAGE / "lapses" / datetime.datetime.utcnow().isoformat()
        storage_dir.mkdir(exist_ok=True)
        for filename in camera.capture_continuous(
            str(storage_dir) + "/{timestamp:%Y-%m-%dT%H:%M:%S}.jpg"
        ):
            print(f"Captured to {filename}")
            time.sleep(args.lapse_seconds)
