from os.path import join, dirname

import boto3
from dotenv import load_dotenv


class Lex(object):
    def __init__(self, credential_path):
        dotenv_path = join(dirname(__file__), credential_path)
        load_dotenv(dotenv_path)
        self.client = boto3.client('lex-runtime',
                                   region_name='us-east-1')

    def ask(self, audio_stream):
        return self.client.post_content(
            botName='HeyOffice',
            botAlias='$LATEST',
            userId='office',
            contentType='audio/l16; rate=16000; channels=1',
            accept='audio/pcm',
            inputStream=audio_stream)
