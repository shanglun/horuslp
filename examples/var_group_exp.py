'''
2. Solve the knapsack problem using variable group instead of individual variables
'''

from core import Constraint, VariableManager, Problem, ObjectiveComponent
from core.Variables import BinaryVariableGroup
from core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, objects):
        return 2 * objects[0] + 4 * objects[1] + 7 * objects[2] + 10 * objects[3] <= 15


class ValueObjective(ObjectiveComponent):
    def define(self, objects):
        return 5 * objects[0] + 7 * objects[1] + 2 * objects[2] + 10 * objects[3]


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariableGroup('objects', [i for i in range(4)])
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
objects[0] 0.0
objects[1] 1.0
objects[2] 0.0
objects[3] 1.0
ValueObjective: 17.00
SizeConstraint: 14.00
{'objects': {0: 0.0, 1: 1.0, 2: 0.0, 3: 1.0}}
'''
