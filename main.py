import threading
import time

import cv2

import auralizer
import filters
from AudioPlayer import AudioPlayer
from MotionFilter import MotionFilter
from XiaoYiActionCamera import XiaoYiActionCamera

CURRENT_FILTER = "BLUR"


def stream_thread(video_stream, frame, cont):
    while cont[0]:
        video_data = video_stream.read_frame()
        res, boxes = filters.boundingBoxes(video_data)
        for b in boxes:
            cv2.rectangle(video_data, b.coords(), b.ends(), (0, 0, 255), 2)
        cv2.imshow('BLUR', video_data)
        frame[0] = filters.filters[CURRENT_FILTER](video_data)
        cv2.imshow('FILTER', filters.six_colours(frame[0]))
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            cont[0] = False


def auralizer_thread(player, frame, cont):
    prev_frame = frame[0]
    while cont[0]:
        t0 = time.time()
        video_data = frame[0]
        audio_data = auralizer.auralize(video_data, prev_frame)
        print(audio_data)
        player.play_multiple_chords(audio_data)
        prev_frame = video_data
        time.sleep(max(0, DELTA - (time.time() - t0)))


DELTA = 60 / AudioPlayer.BPM

if __name__ == "__main__":
    player = AudioPlayer()

    prev_frame = None
    cont = [True]

    video_stream = XiaoYiActionCamera().open_stream()
    # video_stream = VideoStream(cv2.VideoCapture(0))
    frame = video_stream.read_frame()
    filters.registerMotionFilter(MotionFilter(frame.shape))

    frame = [frame]

    t1 = threading.Thread(target=stream_thread, args=(video_stream, frame, cont))
    t1.start()

    t2 = threading.Thread(target=auralizer_thread, args=(player, frame, cont))
    t2.start()

    t1.join()
    t2.join()

    video_stream.close()

    player.close()
