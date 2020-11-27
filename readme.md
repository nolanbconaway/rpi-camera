# Raspberry Pi Camera Functions

This repo contains python modules to do basic things with a camera attached to my 
raspberry pi.

So far:

- `python -m camera.lapse`: take timelapse photos every `N` seconds, save them to a 
  mounted USB drive.
- `python -m camera.server`: run an HTTP server with live images form the camera
- `python -m camera.lapse2movie`: combine imahes from `lapse` into a divx encoded .avi file.