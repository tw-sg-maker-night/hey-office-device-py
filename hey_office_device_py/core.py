import signal

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
        self.current_state.activate(self, self.transition_context)

    def signal_handler(self, signal, frame):
        print('Request to stop!')
        self.should_continue = False

    def start(self, initial_context):
        signal.signal(signal.SIGINT, self.signal_handler)

        self.transition_context = initial_context
        while self.should_continue:
            self.transit_state()
