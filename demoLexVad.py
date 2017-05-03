import snowboydecoder
import sys
import signal
import boto3
import pyaudio
import wave
from os.path import join, dirname
from dotenv import load_dotenv
import webrtcvad

interrupted = False

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

p = pyaudio.PyAudio()

def record_audio():
    FORMAT = p.get_format_from_width(width=2)
    CHANNELS = 1
    RATE = 16000
    CHUNK = 160

    vad = webrtcvad.Vad()

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* Recording audio...")

    frames = []

    keep_going = True
    not_talk_count = 0

    while keep_going:
        data = stream.read(CHUNK)
        frames.append(data)
        if vad.is_speech(data, RATE):
            not_talk_count = 0
        else:
            not_talk_count = not_talk_count + 1
        print(not_talk_count)
        if not_talk_count > 25:
            keep_going = False

    print("* done")

    stream.stop_stream()
    stream.close()

    audio = b''.join(frames)

    return audio

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
