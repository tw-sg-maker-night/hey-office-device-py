from hey_office_device_py.core import HeyOffice, Ping, Pong, TransitionContext

hey_office = HeyOffice({'PING': Ping(), 'PONG': Pong()})
hey_office.start(TransitionContext('PING', 'data'))
