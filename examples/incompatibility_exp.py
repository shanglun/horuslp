'''
6. Incompatible constraints should be identifiable and pullable
'''

from horuslp.core.Variables import BinaryVariable
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, a, b, c, d):
        return 2 * a + 4 * b + 7 * c + 10 * d <= 15


class SizeConstraint2(Constraint):
    def define(self, a, b, c, d):
        return 2 * a + 4 * b + 7 * c + 10 * d <= 20


class IncompatibleConstraint1(Constraint):
    def define(self, a):
        return a >= 1


class IncompatibleConstraint2(Constraint):
    def define(self, a):
        return a <= 0


class CombinedConstraints(Constraint):
    dependent_constraints = [SizeConstraint, SizeConstraint2, IncompatibleConstraint1, IncompatibleConstraint2]


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
    # constraints = [SizeConstraint, IncompatibleConstraint1, IncompatibleConstraint2, SizeConstraint2]
    constraints = [CombinedConstraints]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.print_results(True, True)

'''
Output:
KnapsackProblem: Infeasible
Finding incompatible constraints...
Incompatible Constraints: ('IncompatibleConstraint1', 'IncompatibleConstraint2')
'''
