"""Combine images taken in a timelapse to a video.

This works by reading the iso-formatted timestamps in the filenames. We want one frame 
per second of real time, and will re-use the most recent frame for periods where a new 
images has not been captured. 

Since there will be one frame per second, the FPS argument can be used to adjust the 
speed of the video relative to real time (5 FPS = 5x speedup).
"""

import argparse
import datetime
from contextlib import contextmanager
from pathlib import Path

import cv2
from tqdm import tqdm


def existing_dir_arg(s):
    p = Path(s)
    if not p.exists():
        raise ValueError(f"Nonexistent path: {s}")
    if not p.is_dir():
        raise ValueError(f"{s} is not a directory.")
    return p


def avi_path_arg(s):
    if not s.endswith(".avi"):
        raise ValueError(f"Expecting .avi output, got {s}.")
    return Path(s)


@contextmanager
def VideoWriter(*args, **kwargs):
    cap = cv2.VideoWriter(*args, **kwargs)
    try:
        yield cap
    finally:
        cap.release()


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=existing_dir_arg)
    parser.add_argument(
        "--fps",
        type=int,
        default=12,
    )
    parser.add_argument("--dst", type=Path, default=Path("video.avi"))
    return parser


def seconds_range(
    start_dt: datetime.datetime,
    end_dt: datetime.datetime,
    length_seconds: float = 1.0,
    inclusive: bool = False,
):
    """A range function but for datetimes. Returns a generator."""
    assert length_seconds > 0

    result = start_dt
    while result < end_dt:
        yield result
        result += datetime.timedelta(minutes=length_seconds)


def image_finder(ts, images, timestamps):
    """Get the latest image for a timestamp"""
    before_ts = list((t, i) for t, i in zip(timestamps, images) if t <= ts)
    _, image = sorted(before_ts)[-1]
    return image


if __name__ == "__main__":
    args = make_parser().parse_args()
    images = sorted([p for p in args.src.glob("*.jpg") if p.stat().st_size > 0])
    timestamps = [datetime.datetime.fromisoformat(p.name.strip(".jpg")) for p in images]

    height, width, layers = cv2.imread(str(images[0].resolve())).shape
    with VideoWriter(
        str(args.dst), cv2.VideoWriter_fourcc(*"DIVX"), args.fps, (width, height)
    ) as video:

        # for each second, find the latest image
        for ts in tqdm(list(seconds_range(timestamps[0], timestamps[-1]))):
            image = image_finder(ts, images, timestamps)
            video.write(cv2.imread(str(image.resolve())))
