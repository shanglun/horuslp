'''
5. Multiple objectives should be easy to define and easy to weigh
'''
from horuslp.core import Constraint, VariableManager, Problem, Metric, ObjectiveComponent, CombinedObjective
from horuslp.core.constants import MAXIMIZE
from horuslp.core.Variables import Variable, BinaryVariable


class MustHaveItemConstraint(Constraint):
    def define(self, camera):
        return camera >= 1


class SizeConstraint(Constraint):
    dependent_constraints = [MustHaveItemConstraint]

    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 15


class ValueObjectiveComponent(ObjectiveComponent):
    def define(self, camera, figurine, cider, horn):
        return 5 * camera + 7 * figurine + 2 * cider + 10 * horn


class ILoveCiderFigurineObjectiveComponent(ObjectiveComponent):
    def define(self, figurine, cider):
        return figurine + cider


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable('camera'),
        BinaryVariable('figurine'),
        BinaryVariable('cider'),
        BinaryVariable('horn')
    ]


class Combined(CombinedObjective):
    objectives = [
        (ILoveCiderFigurineObjectiveComponent, 2),
        (ValueObjectiveComponent, 1)
    ]


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    objective = Combined
    constraints = [SizeConstraint]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.print_results()

'''
KnapsackProblem: Optimal
a 0.0
b 1.0
c 0.0
d 1.0
Combined: 21.00
ILoveAppleFigurineObjectiveComponent: 2.00 * 2
ValueObjectiveComponent: 17.00 * 1
SizeConstraint: 14.00
DependentConstraint: 0.00
'''