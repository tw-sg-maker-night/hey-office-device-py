from unittest.mock import Mock

import pytest

from hey_office_device_py.core import HeyOffice
from hey_office_device_py.exceptions import InputError


class TestHeyOffice(object):
    @pytest.fixture
    def mock_states(self):
        return {'S1': Mock(), 'S2': Mock()}

    @pytest.fixture
    def hey_office(self, mock_states):
        return HeyOffice(mock_states)

    def test_raise_exception_when_states_map_is_empty(self):
        with pytest.raises(InputError):
            HeyOffice({})

    def test_state_map_is_assigned(self, mock_states):
        assert HeyOffice(mock_states).states == mock_states

    def test_default_current_state_is_none(self, hey_office):
        assert hey_office.current_state is None

    def test_default_current_context_is_none(self, hey_office):
        assert hey_office.current_context is None

    def test_default_next_state_is_none(self, hey_office):
        assert hey_office.next_state is None

    def test_default_next_context_is_none(self, hey_office):
        assert hey_office.next_context is None

    def test_set_valid_next_state_and_context(self, mock_states):
        hey_office = HeyOffice(mock_states)
        hey_office.set_next_state('S1', {})
        assert hey_office.next_state == mock_states['S1']
        assert hey_office.next_context == {}

    def test_transit_state(self, hey_office):
        mock_current_state = Mock()
        mock_next_state = Mock()
        mock_context = {}
        hey_office.current_state = mock_current_state
        hey_office.next_state = mock_next_state
        hey_office.next_context = mock_context

        hey_office.transit_state()

        mock_current_state.deactivate.assert_called_once()
        assert mock_context['__FSM__'] == hey_office
        mock_next_state.activate.assert_called_once_with(mock_context)
