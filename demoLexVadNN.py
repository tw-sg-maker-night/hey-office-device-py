import signal
import sys
import io
from os.path import join, dirname

import boto3
import pyaudio
import numpy
from keras.models import load_model
from dotenv import load_dotenv

from hey_office_device_py import snowboydecoder

interrupted = False

dotenv_path = join(dirname(__file__), 'resources/.env')
load_dotenv(dotenv_path)

p = pyaudio.PyAudio()

vad_model = load_model('vad.h5')

def record_audio():
    p = pyaudio.PyAudio()
    FORMAT = p.get_format_from_width(width=2)
    CHANNELS = 1
    RATE = 16000
    CHUNK = 240

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* Recording audio...")

    sound = io.BytesIO()

    keep_going = True
    not_talk_count = 0
    total_count = 0

    while total_count < 250:
        data = stream.read(CHUNK)
        sound.write(data)
        total_count = total_count + 1

        sample = []
        for s in range(0, CHUNK*2, 2):
            p = int.from_bytes(data[s:(s+2)],byteorder='little', signed=True)
            sample.append(p)
        x = numpy.matrix(sample)

        if vad_model.predict(x) > 0.5:
            not_talk_count = 0
        else:
            not_talk_count = not_talk_count + 1
        print(not_talk_count)
        if not_talk_count >= 25:
            break

    print("* done")

    stream.stop_stream()
    stream.close()

    sound.seek(0)

    return sound

def ask_lex():
    sound = record_audio()

    client = boto3.client('lex-runtime',
        region_name='us-east-1'
    )

    response = client.post_content(
        botName='HeyOffice',
        botAlias='$LATEST',
        userId='office',
        contentType='audio/l16; rate=16000; channels=1',
        accept='audio/pcm',
        inputStream=sound
    )

    print(response['message'])
    print(response['dialogState'])


    stream = p.open(format=p.get_format_from_width(width=2), channels=1, rate=16000, output=True)
    stream.write(response['audioStream'].read())
    stream.stop_stream()
    stream.close()

    if response['dialogState'] not in ['Fulfilled', 'Failed']:
        ask_lex()

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]


# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

def callback():
    global stop
    stop = True

def start_snowboy():
    global interrupted
    global stop

    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    stop = False

    should_stop = lambda : stop or interrupted

    # main loop
    detector.start(detected_callback=callback,
                   interrupt_check=should_stop,
                   sleep_time=0.03)
    detector.terminate()

while not interrupted:
    start_snowboy()
    if not interrupted:
        ask_lex()