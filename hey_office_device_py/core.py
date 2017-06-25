from hey_office_device_py.exceptions import InputError


class HeyOffice(object):
    def __init__(self, states):
        if len(states) == 0:
            raise InputError('The given states map is empty!')
        self.states = states
        self.current_state = None
        self.current_context = None
        self.next_state = None
        self.next_context = None

    def set_next_state(self, state_name, context):
        self.next_state = self.states[state_name]
        self.next_context = context

    def transit_state(self):
        self.current_state.deactivate()
        self.next_context['__FSM__'] = self
        self.next_state.activate(self.next_context)
