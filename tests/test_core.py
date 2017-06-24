from unittest.mock import Mock

import pytest

from hey_office_device_py.core import HeyOffice
from hey_office_device_py.exceptions import InputError


class TestHeyOffice(object):
    @pytest.fixture
    def mock_states(self):
        return {'S1': Mock(), 'S2': Mock()}

    def test_raise_exception_when_states_map_is_empty(self):
        with pytest.raises(InputError):
            HeyOffice({})

    def test_state_map_is_assigned(self, mock_states):
        assert HeyOffice(mock_states).states == mock_states

    def test_default_current_state_is_none(self, mock_states):
        assert HeyOffice(mock_states).current_state is None

    def test_default_current_context_is_none(self, mock_states):
        assert HeyOffice(mock_states).current_context is None

    def test_default_next_state_is_none(self, mock_states):
        assert HeyOffice(mock_states).next_state is None

    def test_default_next_context_is_none(self, mock_states):
        assert HeyOffice(mock_states).next_context is None
