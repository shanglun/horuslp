'''
1. solve the simple knapsack problem
'''
from horuslp.core.Variables import BinaryVariable
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, a, b, c, d):
        return 2 * a + 4 * b + 7 * c + 10 * d <= 15


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
    constraints = [SizeConstraint]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.print_results()
print(prob.result_variables)

'''
Output:
KnapsackProblem: Optimal
a 0.0
b 1.0
c 0.0
d 1.0
ValueObjective: 17.00
SizeConstraint: 14.00
{'a': 0.0, 'b': 1.0, 'c': 0.0, 'd': 1.0}
'''