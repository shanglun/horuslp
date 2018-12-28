import pytest

from horuslp.core.Constraint import Constraint


def test_constraint_initialization():
    class TestConstraint(Constraint):
        pass

    constr = TestConstraint()
    assert constr.name == 'TestConstraint'
    assert constr.dependent_constraints == []
    assert constr.define()


def test_named_constraint():
    class TestConstraint(Constraint):
        name = 'test_name'

    constr = TestConstraint()
    assert constr.name == 'test_name'


def test_add_constraint():
    class TestConstraint(Constraint):
        pass

    class DependentConstraint(Constraint):
        pass

    constr = TestConstraint()

    with pytest.raises(AssertionError):
        constr.add_dependent_constraint('This should fail')
    with pytest.raises(AssertionError):
        constr.add_dependent_constraint('This should fail'.__class__)

    constr.add_dependent_constraint(DependentConstraint)
    assert constr.dependent_constraints == [DependentConstraint]
