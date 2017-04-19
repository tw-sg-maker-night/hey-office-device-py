import boto3
import pyaudio
import wave
from os.path import join, dirname
from dotenv import load_dotenv

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

    # wf = wave.open("sound.wav", 'wb')
    # wf.setnchannels(CHANNELS)
    # wf.setsampwidth(p.get_sample_size(FORMAT))
    # wf.setframerate(RATE)
    # wf.writeframes(audio)
    # wf.close()

    return audio

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
