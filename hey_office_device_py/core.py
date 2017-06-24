from hey_office_device_py.exceptions import InputError


class HeyOffice(object):
    def __init__(self, states):
        if len(states) == 0:
            raise InputError('The given states map is empty!')
        self.states = states
        self.current_state = None
        self.next_state = None
