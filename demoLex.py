import snowboydecoder
import sys
import signal
import boto3
import pyaudio
import wave
from os.path import join, dirname
from dotenv import load_dotenv

interrupted = False

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

p = pyaudio.PyAudio()

def record_audio():
    CHUNK = 1024
    FORMAT = p.get_format_from_width(width=2)
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 3

    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    print("* Recording audio...")

    frames = []

    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("* done")

    stream.stop_stream()
    stream.close()

    audio = b''.join(frames)

    return audio

def ask_lex(detector):
    detector.terminate()
    sound = record_audio()

    client = boto3.client('lex-runtime',
        region_name='us-east-1'
    )

    response = client.post_content(
        botName='HeyOffice',
        botAlias='$LATEST',
        userId='office',
        sessionAttributes={
            'someKey': 'STRING_VALUE',
            'anotherKey': 'ANOTHER_VALUE'
        },
        contentType='audio/l16; rate=16000; channels=1',
        accept='audio/pcm',
        inputStream=sound
    )

    print(response['message'])


    stream = p.open(format=p.get_format_from_width(width=2), channels=1, rate=16000, output=True)
    stream.write(response['audioStream'].read())
    stream.stop_stream()
    stream.close()
    start_snowboy()

def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]


# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)


def start_snowboy():
    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    callback = lambda : ask_lex(detector)

    # main loop
    detector.start(detected_callback=callback,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

start_snowboy()
