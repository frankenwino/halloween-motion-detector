#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Uses a PIR sensor to detect motion.
When motion is detected, an MP3 is played and a video is recorded for as long
as motion is detected.

+----------+
| Hardware |
+----------+
PIR Sensor:
https://www.modmypi.com/electronics/sensors/pir-infrared-motion-sensor-hc-sr501-
Raspberry Pi camera:
https://www.modmypi.com/raspberry-pi/camera/raspberry-pi-camera-board-5mp-1080p-v1.3
USB Speakers:
https://www.modmypi.com/raspberry-pi/accessories/xbmc-media-and-sound/usb-powered-speakers-rpi-compatible/?search=speakers

+-------+
| Notes |
+-------+
Place spooky MP3 files in the mp3 folder.
"""

from gpiozero import MotionSensor  # https://gpiozero.readthedocs.io/en/latest/
from picamera import PiCamera  # https://picamera.readthedocs.io/en/latest/
from pygame import mixer  # http://www.pygame.org/docs/ref/music.html
from random import randint
from datetime import datetime
import multiprocessing
import os
import time


def current_time():
    """Returns datetime in string format."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def video_file_info():
    """Returns dictionary containing video file path and video file name."""
    video_folder = os.path.join(os.getcwd(), "videos")
    if not os.path.isdir(video_folder):
        os.makedirs(video_folder)
    video_file_name = datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")
    video_file_path = os.path.join(video_folder, video_file_name)
    return {"path": video_file_path, "name": video_file_name}


def random_mp3():
    """
    Picks an mp3 at random.
    Returns the mp3 file path.
    """
    mp3_folder = os.path.join(os.getcwd(), "mp3")
    mp3_list = os.listdir(mp3_folder)
    random_sound_index = randint(0, len(mp3_list)-1)
    random_mp3 = mp3_list[random_sound_index]
    return os.path.join(mp3_folder, random_mp3)


def main():
    pir = MotionSensor(4)  # uses Broadcom (BCM) pin numbering for the GPIO pins
    #                        as opposed to physical (BOARD) numbering.
    camera = PiCamera()
    camera.vflip = True
    camera.hflip = True
    mixer.init()
    mixer.music.set_volume(10)
    sleep_time = 15

    try:
        while True:
            mixer.music.load(random_mp3())
            video_file_dict = video_file_info()
            video_file_path = video_file_dict["path"]
            video_file_name = video_file_dict["name"]
            jobs = []
            print("{0} - Waiting for motion.".format(current_time()))
            pir.wait_for_motion()
            print("{0} - Motion detected. Recording video - {1}".format(current_time(), video_file_name))
            for f in [camera.start_recording(video_file_path), mixer.music.play()]:
                j = multiprocessing.Process(target=f)
                jobs.append(j)
                j.start()
            pir.wait_for_no_motion()
            camera.stop_recording()
            print("{0} - Motion stopped. Finished recording video - {1}".format(current_time(), video_file_name))
            print("{0} - Sleeping for {1} seconds".format(current_time(), sleep_time))
            time.sleep(sleep_time)

    except KeyboardInterrupt:
        camera.close()

if __name__ == "__main__":
    main()
