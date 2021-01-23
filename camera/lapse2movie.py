"""Combine images taken in a timelapse to a video.

Image filenames are assumed to be in sorted order. Each image will be a single frame, so
the FPS argument can be used to adjust the "speed" of the video.
"""

import argparse
import datetime
import multiprocessing
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
    parser.add_argument("--stamp", action="store_true")
    parser.add_argument(
        "--cores",
        type=int,
        default=multiprocessing.cpu_count(),
    )
    return parser


def load_image(p: Path):
    """Load a single image from a path."""
    dt = datetime.datetime.fromisoformat(p.name[:-4])
    return dt, cv2.imread(str(p.resolve()))


if __name__ == "__main__":
    args = make_parser().parse_args()

    # load a single image for the dimensions.
    image_paths = sorted([p for p in args.src.glob("*.jpg") if p.stat().st_size > 0])
    height, width, layers = load_image(image_paths[0])[1].shape

    # load the rest via multiprocessing
    print("Loading images into memory...")
    with multiprocessing.Pool(args.cores) as pool:
        images = dict(
            list(tqdm(pool.imap(load_image, image_paths), total=len(image_paths)))
        )

    print("Making video...")
    with VideoWriter(
        str(args.dst), cv2.VideoWriter_fourcc(*"DIVX"), args.fps, (width, height)
    ) as video:
        for dt, image in tqdm(images.items()):
            ts = dt.strftime("%I:%M%p")
            # if i change this even once more it will become a function.
            if args.stamp:
                image = cv2.putText(
                    img=image,
                    text=ts,
                    org=(int(width * 0.01), int(height * 0.03)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(0, 0, 0),
                    thickness=4,
                )
                image = cv2.putText(
                    img=image,
                    text=ts,
                    org=(int(width * 0.01), int(height * 0.03)),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=1,
                    color=(255, 255, 255),
                    thickness=1,
                )
            video.write(image)
