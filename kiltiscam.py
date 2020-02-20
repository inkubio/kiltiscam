"""
Kiltiscam v1.1

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
from time import sleep, time, strftime
import requests
import config  # Hidden parameters for image uploading to server


def camera_init():
    camera = VideoCapture(0)
    camera.set(CAP_PROP_FRAME_WIDTH, 1920)
    camera.set(CAP_PROP_FRAME_HEIGHT, 1080)
    return camera

def read_gmw90_data():
    """
    Read data saved by another script monitoring climate of kiltis.
    The file where to read data from is defined at config.py

    Returns:
        List of most recent tremperature, CO2 concentration and relative
        humidity measurements.
    """
    measurements = []
    with open("config.gmw90file", "r") as f:
        for i in range(3):
            meas = f.readline()
            measurements.append(meas[:-1]) #removing trailing \n
    return measurements

def create_co2_color(co2_measurement):
    """
    Choose color of CO2 value text based on the value.
    This is done to transform ppm values to more intuitive information.

    Parameters:
        co2_measurement: Amout of co2 in kiltis atmosphere (ppm)
    Returns:
        Tuple of BRG color value (because opencv likes BRG instead of RGB)
    """
    co2 = int(co2_measurement)
    if co2 < 800:
        blue = 200
        green = 200
        red = 200
    elif co2 < 1100:
        blue = int((1-((co2-800)/600))*200)
        green = 200
        red = 200
    elif co2 < 1600:
        blue = 0
        green = int((1-((co2-1100)/600))*200)
        red = 200
    elif co2 < 2600:
        blue = 0
        green = 0
        red = int((1-((co2-1600)/1000))*200)
    else:
        blue = 0
        green = 0
        red = 0
    return (blue, green, red)

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
    meas = read_gmw90_data()

    temp = str("Temp: {}C".format(meas[0]))
    co2 = str("{}ppm".format(meas[1]))
    hum = str("Humidity: {}%".format(meas[2]))

    co2_int = int(meas[1])
    co2color = create_co2_color(co2_int)

    putText(img, strftime("%d.%m.%Y"), (20, 40), FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 1, LINE_AA)
    putText(img, strftime("%H.%M.%S"), (20, 80), FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 1, LINE_AA)
    putText(img, temp, (20, 980), FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 1, LINE_AA)
    putText(img, 'CO2: ', (29, 1020), FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 1, LINE_AA)
    putText(img, co2, (105, 1020), FONT_HERSHEY_DUPLEX, 1, co2color, 1, LINE_AA)
    putText(img, hum, (20, 1060), FONT_HERSHEY_DUPLEX, 1, (200, 200, 200), 1, LINE_AA)

    imwrite("{}".format(filename), img)
    # Uncomment in case of kiltislapses
    # imwrite("/home/maikki/data1/kiltislapse/{}.jpg".format(time()), img)


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
        try:
            now = time()
            get_photo(cam, "kiltahuone.jpg")
            if now - then > 30:
                then = now
                send_photo("kiltahuone.jpg")
            sleep(5)
        except Exception as e:
            with open("err.txt", "a") as f:
                f.write("An error occurred on {}:\n{}\n\n".format(strftime("%H:%M:%S %d.%m.%Y"), e))


if __name__ == "__main__":
    main()
