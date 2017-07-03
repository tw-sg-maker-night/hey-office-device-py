import sys

from hey_office_device_py.core import HeyOffice, TransitionContext, Idle

hey_office = HeyOffice({'Idle': Idle(sys.argv[1])})
hey_office.start(TransitionContext('Idle', 'data'))
