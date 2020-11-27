"""HTTP server for the camera"""
import argparse
import io
import logging
import socketserver
from http import server
from pathlib import Path
from threading import Condition

import picamera

from camera import config

PAGE = (Path(__file__).resolve().parent / "html/server.html").read_text()


RESOLUTIONS = {
    "640x480": "640x480",
    "480p": "640x480",
    "1920x1080": "1920x1080",
    "1080p": "1920x1080",
    "1280x720": "1280x720",
    "720p": "1280x720",
}


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--rot", dest="rotation", type=int, help="degrees rotation", default=0
    )
    parser.add_argument(
        "--fr", dest="framerate", type=int, help="framerate", default=12
    )
    parser.add_argument(
        "--res",
        dest="resolution",
        type=str,
        choices=tuple(RESOLUTIONS.keys()),
        default="480p",
        help="resolution",
    )
    return parser


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(301)
            self.send_header("Location", "/index.html")
            self.end_headers()
        elif self.path == "/index.html":
            content = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == "/stream.mjpg":
            self.send_response(200)
            self.send_header("Age", 0)
            self.send_header("Cache-Control", "no-cache, private")
            self.send_header("Pragma", "no-cache")
            self.send_header(
                "Content-Type", "multipart/x-mixed-replace; boundary=FRAME"
            )
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b"--FRAME\r\n")
                    self.send_header("Content-Type", "image/jpeg")
                    self.send_header("Content-Length", len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b"\r\n")
            except Exception as e:
                logging.warning(
                    "Removed streaming client %s: %s", self.client_address, str(e)
                )
        else:
            self.send_error(404)
            self.end_headers()


class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    args = make_parser().parse_args()

    with picamera.PiCamera(
        resolution=RESOLUTIONS[args.resolution], framerate=args.framerate
    ) as camera:
        output = StreamingOutput()
        camera.start_recording(output, format="mjpeg")
        camera.rotation = args.rotation
        try:
            address = ("0.0.0.0", 8000)
            http_server = StreamingServer(address, StreamingHandler)
            http_server.serve_forever()
        finally:
            camera.stop_recording()
