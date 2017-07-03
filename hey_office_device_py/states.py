import snowboydecoder
from hey_office_device_py.audio import AudioRecorder
from hey_office_device_py.service import Lex


class TransitionContext(object):
    def __init__(self, to_state, data):
        self.to_state = to_state
        self.is_interrupted = None
        self.data = data


class Idle(object):
    def __init__(self, model):
        self.model = model
        self.sensitivity = 0.5
        self.sleep_time = 0.03
        self.stop = False

    def activate(self, context):
        self.stop = False
        detector = snowboydecoder.HotwordDetector(self.model, sensitivity=self.sensitivity)
        print('Say "Hey Office" to wake me up...')

        detector.start(detected_callback=self.__on_keyword_detected,
                       interrupt_check=self.__get_interrupt_check(context.is_interrupted),
                       sleep_time=self.sleep_time)
        detector.terminate()
        return TransitionContext('Listening', {})

    def __on_keyword_detected(self):
        self.stop = True

    def __get_interrupt_check(self, is_interrupted):
        return lambda: self.stop or is_interrupted()


class Listening(object):
    def __init__(self):
        self.recorder = AudioRecorder()
        self.lex = Lex('../.env')

    def activate(self, context):
        audio_data = self.recorder.record(context.is_interrupted)
        if not context.is_interrupted():
            response = self.lex.ask(audio_data)
            self.__display_response(response)
            self.recorder.play_stream(response['audioStream'])
            return self.__get_transition_context(response['dialogState'] in ['Fulfilled', 'Failed'])

    @staticmethod
    def __get_transition_context(dialogEnded):
        if dialogEnded:
            return TransitionContext('Idle', {})
        else:
            return TransitionContext('Listening', {})

    @staticmethod
    def __display_response(response):
        print(response['message'])
        print(response['dialogState'])
