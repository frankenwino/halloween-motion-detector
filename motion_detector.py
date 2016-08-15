#! /usr/bin/env python

"""
Conecting PIR Motion Sensor: https://www.raspberrypi.org/learning/parent-detector/worksheet/
General PIR stuff: http://www.instructables.com/id/PIR-Motion-Sensor-Tutorial/
Controlling mp3: http://www.pygame.org/docs/ref/music.html
"""

import datetime
import multiprocessing
import os
import sqlite3
import sys
from gpiozero import MotionSensor # https://gpiozero.readthedocs.io/en/v1.2.0/api_input.html#motion-sensor-d-sun-pir
from mutagen.mp3 import MP3 # https://mutagen.readthedocs.io/en/latest/
from picamera import PiCamera # https://picamera.readthedocs.io/en/release-1.12/index.html
from pygame import mixer #http://www.pygame.org/docs/ref/music.html
from time import sleep
from random import randint

def create_db():
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS motion(id INTEGER PRIMARY KEY AUTOINCREMENT, \
                        created_at DATETIME DEFAULT (DATETIME(CURRENT_TIMESTAMP, 'LOCALTIME')), \
                        video VARCHAR(255), \
                        mp3 VARCHAR(255), \
                        picture VARCHAR(255))")
    con.commit()
    cur.close()
    con.close()

def current_time():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def current_time_for_filename():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d-%H%M%S")

def get_mp3_length(file_path):
    audio = MP3(file_path)
    return audio.info.length

def randomise_mp3():
    random_sound_index = randint(0, len(sounds_list)-1)
    random_mp3 = sounds_list[random_sound_index]
    duration = get_mp3_length(random_mp3)
    return {"mp3": random_mp3, "duration" : duration}

def play_mp3(mp3_info):
    random_mp3 = mp3_info["mp3"]
    duration = mp3_info["duration"]
    fadeout = int(duration * 1000 - 1000)
    con = sqlite3.connect(db)
    cur = con.cursor()
    cur.execute("INSERT INTO motion (mp3) VALUES(?)", (random_mp3, ))
    con.commit()
    con.close()
    play_music_text = "%s - Motion detected - Playing %s" % (current_time(), random_mp3)
    print(play_music_text)
    mixer.init()
    mixer.music.set_volume(1)
    mixer.music.load(random_mp3)
    mixer.music.play()
    mixer.music.fadeout(fadeout)
    #sleep(duration)

def take_picture():
    image_file = os.path.join(image_folder, "%s.jpg" % current_time_for_filename())
    take_pic_text = "%s - Motion detected - Taking a picture" % (current_time())
    print(take_pic_text)
    with PiCamera() as camera:
        if not os.path.isdir(image_folder):
            os.makedirs(image_folder)
        camera.resolution = (1024, 768)
        camera.start_preview()
        sleep(5)
        camera.capture(image_file)
        finish_pic_text = "%s - Finished taking a picture - %s" % (current_time(), image_file)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("INSERT INTO motion (picture) VALUES(?)", (image_file, ))
        con.commit()
        con.close()
        #camera.stop_preview()
        #sleep(1)

def record_movie(mp3_info):
    duration = mp3_info["duration"]
    record_movie_text = "%s - Motion detected - Recording a movie" % (current_time())
    print(record_movie_text)
    if not os.path.isdir(movie_folder):
        os.makedirs(movie_folder)
    with PiCamera() as camera:
        camera.rotation = 180
        camera.resolution = (1920, 1080)
        movie_file = os.path.join(movie_folder, "%s.h264" % current_time_for_filename())
        camera.start_recording(movie_file)
        camera.wait_recording(duration)
        #pir.wait_for_no_motion()
        camera.stop_recording()
        finish_movie_text = "%s - Finished recording movie - %s" % (current_time(), movie_file)
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("SELECT id FROM motion ORDER BY id DESC LIMIT 1")
        row_id = cur.fetchone()[0]
        cur.execute("UPDATE motion SET video = ? WHERE id = ?", (movie_file, row_id))
        con.commit()
        con.close()

def motion_detected_test():
    motion_detected_text = "%s - Motion detected" % (current_time())
    print(motion_detected_text)
    sleep(sleep_time)

def get_sounds_list():
    sounds_list = []
    for i in os.listdir(mp3_folder):
        if i.endswith(".mp3"):
            sounds_list.append(os.path.join(mp3_folder, i))
    return sounds_list




root_folder = "/home/pi/Documents/Halloween"
log_file = os.path.join(root_folder, "log.txt")
db = os.path.join(root_folder, "log.db")
image_folder = os.path.join(root_folder, "images")
movie_folder = os.path.join(root_folder, "movies")
mp3_folder = os.path.join(root_folder, "mp3")
sounds_list = get_sounds_list()
motion_detected_count = 0
pir = MotionSensor(4)
sleep_time = 60

create_db()
#take_picture()
#sys.exit(0)

while True:
    waiting_for_motion_text = "%s - Waiting for motion" % current_time()
    print(waiting_for_motion_text)
    pir.wait_for_motion(timeout=None)
    motion_detected_count += 1
    #motion_detected_test(motion_detected_count)
    mp3_dict = randomise_mp3()
    jobs = []
    for f in [play_mp3(mp3_dict), record_movie(mp3_dict)]:
        j = multiprocessing.Process(target=f)
        jobs.append(j)
        j.start()
    #play_mp3(motion_detected_count,mp3_dict )
    #take_picture(motion_detected_count)
    #record_movie(motion_detected_count)
    sleeping_text = "%s - Sleeping for %s seconds" % (current_time(), sleep_time)
    print(sleeping_text)
    sleep(sleep_time)
