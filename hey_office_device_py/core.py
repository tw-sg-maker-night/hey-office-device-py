import signal

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
