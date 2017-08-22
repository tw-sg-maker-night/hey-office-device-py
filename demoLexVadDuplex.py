try:
    import threading
except ImportError:
    import dummy_threading as threading

import signal
import sys
import io
from os.path import join, dirname

import boto3
import pyaudio
import webrtcvad
from dotenv import load_dotenv

from hey_office_device_py import snowboydecoder

interrupted = False

dotenv_path = join(dirname(__file__), 'resources/.env')
load_dotenv(dotenv_path)

p = pyaudio.PyAudio()


class DuplexBytesIO(io.IOBase):
    """ A file-like API for reading and writing bytes objects.

    Mostly like StringIO, but write() calls modify the underlying
    bytes object.

    >>> b = bytes()
    >>> f = BytesIO(b, 'w')
    >>> f.write(bytes.fromhex('ca fe ba be'))
    >>> f.write(bytes.fromhex('57 41 56 45'))
    >>> b
    bytes([202, 254, 186, 190, 87, 65, 86, 69])
    """

    def __init__(self, buf):
        """ Create a new BytesIO for reading or writing the given buffer.

        buf - Back-end buffer for this BytesIO.  A bytes object.
            Actually, anything that supports len(), slice-assignment,
            and += will work.

        mode - no need for mode, it's intended to be binary read/write by design
        """

        self._buf = bytearray(buf)
        self.ended = False #Finished writing, now read-only
        self._write_point = 0
        self._read_point = len(buf)
        self.lock = threading.Condition()

    def close(self):
        io.IOBase.close(self)
        self.ended = True

    def end(self):
        self.ended = True
        with self.lock:
            self.lock.notify_all()

    def _check_closed(self):
        if self.closed:
            raise ValueError("file is closed")

    def _check_ended(self):
        if self.ended:
            raise ValueError("file cannot be written")

    def read(self, size):
        print("###############")
        print(size)
        self._check_closed()
        with self.lock:
            e = min(self._read_point + size, len(self._buf))

            while e >= self._read_point and not self.ended:
                print("#####")
                print("waiting")
                self.lock.wait()
                e = min(self._read_point + size, len(self._buf))

            r = self._buf[self._read_point:e]
            self._read_point = e
            return r

    def tell(self):
        self._check_closed()
        return self._read_point

    def seek(self, offset, whence=0):
        self._check_closed()

        if whence == 0:
            self._read_point = offset
        elif whence == 1:
            self._read_point += offset
        elif whence == 2:
            self._read_point = len(self._buf) + offset
        else:
            raise ValueError("whence must be 0, 1, or 2")

        if self._read_point < 0:
            self._read_point = 0

    def write(self, data):
        self._check_ended()
        amt = len(data)
        with self.lock:
            size = len(self._buf)

            if self._write_point > size:
                if isinstance(b, bytes):
                    blank = bytes([0])
                else:
                    # Don't know what default value to insert, unfortunately
                    raise ValueError("can't write past the end of this object")
                self._buf += blank * (self._write_point - size) + data
                self._write_point = len(self._buf)
            else:
                p = self._write_point
                self._buf[p:p + amt] = data
                self._write_point = min(p + amt, len(self._buf))

            self.lock.notify_all()

        def __iter__(self):
            return self


class lexThread (threading.Thread):
    def __init__(self, sound):
        threading.Thread.__init__(self)
        self._sound = sound
        self.response = None

    def run(self):
        client = boto3.client('lex-runtime',
            region_name='us-east-1'
        )

        self.response = client.post_content(
            botName='HeyOffice',
            botAlias='$LATEST',
            userId='office',
            contentType='audio/l16; rate=16000; channels=1',
            accept='audio/pcm',
            inputStream=self._sound
        )

        print("Finished calling lex")

def ask_lex():
    sound = DuplexBytesIO(b'')

    lex = lexThread(sound)
    lex.start()

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

    keep_going = True
    not_talk_count = 0
    total_count = 0

    while total_count < 500:
        data = stream.read(CHUNK)
        sound.write(data)
        total_count = total_count + 1
        if vad.is_speech(data, RATE):
            not_talk_count = 0
        else:
            not_talk_count = not_talk_count + 1
        print(not_talk_count)
        if not_talk_count >= 50:
            break

    print("* done")

    stream.close()
    sound.end()

    lex.join()

    response = lex.response

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

#while not interrupted:
#    start_snowboy()
#    if not interrupted:
#        ask_lex()
ask_lex()
