import pytest
from unittest.mock import patch, Mock
from core import ObjectiveComponent, Constraint, Metric, VariableManager, CombinedObjective
from core.Variables import BinaryVariable, IntegerVariable
from core.ProblemClass import Problem
import pulp as pl
from core.constants import MAXIMIZE
from collections import OrderedDict


class TestProblem(Problem):
    objective = ObjectiveComponent
    constraints = []
    variables = VariableManager

def test_prob_no_name():
    prob = TestProblem()
    assert prob.name == 'TestProblem'


def test_prob_initializer():
    obj_initializer_mock = Mock()

    class TestObjective(ObjectiveComponent):
        def __init__(self):
            super(ObjectiveComponent, self).__init__()
            obj_initializer_mock()

    define_vars_mock = Mock()
    varmgr_init_mock = Mock()

    class TestVariables(VariableManager):
        def __init__(self):
            super(TestVariables, self).__init__()
            self.define_variables = define_vars_mock
            varmgr_init_mock()
            self.variables = 'variables_test'

    constraint1_init_mock = Mock()

    class TestConstraint1(Constraint):
        def __init__(self):
            super(TestConstraint1, self).__init__()
            constraint1_init_mock()

    constraint2_init_mock = Mock()

    class TestConstraint2(Constraint):
        def __init__(self):
            super(TestConstraint2, self).__init__()
            constraint2_init_mock()

    class TestProblem(Problem):
        objective = TestObjective
        constraints = [TestConstraint1, TestConstraint2]
        variables = TestVariables

    prob = TestProblem()
    obj_initializer_mock.assert_called()
    define_vars_mock.assert_called()
    varmgr_init_mock.assert_called()
    constraint1_init_mock.assert_called()
    constraint2_init_mock.assert_called()
    assert prob.vars == 'variables_test'
    assert not prob.model_built
    assert prob.state == 0
    assert prob.status is None
    assert prob.prob is None
    assert prob.result_variables == {}
    assert prob.implemented_constraints == {}
    assert prob.constraint_results == {}
    assert len(prob.constraint_objs) == 2
    assert prob.constraint_objs[0].__class__ == TestConstraint1
    assert prob.constraint_objs[1].__class__ == TestConstraint2
    assert prob._flatten_constraints

def test_constraint_flattening():
    constraint1_init_mock = Mock()

    class TestConstraint1(Constraint):
        def __init__(self):
            super(TestConstraint1, self).__init__()
            constraint1_init_mock()

    constraint2_init_mock = Mock()

    class TestConstraint2(Constraint):
        def __init__(self):
            super(TestConstraint2, self).__init__()
            constraint2_init_mock()

    combined_init_mock = Mock()

    class CombinedConstraint(Constraint):
        dependent_constraints = [TestConstraint1, TestConstraint2]

        def __init__(self):
            super(CombinedConstraint, self).__init__()
            combined_init_mock()

    class TestProblem(Problem):
        objective = ObjectiveComponent
        constraints = [CombinedConstraint]
        variables = VariableManager
    prob = TestProblem()
    assert len(prob.constraint_objs) == 1
    assert len(prob.flattened_constraints) == 3
    assert prob.constraint_objs[0].__class__ == CombinedConstraint
    assert prob.flattened_constraints[0].__class__ == CombinedConstraint
    assert prob.flattened_constraints[1].__class__ == TestConstraint1
    assert prob.flattened_constraints[2].__class__ == TestConstraint2
    constraint1_init_mock.assert_called()
    constraint2_init_mock.assert_called()
    combined_init_mock.assert_called()

def test_non_flattening():
    constraint1_init_mock = Mock()

    class TestConstraint1(Constraint):
        def __init__(self):
            super(TestConstraint1, self).__init__()
            constraint1_init_mock()

    constraint2_init_mock = Mock()

    class TestConstraint2(Constraint):
        def __init__(self):
            super(TestConstraint2, self).__init__()
            constraint2_init_mock()

    combined_init_mock = Mock()

    class CombinedConstraint(Constraint):
        dependent_constraints = [TestConstraint1, TestConstraint2]

        def __init__(self):
            super(CombinedConstraint, self).__init__()
            combined_init_mock()

    class TestProblem(Problem):
        objective = ObjectiveComponent
        constraints = [CombinedConstraint]
        variables = VariableManager
        _flatten_constraints = False
    prob = TestProblem()
    assert len(prob.constraint_objs) == 1
    assert len(prob.flattened_constraints) == 1
    assert prob.constraint_objs[0].__class__ == CombinedConstraint
    assert prob.flattened_constraints[0].__class__ == CombinedConstraint
    constraint1_init_mock.assert_not_called()
    constraint2_init_mock.assert_not_called()
    combined_init_mock.assert_called()


def test_implement_constraint():
    with patch('core.ProblemClass.call_with_required_args') as cwra:
        prob = TestProblem()
        prob.vars = 'test_vars'
        lp_prob_mock = ''
        constraint_mock = Mock()
        constraint_mock.name = 'test_constraint_name'
        constraint_mock.define = 'test_define'
        cwra.return_value = 'constraint_def'
        prob.implement_constraint(lp_prob_mock, constraint_mock)
        cwra.assert_called_with('test_define', 'test_vars')
        assert prob.implemented_constraints['test_constraint_name'] == 'constraint_def'


def test_implement_constraints():
    prob = TestProblem()
    implement_constraint_mock = Mock()
    prob.implement_constraint = implement_constraint_mock
    prob.flattened_constraints = ['constr_1', 'constr_2']
    prob.implement_constraints('prob')
    implement_constraint_mock.assert_called()
    implement_constraint_mock.assert_any_call('prob', 'constr_1')
    implement_constraint_mock.assert_any_call('prob', 'constr_2')


def test_implement_objective():
    with patch('core.ProblemClass.call_with_required_args') as cwra:
        cwra.return_value = 'test_cwra_return'
        prob = TestProblem()
        prob.vars = 'vars_test'
        prob.objective_obj = Mock()
        prob.objective_obj.define = 'obj_define'
        prob.implement_objective('')
        cwra.assert_called_once_with('obj_define', 'vars_test')


def test_build_model_already_built():
    with patch('core.ProblemClass.pl.LpProblem') as lpp:
        prob = TestProblem()
        prob.model_built = True
        prob.implement_constraints = Mock()
        prob.implement_objective = Mock()
        prob.build_model()
        prob.implement_constraints.assert_not_called()
        prob.implement_objective.assert_not_called()
        lpp.assert_not_called()
        assert prob.prob is None


def test_build_model_min():
    with patch('core.ProblemClass.pl.LpProblem') as lpp:
        lpp.return_value = 'test_lp_prob'
        prob = TestProblem()
        prob.implement_constraints = Mock()
        prob.implement_objective = Mock()
        prob.build_model()
        lpp.assert_called_once_with('TestProblem', pl.LpMinimize)
        prob.implement_constraints.assert_called_once_with('test_lp_prob')
        prob.implement_objective.assert_called_once_with('test_lp_prob')
        assert prob.model_built
        assert prob.prob == 'test_lp_prob'


def test_build_model_max():
    with patch('core.ProblemClass.pl.LpProblem') as lpp:
        class TestProblem(Problem):
            objective = ObjectiveComponent
            constraints = []
            variables = VariableManager
            name = 'test_name'
            sense = MAXIMIZE

        lpp.return_value = 'test_lp_prob'

        prob = TestProblem()
        prob.implement_constraints = Mock()
        prob.implement_objective = Mock()
        prob.build_model()
        lpp.assert_called_once_with('test_name', pl.LpMaximize)
        prob.implement_constraints.assert_called_once_with('test_lp_prob')
        prob.implement_objective.assert_called_once_with('test_lp_prob')
        assert prob.model_built
        assert prob.prob == 'test_lp_prob'


def test_gulp_problem_not_built():
    class TestProblem(Problem):
        objective = ObjectiveComponent
        constraints = []
        variables = VariableManager

    prob = TestProblem()
    prob.model_built = False
    prob.build_model = Mock()
    prob.prob = 'test_prob'
    model = prob.get_pulp_problem()
    assert model == 'test_prob'
    prob.build_model.assert_called_once()


def test_gulp_problem_built():
    prob = TestProblem()
    prob.model_built = True
    prob.build_model = Mock()
    prob.prob = 'test_prob'
    model = prob.get_pulp_problem()
    assert model == 'test_prob'
    prob.build_model.assert_not_called()


def test_read_results_vargroup():
    with patch('core.ProblemClass.pl.value') as plv:
        plv.return_value = 'plv_ret'
        prob = TestProblem()
        pl_var = Mock()
        pl_var.items = Mock()
        pl_var.items.return_value = [
            ('test_key_1', 'test_val_1'),
            ('test_key_2', 'test_val_2')
        ]
        prob.read_result_var_group('var_name', pl_var)
        plv.assert_any_call('test_val_1')
        plv.assert_any_call('test_val_2')
        pl_var.items.assert_called_once()
        assert prob.result_variables['var_name'] == {
            'test_key_1': 'plv_ret',
            'test_key_2': 'plv_ret'
        }


def test_read_result_vars():
    with patch('core.ProblemClass.pl.value') as plv:
        plv.return_value = 'plv_retval'
        prob = TestProblem()
        prob.vars = Mock()
        prob.vars.items = Mock()
        prob.read_result_var_group = Mock()
        test_var_3 = OrderedDict()
        prob.vars.items.return_value = [
            ('test_name_1', 'test_var_1'),
            ('test_name_2', 'test_var_2'),
            ('test_name_3', test_var_3)
        ]
        prob.read_result_variables()
        prob.vars.items.assert_called_once()
        plv.assert_any_call('test_var_1')
        plv.assert_any_call('test_var_2')
        prob.read_result_var_group.assert_called_with('test_name_3', test_var_3)
        assert prob.result_variables['test_name_1'] == 'plv_retval'
        assert prob.result_variables['test_name_2'] == 'plv_retval'


def test_read_constraint_values():
    with patch('core.ProblemClass.get_constraints_value') as gcv:
        gcv.return_value = 'constraint_value'
        prob = TestProblem()
        prob.implemented_constraints = Mock()
        prob.implemented_constraints.items = Mock()
        prob.implemented_constraints.items.return_value = [
            ('constr_name_1', 'constr_1'),
            ('constr_name_2', True),
            ('constr_name_3', 'constr_3')
        ]
        prob.read_constraint_values()
        gcv.assert_any_call('constr_1')
        gcv.assert_any_call('constr_3')
        prob.implemented_constraints.items.assert_called_once()
        assert prob.constraint_results['constr_name_1'] == 'constraint_value'
        assert prob.constraint_results['constr_name_3'] == 'constraint_value'
        assert 'constr_name_2' not in prob.constraint_results


def test_read_metric_values():
    with patch('core.ProblemClass.call_with_required_args') as cwra:
        class TestMetric1:
            name = 'test1'
            define = 'testd1'

        class TestMetric2:
            name = 'test2'
            define = 'testd2'

        prob = TestProblem()
        prob.metrics = [TestMetric1, TestMetric2]
        prob.result_variables = 'resval'
        cwra.return_value = 'cwra_ret'
        prob.read_metric_values()
        cwra.assert_any_call('testd1', 'resval')
        cwra.assert_any_call('testd2', 'resval')
        assert prob.metrics_results['test1'] == 'cwra_ret'
        assert prob.metrics_results['test2'] == 'cwra_ret'


def test_solve():
    with patch('core.ProblemClass.pl.LpStatus') as stat:
        stat.__getitem__ = Mock()
        stat.__getitem__.return_value = 'stat_ret_val'
        prob = TestProblem()
        prob.build_model = Mock()
        prob.prob = Mock()
        prob.prob.solve = Mock()
        prob.prob.solve.return_value = 'solve_stat'
        prob.read_result_variables = Mock()
        prob.read_constraint_values = Mock()
        prob.read_metric_values = Mock()
        ret = prob.solve(solve_args={'test_arg': 'test_arg_val'})
        assert ret == 'stat_ret_val'
        assert prob.status == 'solve_stat'
        stat.__getitem__.assert_called_once_with('solve_stat')
        prob.build_model.assert_called_once()
        prob.prob.solve.assert_called_once_with(test_arg='test_arg_val')
        prob.read_result_variables.assert_called_once()
        prob.read_constraint_values.assert_called_once()
        prob.read_metric_values.assert_called_once()

#<TODO: Infeasible constraints and infeasible constraint groups tests>
def test_build_subproblem():
    prob = TestProblem()
    prob.variables = Mock()
    prob.variables.return_value = Mock()
    prob.variables.return_value.variables = 'vars'
    prob.sense = 'sense'
    prob.objective = Mock()
    prob.objective.return_value = 'obj_return'
    flatten_boolean = 'flatten_boolean'

    class TestConstraint1(Constraint):
        pass

    class TestConstraint2(Constraint):
        pass

    sub_prob, constr_names = prob.build_subproblem([TestConstraint1(), TestConstraint2()], flatten_boolean)
    assert constr_names == ('TestConstraint1', 'TestConstraint2')
    assert sub_prob.variables == prob.variables
    prob.variables.assert_called_once()
    assert sub_prob.constraints == [TestConstraint1, TestConstraint2]
    assert sub_prob.sense == prob.sense
    assert sub_prob.objective == prob.objective
    assert sub_prob.name == "TestProblem[('TestConstraint1', 'TestConstraint2')]"
    assert sub_prob._flatten_constraints == 'flatten_boolean'
    assert sub_prob.vars == 'vars'


def test_find_infeasible_constraints_no_others():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.flattened_constraints = [constr_1, constr_2]
        cmb.return_value = []
        infeasibles = prob.find_infeasible_constraints()
        prob.build_subproblem.assert_not_called()
        assert infeasibles == [('constr_1_name', 'constr_2_name')]

def test_find_infeasible_constraints_some_others_infeasible():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        sub_prob = Mock()
        sub_prob.solve = Mock()
        sub_prob.solve.return_value = 'Infeasible'
        sub_prob.find_infeasible_constraints = Mock()
        sub_prob.find_infeasible_constraints.return_value = ['infeasible_subp']
        prob.build_subproblem.return_value = (sub_prob, 'constr_names')
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.flattened_constraints = [constr_1, constr_2]
        cmb.return_value = ['subset_1', 'subset_2']
        infeasibles = prob.find_infeasible_constraints()
        prob.build_subproblem.assert_any_call('subset_1', False)
        prob.build_subproblem.assert_any_call('subset_2', False)
        assert infeasibles == [('constr_1_name', 'constr_2_name'),
                               'constr_names', 'infeasible_subp']
        sub_prob.find_infeasible_constraints.assert_called()

def test_find_infeasible_constraints_some_others_optimal():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        sub_prob = Mock()
        sub_prob.solve = Mock()
        sub_prob.solve.return_value = 'Optimal'
        prob.build_subproblem.return_value = (sub_prob, 'constr_names')
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.flattened_constraints = [constr_1, constr_2]
        cmb.return_value = ['subset_1', 'subset_2']
        infeasibles = prob.find_infeasible_constraints()
        prob.build_subproblem.assert_any_call('subset_1', False)
        prob.build_subproblem.assert_any_call('subset_2', False)
        sub_prob.solve.assert_called_once()
        assert infeasibles == [('constr_1_name', 'constr_2_name')]


def test_find_infeasible_constraint_group_no_others():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.constraint_objs = [constr_1, constr_2]
        cmb.return_value = []
        infeasibles = prob.find_infeasible_constraint_groups()
        prob.build_subproblem.assert_not_called()
        assert infeasibles == [('constr_1_name', 'constr_2_name')]

def test_find_infeasible_constraint_group_some_others_infeasible():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        sub_prob = Mock()
        sub_prob.solve = Mock()
        sub_prob.solve.return_value = 'Infeasible'
        sub_prob.find_infeasible_constraint_groups = Mock()
        sub_prob.find_infeasible_constraint_groups.return_value = ['infeasible_subp']
        prob.build_subproblem.return_value = (sub_prob, 'constr_names')
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.constraint_objs = [constr_1, constr_2]
        cmb.return_value = ['subset_1', 'subset_2']
        infeasibles = prob.find_infeasible_constraint_groups()
        prob.build_subproblem.assert_any_call('subset_1', True)
        prob.build_subproblem.assert_any_call('subset_2', True)
        assert infeasibles == [('constr_1_name', 'constr_2_name'),
                               'constr_names', 'infeasible_subp']
        sub_prob.find_infeasible_constraint_groups.assert_called()

def test_find_infeasible_constraint_group_some_others_optimal():
    with patch('core.ProblemClass.itertools.combinations') as cmb:
        prob = TestProblem()
        prob.build_subproblem = Mock()
        sub_prob = Mock()
        sub_prob.solve = Mock()
        sub_prob.solve.return_value = 'Optimal'
        prob.build_subproblem.return_value = (sub_prob, 'constr_names')
        constr_1 = Mock()
        constr_1.name = 'constr_1_name'
        constr_2 = Mock()
        constr_2.name = 'constr_2_name'
        prob.constraint_objs = [constr_1, constr_2]
        cmb.return_value = ['subset_1', 'subset_2']
        infeasibles = prob.find_infeasible_constraint_groups()
        prob.build_subproblem.assert_any_call('subset_1', True)
        prob.build_subproblem.assert_any_call('subset_2', True)
        sub_prob.solve.assert_called_once()
        assert infeasibles == [('constr_1_name', 'constr_2_name')]

def test_find_incompatibility_flatten():
    prob = TestProblem()
    prob.find_infeasible_constraints = Mock()
    prob.find_infeasible_constraint_groups = Mock()
    ret_val = [
        'ab',
        'abc',
        'a',
        'bc'
    ]
    prob.find_infeasible_constraint_groups.return_value = ret_val
    retval = prob.find_incompatibility()
    assert retval == 'a'
    prob.find_infeasible_constraints.assert_not_called()
    prob.find_infeasible_constraint_groups.assert_called_once()


def test_find_incompatibility_no_flatten():
    prob = TestProblem()
    prob.find_infeasible_constraints = Mock()
    prob.find_infeasible_constraint_groups = Mock()
    ret_val = [
        'ab',
        'abc',
        'a',
        'bc'
    ]
    prob.find_infeasible_constraints.return_value = ret_val
    retval = prob.find_incompatibility(True)
    assert retval == 'a'
    prob.find_infeasible_constraints.assert_called_once()
    prob.find_infeasible_constraint_groups.assert_not_called()


def test_find_incompatibility_no_infeasibles():
    prob = TestProblem()
    prob.find_infeasible_constraints = Mock()
    prob.find_infeasible_constraint_groups = Mock()
    ret_val = []
    prob.find_infeasible_constraint_groups.return_value = ret_val
    retval = prob.find_incompatibility(False)
    assert retval is None
    prob.find_infeasible_constraint_groups.assert_called_once()
    prob.find_infeasible_constraints.assert_not_called()


def test_print_result_variables():
    with patch('core.ProblemClass.print') as prnt:
        prob = TestProblem()
        prob.result_variables = Mock()
        prob.result_variables.items = Mock()
        prob.result_variables.items.return_value = [
            ('var_name_1', 'var_val_1'),
            ('var_name_2', {
                'subscript1': 'var_val_2_1',
                'subscript2': 'var_val_2_2'
            })
        ]
        prob.print_result_variables()
        prob.result_variables.items.assert_called_once()
        prnt.assert_any_call('var_name_1', 'var_val_1')
        prnt.assert_any_call('var_name_2[subscript1]', 'var_val_2_1')
        prnt.assert_any_call('var_name_2[subscript2]', 'var_val_2_2')


def test_print_result_objectives():
    with patch('core.ProblemClass.print') as prnt:
        with patch('core.ProblemClass.call_with_required_args') as cwra:
            cwra.return_value = 0.01
            prob = TestProblem()
            prob.objective_obj = Mock()
            prob.objective_obj.name = 'Mock'
            prob.objective_obj.define = 'objective_define'
            prob.result_variables = 'result_variables'
            prob.print_result_objectives()
            prnt.assert_called_once_with('Mock: 0.01')
            cwra.assert_called_once_with('objective_define', 'result_variables')


def test_print_result_objectives_combined_obj():
    with patch('core.ProblemClass.print') as prnt:
        with patch('core.ProblemClass.call_with_required_args') as cwra:
            cwra.return_value = 0.01

            class CombObj(CombinedObjective):
                name = 'CombObj'
                define = 'comb_obj'

            class TestProblem(Problem):
                objective = CombObj
                constraints = []
                variables = VariableManager

            prob = TestProblem()
            prob.objective_obj.define = 'comb_obj_def'
            prob.result_variables = 'result_variables'

            class ObjComp1(ObjectiveComponent):
                define = 'obj1_define_mock'

            class ObjComp2(ObjectiveComponent):
                define = 'obj2_define_mock'

            prob.objective_obj.objectives = [
                (ObjComp1, 2),
                (ObjComp2, 3)
            ]
            prob.print_result_objectives()

            cwra.assert_any_call('obj1_define_mock', 'result_variables')
            cwra.assert_any_call('obj2_define_mock', 'result_variables')
            cwra.assert_any_call('comb_obj_def', 'result_variables')
            prnt.assert_any_call('CombObj: 0.01')
            prnt.assert_any_call('ObjComp1: 0.01 * 2')
            prnt.assert_any_call('ObjComp2: 0.01 * 3')


def test_print_optimal_results():
    prob = TestProblem()
    prob.print_result_variables = Mock()
    prob.print_result_objectives = Mock()
    prob.print_result_constraints = Mock()
    prob.print_result_metrics = Mock()
    prob.print_optimal_results()
    prob.print_result_variables.assert_called_once()
    prob.print_result_objectives.assert_called_once()
    prob.print_result_constraints.assert_called_once()
    prob.print_result_metrics.assert_called_once()


def test_print_infeasible_results():
    with patch('core.ProblemClass.print') as prnt:
        prob = TestProblem()
        prob.find_incompatibility = Mock()
        prob.find_incompatibility.return_value = 'find_incompat_ret'
        prob.print_infeasible_results('deep_infeas_search_boolean')
        prob.find_incompatibility.assert_called_once_with(flatten='deep_infeas_search_boolean')
        prnt.assert_any_call('Finding incompatible constraints...')
        prnt.assert_any_call("Incompatible Constraints:", 'find_incompat_ret')

def test_print_results_optimal():
    with patch('core.ProblemClass.pl.LpStatus') as stat:
        with patch('core.ProblemClass.print') as prnt:
            stat.__getitem__ = Mock()
            stat.__getitem__.return_value = 'Optimal'
            prob = TestProblem()
            prob.status = 'test_status'
            prob.print_optimal_results = Mock()
            prob.print_infeasible_results = Mock()
            prob.print_results()
            stat.__getitem__.assert_called_with('test_status')
            prob.print_optimal_results.assert_called_once()
            prnt.assert_called_with('TestProblem: Optimal')


def test_print_results_infeasible_nofind():
    with patch('core.ProblemClass.pl.LpStatus') as stat:
        with patch('core.ProblemClass.print') as prnt:
            stat.__getitem__ = Mock()
            stat.__getitem__.return_value = 'Infeasible'
            prob = TestProblem()
            prob.status = 'test_status'
            prob.print_optimal_results = Mock()
            prob.print_infeasible_results = Mock()
            prob.print_results()
            stat.__getitem__.assert_called_with('test_status')
            prob.print_optimal_results.assert_not_called()
            prob.print_infeasible_results.assert_not_called()
            prnt.assert_called_with('TestProblem: Infeasible')


def test_print_results_infeasible_find():
    with patch('core.ProblemClass.pl.LpStatus') as stat:
        with patch('core.ProblemClass.print') as prnt:
            stat.__getitem__ = Mock()
            stat.__getitem__.return_value = 'Infeasible'
            prob = TestProblem()
            prob.status = 'test_status'
            prob.print_optimal_results = Mock()
            prob.print_infeasible_results = Mock()
            prob.print_results(True)
            stat.__getitem__.assert_called_with('test_status')
            prob.print_optimal_results.assert_not_called()
            prob.print_infeasible_results.assert_called_once()
            prnt.assert_called_with('TestProblem: Infeasible')


