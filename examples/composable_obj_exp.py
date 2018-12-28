'''
5. Multiple objectives should be easy to define and easy to weigh
'''
from core import Constraint, VariableManager, Problem, Metric, ObjectiveComponent, CombinedObjective
from core.Variables import Variable, BinaryVariable
from core.constants import MAXIMIZE


class DependentConstraint(Constraint):
    def define(self, a):
        return a <= 1


class SizeConstraint(Constraint):
    dependent_constraints = [DependentConstraint]

    def define(self, a, b, c, d):
        return 2 * a + 4 * b + 7 * c + 10 * d <= 15


class ValueObjectiveComponent(ObjectiveComponent):
    def define(self, a, b, c, d):
        return 5 * a + 7 * b + 2 * c + 10 * d


class ILoveAppleFigurineObjectiveComponent(ObjectiveComponent):
    def define(self, b, c):
        return 2 * b + c


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable('a'),
        BinaryVariable('b'),
        BinaryVariable('c'),
        BinaryVariable('d')
    ]


class Combined(CombinedObjective):
    objectives = [
        (ILoveAppleFigurineObjectiveComponent, 2),
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