# Raspberry Pi Camera Functions

This repo contains python modules to do basic things with a camera attached to my 
raspberry pi.

So far:

- `python -m camera.lapse`: take timelapse photos every `N` seconds, save them to a 
  mounted USB drive. Also spins up a flask server showing the latest photo.
- `python -m camera.realtime`: run a real time HTTP server with live images form the camera.
- `python -m camera.lapse2movie`: combine images from `lapse` into a divx encoded .avi file.

Web services are served to port 5000 on `0.0.0.0`, which i access via `<hostname>.local`.