import pytest
from unittest.mock import patch, Mock

from horuslp.core.Objective import ObjectiveComponent, CombinedObjective


def test_objective_default_name():
    class TestObjectiveComponent(ObjectiveComponent):
        pass

    obj = TestObjectiveComponent()
    assert obj.name == 'TestObjectiveComponent'


def test_objective_given_name():
    class NamedObjectiveComponent(ObjectiveComponent):
        name = 'test_name'

    obj = NamedObjectiveComponent()
    assert obj.name == 'test_name'


def test_objective_abstractmethod():
    with pytest.raises(NotImplementedError):
        ObjectiveComponent().define()


def test_combined_objective_defaults():
    assert CombinedObjective().define() == 0


def test_combined_objective_collection():
    with patch('horuslp.core.Objective.call_with_required_args') as mock_call:
        mock_call.return_value = 1
        mock_define_1 = Mock()
        mock_define_2 = Mock()

        class TestObjective1(ObjectiveComponent):
            def __init__(self):
                super(TestObjective1, self).__init__()
                self.define = mock_define_1

            def define(self):
                return 0

        class TestObjective2(ObjectiveComponent):
            def __init__(self):
                super(TestObjective2, self).__init__()
                self.define = mock_define_2

            def define(self):
                return 0

        class TestCombinedObj(CombinedObjective):
            objectives = [
                (TestObjective1, 1),
                (TestObjective2, 2)
            ]

        cobj = TestCombinedObj()
        res = cobj.define(test_arg='test_value')
        assert res == 3
        assert mock_call.call_count == 2
        assert mock_call.call_args_list[0][0][1] == {'test_arg': 'test_value'}
        assert mock_call.call_args_list[1][0][1] == {'test_arg': 'test_value'}
        assert mock_call.call_args_list[0][0][0] == mock_define_1
        assert mock_call.call_args_list[1][0][0] == mock_define_2
