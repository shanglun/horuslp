'''
Write the MPS
'''
from horuslp_gurobi.core.Variables import BinaryVariable
from horuslp_gurobi.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp_gurobi.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 15


class ValueObjective(ObjectiveComponent):
    def define(self, camera, figurine, cider, horn):
        return 5 * camera + 7 * figurine + 2 * cider + 10 * horn


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable('camera'),
        BinaryVariable('figurine'),
        BinaryVariable('cider'),
        BinaryVariable('horn')
    ]


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    objective = ValueObjective
    constraints = [SizeConstraint]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.model.write('knapsack.mps')
