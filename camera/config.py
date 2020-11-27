"""Misc config vars."""
from pathlib import Path

RESOLUTION_MAPPING = {
    "640x480": "640x480",
    "480p": "640x480",
    "1920x1080": "1920x1080",
    "1080p": "1920x1080",
    "1280x720": "1280x720",
    "720p": "1280x720",
}

STORAGE = Path("/mnt/usb/camera")
MODULE_DIR = Path(__file__).resolve().parent
