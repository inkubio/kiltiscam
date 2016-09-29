"""
Kiltiscam v1.0

A script to capture an image from the webcam in the guildroom
of Inkubio. Original script got as an anniversary present from
the Guild of Physics in 2013, written by Lari Koponen, using
http-POST functions by Wade Leftwich and Chris Green.

Rewritten to be ran on inkubaattori.aalto.fi on python 3, using
openCV and requests instead of pygame and httplib on python 2.
Functions structured for easy implementation into kiltisbot.

Author: Joonas Palosuo
Email: joonas.palosuo@gmail.com
Telegram: @jonesus
Date: 29.9.2016
"""


from cv2 import *
from time import sleep, time
import requests
import config  # Hidden parameters for image uploading to server


def camera_init():
    camera = VideoCapture(0)
    camera.set(CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(CAP_PROP_FRAME_HEIGHT, 1080)
    return camera


def shoot(camera):
    """
    Captures a photo from webcam

    Params:
        camera: camera to be used to capture image (cv2.VideoCapture)
    Returns:
        captured image (numpy.ndarray)
    """
    for i in range(6):  # ebin solution to 5 frame buffer problem (c) Salla Autti
        ret, img = camera.read()
    if ret:
        return img
    else:
        raise Exception("Failed to capture image!")


def get_photo(camera, filename):
    """
    Captures and saves a photo from webcam

    Params:
        camera: camera to be used to capture image (cv2.VideoCapture)
        filename: filename for saved image (string)
    Returns:
        nothing
    """
    img = shoot(camera)
    imwrite("{}".format(filename), img)


def send_photo(filename):
    """
    Uploads an image gotten as parameter to www.inkubio.fi/kiltiscam
    The photo is received by upload.php script, which requires
    password authentication and camera id in addition to the
    picture itself. Picture needs to be delivered in byte form.

    Params:
        filename: name of file to upload (string)
    Returns:
        nothing
    """
    args = {"password": config.password, "camera": "0"}
    payload = {"file": (filename, open(filename, "rb").read(), "image/jpeg")}
    r = requests.post(config.url, data=args, files=payload)
    print("HTTP response:", r.text)


def main():
    """
    Main loop, polls for 30sec refresh timeout every 5 seconds and
    then uploads new image
    """
    cam = camera_init()

    then = time()
    while True:
        now = time()
        get_photo(cam, "kiltahuone.jpg")
        if now - then > 30:
            then = now
            send_photo("kiltahuone.jpg")
        sleep(5)


if __name__ == "__main__":
    main()
