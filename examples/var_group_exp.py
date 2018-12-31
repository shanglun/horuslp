'''
2. Solve the knapsack problem using variable group instead of individual variables
'''

from horuslp.core.Variables import BinaryVariableGroup
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, objects):
        return 2 * objects['camera'] + 4 * objects['figurine'] + 7 * objects['cider'] + 10 * objects['horn'] <= 15


class ValueObjective(ObjectiveComponent):
    def define(self, objects):
        return 5 * objects['camera'] + 7 * objects['figurine'] + 2 * objects['cider'] + 10 * objects['horn']


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariableGroup('objects', [
            'camera',
            'figurine',
            'cider',
            'horn'
        ])
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
objects[camera] 0.0
objects[figurine] 1.0
objects[cider] 0.0
objects[horn] 1.0
ValueObjective: 17.00
SizeConstraint: 14.00
{'objects': {'camera': 0.0, 'figuring': 1.0, 'cider': 0.0, 'horn': 1.0}}
'''
