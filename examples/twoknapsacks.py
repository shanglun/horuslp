'''
9. A slightly more complex problem
'''
import json

from horuslp.core.Variables import BinaryVariableGroup
from horuslp.core import Constraint, VariableManager, Problem, Metric, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE

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
        # call the dependent constraint builder function for every durable item, and
        # push them into dependent constraints.
        dependent_constraints = [self.define_uniqueness_constraint(item) for item in mip_cfg['durable']]
        self.dependent_constraints = dependent_constraints

    def define_uniqueness_constraint(self, item):
        # classes are first-class objects in python, so we can define a class within this function and return it
        class UQConstraint(Constraint):
            # we name the constraint based on the item this is for, so that debugging is easier.
            name = "Uniqueness_%s" % item['name']

            # the define function can access the variables much in the same way as other functions
            def define(self, suitcase_d, bag_d):
                return suitcase_d[item['name']] + bag_d[item['name']] <= 1

        return UQConstraint


class TotalValueObjective(ObjectiveComponent):
    def define(self, suitcase_f, suitcase_d, bag_d):
        fragile_value = sum([suitcase_f[i['name']] * i['weight'] for i in mip_cfg['fragile']])
        durable_value_s = sum([suitcase_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        durable_value_d = sum([bag_d[i['name']] * i['weight'] for i in mip_cfg['durable']])
        return fragile_value + durable_value_s + durable_value_d


class SuitcaseFragileWeightMetric(Metric):
    def define(self, suitcase_f):
        return sum([suitcase_f[i['name']] * i['weight'] for i in mip_cfg['fragile']])


class SuitcaseDurableWeightMetric(Metric):
    def define(self, suitcase_d):
        return sum([suitcase_d[i['name']] * i['weight'] for i in mip_cfg['durable']])


class BagWeightMetric(Metric):
    def define(self, bag_d):
        return sum([bag_d[i['name']] * i['weight'] for i in mip_cfg['durable']])


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    constraints = [SuitcaseCapacityConstraint, BagCapacityConstraint, UniquenessConstraints]
    objective = TotalValueObjective
    metrics = [SuitcaseDurableWeightMetric, SuitcaseFragileWeightMetric, BagWeightMetric]
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
SuitcaseDurableWeightMetric: 0.00
SuitcaseFragileWeightMetric: 15.00
BagWeightMetric: 17.00
'''
