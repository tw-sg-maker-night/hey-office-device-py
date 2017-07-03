import pyaudio
import webrtcvad


class AudioRecorder(object):
    def __init__(self):
        self.pyaudio = pyaudio.PyAudio()
        self.format = self.pyaudio.get_format_from_width(width=2)
        self.channels = 1
        self.rate = 16000
        self.chunk = 160
        self.max_frame_count = 500
        self.vad = webrtcvad.Vad()

    def record(self, is_interrupted):
        stream = self.pyaudio.open(format=self.format,
                                   channels=self.channels,
                                   rate=self.rate,
                                   input=True,
                                   frames_per_buffer=self.chunk)
        print("* Recording audio...")
        frames = []
        silence_count = 0

        while len(frames) < self.max_frame_count and not is_interrupted():
            data = stream.read(self.chunk)

            if self.__is_speech(data):
                frames.append(data)
                silence_count = 0
            else:
                silence_count += 1

            print(silence_count)
            if silence_count >= 50:
                break

        print("* done")

        stream.stop_stream()
        stream.close()

        audio = b''.join(frames)

        return audio

    def __is_speech(self, audio_data):
        return self.vad.is_speech(audio_data, self.rate)

    def play_stream(self, audio_stream):
        stream = self.pyaudio.open(format=self.format,
                                   channels=self.channels,
                                   rate=self.rate,
                                   output=True)
        stream.write(audio_stream.read())
        stream.stop_stream()
        stream.close()
