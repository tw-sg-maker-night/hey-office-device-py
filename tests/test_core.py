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

    def test_raise_exception_when_list_of_states_is_empty(self):
        with pytest.raises(InputError):
            HeyOffice(())

    def test_state_map_is_assigned(self, mock_states):
        assert HeyOffice(mock_states).states == mock_states

    def test_get_state(self, mock_states):
        assert HeyOffice(mock_states).get_state('S1') == mock_states['S1']

    def test_default_current_state_is_none(self, hey_office):
        assert hey_office.current_state is None

    def test_default_transition_context_is_none(self, hey_office):
        assert hey_office.transition_context is None

    def test_transit_state(self, hey_office):
        mock_context = Mock(to_state='S2', data={})
        hey_office.transition_context = mock_context
        mock_state = hey_office.get_state('S2')
        mock_state.activate = Mock(return_value=Mock(to_state='S3', data={}))

        hey_office.transit_state()

        assert hey_office.current_state == mock_state
        hey_office.current_state.activate.assert_called_once_with(mock_context)
        assert hey_office.transition_context.to_state == 'S3'

    def test_start(self, hey_office):
        hey_office.allowed_to_continue = Mock(side_effect=[True, False])
        hey_office.transit_state = Mock()
        initial_context = Mock()

        hey_office.start(initial_context)

        assert hey_office.transition_context == initial_context
        hey_office.transit_state.assert_called_once()

