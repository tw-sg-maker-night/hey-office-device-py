import signal

import time

from hey_office_device_py.exceptions import InputError


class HeyOffice(object):
    def __init__(self, states):
        if len(states) == 0:
            raise InputError('The given states map is empty!')
        self.states = states
        self.current_state = None
        self.transition_context = None
        self.should_continue = True

    def get_state(self, state_name):
        return self.states[state_name]

    def transit_state(self):
        self.current_state = self.get_state(self.transition_context.to_state)
        self.transition_context = self.current_state.activate(self.transition_context)

    def signal_handler(self, signal, frame):
        print('Request to stop!')
        self.should_continue = False

    def allowed_to_continue(self):
        return self.should_continue

    def start(self, initial_context):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.transition_context = initial_context
        while self.allowed_to_continue():
            self.transit_state()


class TransitionContext(object):
    def __init__(self, to_state, data):
        self.to_state = to_state
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
