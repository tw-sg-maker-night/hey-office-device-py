import boto3
import pyaudio
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

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
    contentType='text/plain; charset=utf-8',
    accept='audio/pcm',
    inputStream=b'when is the 186 bus?'
)

print(response['message'])

p = pyaudio.PyAudio()
stream = p.open(format=p.get_format_from_width(width=2), channels=1, rate=16000, output=True)
stream.write(response['audioStream'].read())
stream.stop_stream()
stream.close()
