'''
6. Incompatible constraints should be identifiable and pullable
'''

from horuslp.core.Variables import BinaryVariable
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MAXIMIZE


class SizeConstraint(Constraint):
    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 15


class SizeConstraint2(Constraint):
    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 20


class MustHaveItemConstraint(Constraint):
    def define(self, cider):
        return cider >= 1


class IncompatibleConstraint1(Constraint):
    def define(self, camera):
        return camera >= 1


class IncompatibleConstraint2(Constraint):
    def define(self, camera):
        return camera <= 0


class CombinedConstraints1(Constraint):
    dependent_constraints = [SizeConstraint2, IncompatibleConstraint1]


class CombinedConstraints2(Constraint):
    dependent_constraints = [SizeConstraint, IncompatibleConstraint2]


class ValueObjective(ObjectiveComponent):
    def define(self, camera, figurine, cider, horn):
        return 5 * camera + 7 * figurine + 2 * cider + 10 * horn


class KnapsackVariables(VariableManager):
    vars = [
        BinaryVariable('camera'),
        BinaryVariable('figurine'),
        BinaryVariable('cider'),
        BinaryVariable('horn')
    ]


class KnapsackProblem(Problem):
    variables = KnapsackVariables
    objective = ValueObjective
    constraints = [CombinedConstraints1, CombinedConstraints2, MustHaveItemConstraint]
    sense = MAXIMIZE


prob = KnapsackProblem()
prob.solve()
print("===== Basic Print ========")
prob.print_results()
print("===== Basic Infeasibility Search =========")
prob.print_results(find_infeasible=True)
print("===== Now with Deep Infeasibility Search ========")
prob.print_results(find_infeasible=True, deep_infeasibility_search=True)

'''
Output:
===== Basic Infeasibility Search =========
KnapsackProblem: Infeasible
Finding incompatible constraints...
Incompatible Constraints: ('CombinedConstraints1', 'CombinedConstraints2')
===== Now with Deep Infeasibility Search ========
KnapsackProblem: Infeasible
Finding incompatible constraints...
Incompatible Constraints: ('IncompatibleConstraint1', 'IncompatibleConstraint2')
'''
