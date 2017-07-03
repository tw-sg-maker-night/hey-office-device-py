import signal
import time

import snowboydecoder
from hey_office_device_py.exceptions import InputError


class HeyOffice(object):
    def __init__(self, states):
        if len(states) == 0:
            raise InputError('The given states map is empty!')
        self.states = states
        self.current_state = None
        self.transition_context = None
        self.interrupted = False

    def get_state(self, state_name):
        return self.states[state_name]

    def transit_state(self):
        self.current_state = self.get_state(self.transition_context.to_state)
        self.transition_context.is_interrupted = self.is_interrupted
        self.transition_context = self.current_state.activate(self.transition_context)

    def __on_interrupted(self, signal, frame):
        self.interrupted = True

    def is_interrupted(self):
        return self.interrupted

    def start(self, initial_context):
        signal.signal(signal.SIGINT, self.__on_interrupted)
        print('Press Ctrl+C to exit!')

        self.transition_context = initial_context
        while not self.is_interrupted():
            self.transit_state()

        print('Goodbye!')

class TransitionContext(object):
    def __init__(self, to_state, data):
        self.to_state = to_state
        self.is_interrupted = None
        self.data = data


class Ping(object):
    def activate(self, context):
        print('In Ping State ...')
        time.sleep(1)
        return TransitionContext('PONG', 'data')


class Pong(object):
    def activate(self, context):
        print('In Pong State ...')
        time.sleep(1)
        return TransitionContext('PING', 'data')


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
        return TransitionContext('Idle', 'data')

    def __on_keyword_detected(self):
        self.stop = True

    def __get_interrupt_check(self, is_interrupted):
        return lambda: self.stop or is_interrupted()
