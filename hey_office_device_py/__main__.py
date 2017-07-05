import sys

from hey_office_device_py.core import HeyOffice
from hey_office_device_py.states import TransitionContext, Idle, Listening, Processing

hey_office = HeyOffice({
    'Idle': Idle(sys.argv[1]),
    'Listening': Listening(),
    'Processing': Processing()
})
hey_office.start(TransitionContext('Idle', {}))
