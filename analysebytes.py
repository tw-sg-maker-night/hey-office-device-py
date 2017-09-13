
import pyaudio

p = pyaudio.PyAudio()

FORMAT = p.get_format_from_width(width=2)
CHANNELS = 1
RATE = 16000
CHUNK = 160

stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK)

data = stream.read(CHUNK)

data = stream.read(CHUNK)
stream.stop_stream()
stream.close()

# print("big - unsigned")
# print(int.from_bytes(data[:2],byteorder='big', signed=False))
# print(int.from_bytes(data[2:4],byteorder='big', signed=False))
# print(int.from_bytes(data[4:6],byteorder='big', signed=False))
# print()
# print(int.from_bytes(data[100:102], byteorder='big', signed=False))
# print(int.from_bytes(data[102:104], byteorder='big', signed=False))
# print(int.from_bytes(data[104:106], byteorder='big', signed=False))
# print()
# print("big - signed")
# print(int.from_bytes(data[:2],byteorder='big', signed=True))
# print(int.from_bytes(data[2:4],byteorder='big', signed=True))
# print(int.from_bytes(data[4:6],byteorder='big', signed=True))
# print()
# print(int.from_bytes(data[100:102], byteorder='big', signed=True))
# print(int.from_bytes(data[102:104], byteorder='big', signed=True))
# print(int.from_bytes(data[104:106], byteorder='big', signed=True))
# print()
# print("little - unsigned")
# print(int.from_bytes(data[:2],byteorder='little', signed=False))
# print(int.from_bytes(data[2:4],byteorder='little', signed=False))
# print(int.from_bytes(data[4:6],byteorder='little', signed=False))
# print()
# print(int.from_bytes(data[100:102], byteorder='little', signed=False))
# print(int.from_bytes(data[102:104], byteorder='little', signed=False))
# print(int.from_bytes(data[104:106], byteorder='little', signed=False))
# print()
# print("little - signed")
# print(int.from_bytes(data[:2],byteorder='little', signed=True))
# print(int.from_bytes(data[2:4],byteorder='little', signed=True))
# print(int.from_bytes(data[4:6],byteorder='little', signed=True))
# print()
# print(int.from_bytes(data[100:102], byteorder='little', signed=True))
# print(int.from_bytes(data[102:104], byteorder='little', signed=True))
# print(int.from_bytes(data[104:106], byteorder='little', signed=True))

for x in range(0, len(data), 2):
    print(int.from_bytes(data[x:(x+2)],byteorder='little', signed=True))


print(len(data))

print(data)
