import pytest
from unittest.mock import patch, Mock

from horuslp_gurobi.core.Constraint import Constraint


def test_constraint_initialization():
    class TestConstraint(Constraint):
        pass
    model_mock = Mock()
    constr = TestConstraint(model_mock)
    assert constr.name == 'TestConstraint'
    assert constr.dependent_constraints == []
    assert constr.define()
    assert constr.model == model_mock


def test_named_constraint():
    class TestConstraint(Constraint):
        name = 'test_name'

    model_mock = Mock()
    constr = TestConstraint(model_mock)
    assert constr.name == 'test_name'
    assert constr.model == model_mock


def test_add_constraint():
    class TestConstraint(Constraint):
        pass

    class DependentConstraint(Constraint):
        pass

    model_mock = Mock()
    constr = TestConstraint(model_mock)

    with pytest.raises(AssertionError):
        constr.add_dependent_constraint('This should fail')
    with pytest.raises(AssertionError):
        constr.add_dependent_constraint('This should fail'.__class__)

    constr.add_dependent_constraint(DependentConstraint)
    assert constr.dependent_constraints == [DependentConstraint]
