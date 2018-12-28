import pytest
from unittest.mock import patch, Mock

from horuslp.core.utils import get_constraints_value, call_with_required_args


def test_get_constr_value_null():
    assert get_constraints_value({}) == 0


def test_get_constr_value_iters():
    with patch('horuslp.core.utils.pl.value') as pl_mock:
        test_const = {
            'test_var_1': 1,
            'test_var_2': 2
        }
        pl_mock.return_value = 1
        assert get_constraints_value(test_const) == 3
        assert pl_mock.call_count == 2
        assert pl_mock.call_args_list[0][0][0] == 'test_var_1'
        assert pl_mock.call_args_list[1][0][0] == 'test_var_2'


def test_call_with_required_args_no_varkw():
    with patch('horuslp.core.utils.inspect.getfullargspec') as mock_argspeck:
        mock_ret = Mock()
        mock_ret.varkw = None
        mock_ret.args = ['a', 'b', 'd']
        mock_argspeck.return_value = mock_ret
        arg_list = {'a': 'val_a', 'b': 'val_b', 'c': 'val_c', 'd': 'val_d'}
        callee = Mock()
        callee.return_value = 'call_return'
        retval = call_with_required_args(callee, arg_list)
        assert retval == 'call_return'
        assert callee.call_count == 1
        assert callee.call_args_list[0][1] == {'a': 'val_a', 'b': 'val_b', 'd': 'val_d'}


def test_call_with_required_args_with_varkw():
    with patch('horuslp.core.utils.inspect.getfullargspec') as mock_argspeck:
        mock_ret = Mock()
        mock_ret.varkw = 'kwargs'
        mock_ret.args = ['a', 'b', 'd']
        mock_argspeck.return_value = mock_ret
        arg_list = {'a': 'val_a', 'b': 'val_b', 'c': 'val_c', 'd': 'val_d'}
        callee = Mock()
        callee.return_value = 'call_return'
        retval = call_with_required_args(callee, arg_list)
        assert retval == 'call_return'
        assert callee.call_count == 1
        assert callee.call_args_list[0][1] == {'a': 'val_a', 'b': 'val_b', 'c': 'val_c', 'd': 'val_d'}
