'''
3. Multiple constraints should be respected
'''

from horuslp.core.Variables import BinaryVariable
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 15


class MustHaveItemConstraint(Constraint):
    def define(self, camera):
        return camera >= 1


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
    constraints = [
        SizeConstraint,
        MustHaveItemConstraint
    ]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.find_incompatibility()
prob.print_results()

'''
Output:
KnapsackProblem: Optimal
camera 1.0
figurine 0.0
cider 0.0
horn 1.0
ValueObjective: 15.00
SizeConstraint: 12.00
MustHaveItemConstraint: 1.00
'''