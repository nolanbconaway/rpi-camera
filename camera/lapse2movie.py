import argparse
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


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("src", type=existing_dir_arg)
    parser.add_argument("--dst", type=Path, default=Path("video.avi"))
    parser.add_argument("--fps", type=int, default=4)

    return parser


if __name__ == "__main__":
    args = make_parser().parse_args()
    images = sorted([p for p in args.src.glob("*.jpg")])
    height, width, layers = cv2.imread(str(images[0].resolve())).shape

    video = cv2.VideoWriter(
        args.dst,
        cv2.VideoWriter_fourcc(*"DIVX"),
        args.fps,
        (width, height),
    )
    for image in tqdm(images):
        video.write(cv2.imread(str(image.resolve())))

    video.release()
