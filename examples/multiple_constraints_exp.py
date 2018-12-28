'''
3. Multiple constraints should be respected
'''

from horuslp.core.Variables import BinaryVariable
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, a, b, c, d):
        return 2 * a + 4 * b + 7 * c + 10 * d <= 15


class MustHaveItemConstraint(Constraint):
    def define(self, a):
        return a >= 1


class ValueObjective(ObjectiveComponent):
    def define(self, a, b, c, d):
        return 5 * a + 7 * b + 2 * c + 10 * d


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable('a'),
        BinaryVariable('b'),
        BinaryVariable('c'),
        BinaryVariable('d')
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
a 1.0
b 0.0
c 0.0
d 1.0
ValueObjective: 15.00
SizeConstraint: 12.00
MustHaveItemConstraint: 1.00
'''