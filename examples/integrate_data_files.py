'''
7. Demo for defining an LP from data file
'''
import json

from horuslp.core import Constraint, VariableManager, Problem, Metric, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE
from horuslp.core.Variables import Variable, BinaryVariable

JSON = '''
{
  "items": [
    {"name": "camera", "value": 5, "weight": 2},
    {"name": "figurine", "value": 7, "weight": 4},
    {"name": "apple", "value": 2, "weight": 7},
    {"name": "horn", "value": 10, "weight": 10},
    {"name": "banana", "value": 9, "weight": 2}
  ],
  "capacity": 15
}
'''
mip_cfg = json.loads(JSON)


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable(i['name']) for i in mip_cfg['items']
    ]


class CapacityConstraint(Constraint):
    def define(self, **kwargs):
        item_dict = {i['name']: i['weight'] for i in mip_cfg['items']}
        return sum(kwargs[name] * item_dict[name] for name in kwargs) <= mip_cfg['capacity']


class ValueObjective(ObjectiveComponent):
    def define(self, **kwargs):
        item_dict = {i['name']: i['value'] for i in mip_cfg['items']}
        return sum(kwargs[name] * item_dict[name] for name in kwargs)


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    constraints = [CapacityConstraint]
    objective = ValueObjective
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.print_results()

'''
Output:
KnapsackProblem: Optimal
camera 1.0
figurine 0.0
apple 0.0
horn 1.0
banana 1.0
ValueObjective: 24.00
CapacityConstraint: 14.00
'''
