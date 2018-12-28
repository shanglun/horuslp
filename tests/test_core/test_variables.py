import pulp as pl
import pytest
from unittest.mock import patch, Mock

from horuslp.core import BINARY, INTEGER, CONTINUOUS
from horuslp.core import Variable, VariableGroup, VariableManager, IntegerVariable, IntegerVariableGroup, \
    BinaryVariable, BinaryVariableGroup


def test_variable_class():
    test_variable = Variable('test_name', 'test_lb', 'test_ub', 'test_vartype')
    assert test_variable.var_name == 'test_name'
    assert test_variable.lb == 'test_lb'
    assert test_variable.ub == 'test_ub'
    assert test_variable.var_type == 'test_vartype'


def test_binary_variable_class():
    test_variable = BinaryVariable('test_name')
    assert test_variable.var_name == 'test_name'
    assert test_variable.lb == 0
    assert test_variable.ub == 1
    assert test_variable.var_type == BINARY


def test_integer_variable_class():
    test_variable = IntegerVariable('test_name', -5, 5)
    assert test_variable.var_name == 'test_name'
    assert test_variable.lb == -5
    assert test_variable.ub == 5
    assert test_variable.var_type == INTEGER


def test_variable_group():
    test_variable = VariableGroup('test_name', 'test_keys', 'test_lb', 'test_ub', 'test_vartype')
    assert test_variable.group_name == 'test_name'
    assert test_variable.var_names == 'test_keys'
    assert test_variable.lb == 'test_lb'
    assert test_variable.ub == 'test_ub'
    assert test_variable.var_type == 'test_vartype'


def test_binary_variable_group():
    test_variable = BinaryVariableGroup('test_name', 'test_keys')
    assert test_variable.group_name == 'test_name'
    assert test_variable.var_names == 'test_keys'
    assert test_variable.lb == 0
    assert test_variable.ub == 1
    assert test_variable.var_type == BINARY


def test_integer_variable_group():
    test_variable = IntegerVariableGroup('test_name', 'test_keys', -5, 5)
    assert test_variable.group_name == 'test_name'
    assert test_variable.var_names == 'test_keys'
    assert test_variable.lb == -5
    assert test_variable.ub == 5
    assert test_variable.var_type == INTEGER


def test_var_manager_empty():
    var_mgr = VariableManager()
    var_mgr.define_variables()
    assert var_mgr.variables == {}


def test_var_manager_non_bad_type():
    with pytest.raises(AssertionError):
        class BadVarManager(VariableManager):
            vars = ['bad_type']
        var_mgr = BadVarManager()
        var_mgr.define_variables()


def test_var_manager_variable():
    with patch('core.Variables.pl.LpVariable') as lpv_mock:
        lpv_mock.return_value = 'return_var'
        class VarMgr(VariableManager):
            vars = [Variable('test', 0, 1), BinaryVariable('test2'), IntegerVariable('test3', -1, 2)]
        mgr = VarMgr()
        mgr.define_variables()
        assert lpv_mock.call_count == 3
        assert mgr.variables == {
            'test': 'return_var',
            'test2': 'return_var',
            'test3': 'return_var'
        }
        assert lpv_mock.call_args_list[0][0][0] == 'test'
        assert lpv_mock.call_args_list[0][0][1] == 0
        assert lpv_mock.call_args_list[0][0][2] == 1
        assert lpv_mock.call_args_list[0][0][3] == pl.LpContinuous
        assert lpv_mock.call_args_list[1][0][0] == 'test2'
        assert lpv_mock.call_args_list[1][0][1] == 0
        assert lpv_mock.call_args_list[1][0][2] == 1
        assert lpv_mock.call_args_list[1][0][3] == pl.LpBinary
        assert lpv_mock.call_args_list[2][0][0] == 'test3'
        assert lpv_mock.call_args_list[2][0][1] == -1
        assert lpv_mock.call_args_list[2][0][2] == 2
        assert lpv_mock.call_args_list[2][0][3] == pl.LpInteger


def test_var_manager_vargroup():
    with patch('core.Variables.pl.LpVariable') as lpv_mock:
        lpv_mock.return_value = 'return_var'
        class VarMgr(VariableManager):
            vars = [
                VariableGroup('test', ['ckey1', 'ckey2'], 0, 1),
                BinaryVariableGroup('test2', ['bkey1', 'bkey2']),
                IntegerVariableGroup('test3', ['ikey1', 'ikey2'], -1, 2)
            ]
        mgr = VarMgr()
        mgr.define_variables()
        assert lpv_mock.call_count == 6
        assert 'test' in mgr.variables
        assert len(mgr.variables['test']) == 2
        assert 'ckey1' in mgr.variables['test']
        assert 'ckey2' in mgr.variables['test']
        assert 'test2' in mgr.variables
        assert len(mgr.variables['test2']) == 2
        assert 'bkey1' in mgr.variables['test2']
        assert 'bkey2' in mgr.variables['test2']
        assert 'test3' in mgr.variables
        assert len(mgr.variables['test3']) == 2
        assert 'ikey1' in mgr.variables['test3']
        assert 'ikey2' in mgr.variables['test3']

        assert lpv_mock.call_args_list[0][0][0] == 'test[ckey1]'
        assert lpv_mock.call_args_list[0][0][1] == 0
        assert lpv_mock.call_args_list[0][0][2] == 1
        assert lpv_mock.call_args_list[0][0][3] == pl.LpContinuous
        assert lpv_mock.call_args_list[1][0][0] == 'test[ckey2]'
        assert lpv_mock.call_args_list[1][0][1] == 0
        assert lpv_mock.call_args_list[1][0][2] == 1
        assert lpv_mock.call_args_list[1][0][3] == pl.LpContinuous

        assert lpv_mock.call_args_list[2][0][0] == 'test2[bkey1]'
        assert lpv_mock.call_args_list[2][0][1] == 0
        assert lpv_mock.call_args_list[2][0][2] == 1
        assert lpv_mock.call_args_list[2][0][3] == pl.LpBinary
        assert lpv_mock.call_args_list[3][0][0] == 'test2[bkey2]'
        assert lpv_mock.call_args_list[3][0][1] == 0
        assert lpv_mock.call_args_list[3][0][2] == 1
        assert lpv_mock.call_args_list[3][0][3] == pl.LpBinary

        assert lpv_mock.call_args_list[4][0][0] == 'test3[ikey1]'
        assert lpv_mock.call_args_list[4][0][1] == -1
        assert lpv_mock.call_args_list[4][0][2] == 2
        assert lpv_mock.call_args_list[4][0][3] == pl.LpInteger
        assert lpv_mock.call_args_list[5][0][0] == 'test3[ikey2]'
        assert lpv_mock.call_args_list[5][0][1] == -1
        assert lpv_mock.call_args_list[5][0][2] == 2
        assert lpv_mock.call_args_list[5][0][3] == pl.LpInteger



def test_var_manager_mix():
    with patch('core.Variables.pl.LpVariable') as lpv_mock:
        lpv_mock.return_value = 'return_var'
        class VarMgr(VariableManager):
            vars = [
                VariableGroup('test', ['ckey1', 'ckey2'], 0, 1),
                BinaryVariableGroup('test2', ['bkey1', 'bkey2']),
                IntegerVariableGroup('test3', ['ikey1', 'ikey2'], -1, 2),
                Variable('vtest', 0, 1),
                BinaryVariable('vtest2'),
                IntegerVariable('vtest3', -1, 2)
            ]
        mgr = VarMgr()
        mgr.define_variables()
        assert lpv_mock.call_count == 9
        assert 'test' in mgr.variables
        assert len(mgr.variables['test']) == 2
        assert 'ckey1' in mgr.variables['test']
        assert 'ckey2' in mgr.variables['test']
        assert 'test2' in mgr.variables
        assert len(mgr.variables['test2']) == 2
        assert 'bkey1' in mgr.variables['test2']
        assert 'bkey2' in mgr.variables['test2']
        assert 'test3' in mgr.variables
        assert len(mgr.variables['test3']) == 2
        assert 'ikey1' in mgr.variables['test3']
        assert 'ikey2' in mgr.variables['test3']
        assert 'vtest' in mgr.variables
        assert mgr.variables['vtest'] == 'return_var'
        assert 'vtest2' in mgr.variables
        assert mgr.variables['vtest2'] == 'return_var'
        assert 'vtest3' in mgr.variables
        assert mgr.variables['vtest3'] == 'return_var'

        assert lpv_mock.call_args_list[0][0][0] == 'test[ckey1]'
        assert lpv_mock.call_args_list[0][0][1] == 0
        assert lpv_mock.call_args_list[0][0][2] == 1
        assert lpv_mock.call_args_list[0][0][3] == pl.LpContinuous
        assert lpv_mock.call_args_list[1][0][0] == 'test[ckey2]'
        assert lpv_mock.call_args_list[1][0][1] == 0
        assert lpv_mock.call_args_list[1][0][2] == 1
        assert lpv_mock.call_args_list[1][0][3] == pl.LpContinuous

        assert lpv_mock.call_args_list[2][0][0] == 'test2[bkey1]'
        assert lpv_mock.call_args_list[2][0][1] == 0
        assert lpv_mock.call_args_list[2][0][2] == 1
        assert lpv_mock.call_args_list[2][0][3] == pl.LpBinary
        assert lpv_mock.call_args_list[3][0][0] == 'test2[bkey2]'
        assert lpv_mock.call_args_list[3][0][1] == 0
        assert lpv_mock.call_args_list[3][0][2] == 1
        assert lpv_mock.call_args_list[3][0][3] == pl.LpBinary

        assert lpv_mock.call_args_list[4][0][0] == 'test3[ikey1]'
        assert lpv_mock.call_args_list[4][0][1] == -1
        assert lpv_mock.call_args_list[4][0][2] == 2
        assert lpv_mock.call_args_list[4][0][3] == pl.LpInteger
        assert lpv_mock.call_args_list[5][0][0] == 'test3[ikey2]'
        assert lpv_mock.call_args_list[5][0][1] == -1
        assert lpv_mock.call_args_list[5][0][2] == 2
        assert lpv_mock.call_args_list[5][0][3] == pl.LpInteger

        assert lpv_mock.call_args_list[6][0][0] == 'vtest'
        assert lpv_mock.call_args_list[6][0][1] == 0
        assert lpv_mock.call_args_list[6][0][2] == 1
        assert lpv_mock.call_args_list[6][0][3] == pl.LpContinuous
        assert lpv_mock.call_args_list[7][0][0] == 'vtest2'
        assert lpv_mock.call_args_list[7][0][1] == 0
        assert lpv_mock.call_args_list[7][0][2] == 1
        assert lpv_mock.call_args_list[7][0][3] == pl.LpBinary
        assert lpv_mock.call_args_list[8][0][0] == 'vtest3'
        assert lpv_mock.call_args_list[8][0][1] == -1
        assert lpv_mock.call_args_list[8][0][2] == 2
        assert lpv_mock.call_args_list[8][0][3] == pl.LpInteger


