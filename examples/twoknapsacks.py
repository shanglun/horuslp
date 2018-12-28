'''
9. Sometimes it might make to have people develop different variable managers that support separate objectives
and constraints. Can be useful if we have "raw" variables and variables that come from combinations of raw variables,
for instance
'''
from core import Constraint, VariableManager, Problem, Metric, ObjectiveComponent
from core.Variables import BinaryVariableGroup
from core.constants import MAXIMIZE
import json

JSON = '''
{
  "fragile": [
    {"name": "camera", "value": 5, "weight": 2},
    {"name": "glasses", "value": 3, "weight": 4},
    {"name": "apple", "value": 2, "weight": 7},
    {"name": "pear", "value": 5, "weight": 3},
    {"name": "banana", "value": 9, "weight": 2}
  ],
  "durable": [
    {"name": "figurine", "value": 7, "weight": 4},
    {"name": "horn", "value": 10, "weight": 10},
    {"name": "leatherman", "value": 10, "weight": 3}
  ],
  "suitcase_capacity": 15,
  "bag_capacity": 20
}
'''
mip_cfg = json.loads(JSON)


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariableGroup('suitcase_f', [i['name'] for i in mip_cfg['fragile']]),
        BinaryVariableGroup('suitcase_d', [i['name'] for i in mip_cfg['durable']]),
        BinaryVariableGroup('bag_d', [i['name'] for i in mip_cfg['durable']])
    ]


class SuitcaseCapacityConstraint(Constraint):
    def define(self, suitcase_d, suitcase_f):
        fragile_weight = sum([suitcase_f[i['name']] * i['weight'] for i in mip_cfg['fragile']])
        durable_weight = sum([suitcase_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        return fragile_weight + durable_weight <= mip_cfg['suitcase_capacity']


class BagCapacityConstraint(Constraint):
    def define(self, bag_d):
        durable_weight = sum([bag_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        return durable_weight <= mip_cfg['bag_capacity']


class UniquenessConstraints(Constraint):
    def __init__(self):
        super(UniquenessConstraints, self).__init__()
        dependent_constraints = [self.define_uniqueness_constraint(item) for item in mip_cfg['durable']]
        self.dependent_constraints = dependent_constraints

    def define_uniqueness_constraint(self, item):
        class UQConstraint(Constraint):
            name = "Uniqueness_%s" % item['name']

            def define(self, suitcase_d, bag_d):
                return suitcase_d[item['name']] + bag_d[item['name']] <= 1

        return UQConstraint


class TotalValueObjective(ObjectiveComponent):
    def define(self, suitcase_f, suitcase_d, bag_d):
        fragile_value = sum([suitcase_f[i['name']] * i['weight'] for i in mip_cfg['fragile']])
        durable_value_s = sum([suitcase_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        durable_value_d = sum([bag_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        return fragile_value + durable_value_s + durable_value_d


class SuitcaseFragileValueMetric(Metric):
    def define(self, suitcase_f):
        return sum([suitcase_f[i['name']] * i['weight'] for i in mip_cfg['fragile']])


class SuitcaseDurableValueMetric(Metric):
    def define(self, suitcase_d):
        return sum([suitcase_d[i['name']] * i['weight'] for i in mip_cfg['durable']])


class BagValueMetric(Metric):
    def define(self, bag_d):
        return sum([bag_d[i['name']] * i['weight'] for i in mip_cfg['durable']])


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    constraints = [SuitcaseCapacityConstraint, BagCapacityConstraint, UniquenessConstraints]
    objective = TotalValueObjective
    metrics = [SuitcaseDurableValueMetric, SuitcaseFragileValueMetric, BagValueMetric]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
prob.print_results()

'''
KnapsackProblem: Optimal
suitcase_f[camera] 1.0
suitcase_f[glasses] 1.0
suitcase_f[apple] 1.0
suitcase_f[pear] 0.0
suitcase_f[banana] 1.0
suitcase_d[figurine] 0.0
suitcase_d[horn] 0.0
suitcase_d[leatherman] 0.0
bag_d[figurine] 1.0
bag_d[horn] 1.0
bag_d[leatherman] 1.0
TotalValueObjective: 32.00
SuitcaseCapacityConstraint: 15.00
BagCapacityConstraint: 17.00
Uniqueness_figurine: 1.00
Uniqueness_horn: 1.00
Uniqueness_leatherman: 1.00
SuitcaseDurableValueMetric: 0.00
SuitcaseFragileValueMetric: 15.00
BagValueMetric: 17.00
'''
