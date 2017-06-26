import time

from hey_office_device_py.core import HeyOffice


class TransitionContext(object):
    def __init__(self, to_state, data):
        self.to_state = to_state
        self.data = data

class Ping(object):
    def activate(self, fsm, context):
        print('In Ping State ...')
        time.sleep(1)
        fsm.transition_context = TransitionContext('PONG', 'data')

class Pong(object):
    def activate(self, fsm, context):
        print('In Pong State ...')
        time.sleep(1)
        fsm.transition_context = TransitionContext('PING', 'data')


hey_office = HeyOffice({'PING': Ping(), 'PONG': Pong()})
hey_office.start(TransitionContext('PING', 'data'))