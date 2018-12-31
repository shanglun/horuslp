'''
11. Demo for solving something non-trivial
   a. The game of thrones staffing problem
'''

from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent
from horuslp.core.constants import MINIMIZE
from horuslp.core.Variables import BinaryVariableGroup

shift_requirements = [1, 4, 3, 5, 2]
workers = {
    "Melisandre": {
        "availability": [0, 1, 4],
        "cost": 20
    },
    "Bran": {
        "availability": [1, 2, 3, 4],
        "cost": 15
    },
    "Cersei": {
        "availability": [2, 3],
        "cost": 35
    },
    "Daenerys": {
        "availability": [3, 4],
        "cost": 35
    },
    "Theon": {
        "availability": [1, 3, 4],
        "cost": 10
    },
    "Jon": {
        "availability": [0, 2, 4],
        "cost": 25
    },
    "Tyrion": {
        "availability": [1, 3, 4],
        "cost": 30
    },
    "Jaime": {
        "availability": [1, 2, 4],
        "cost": 20
    },
    "Arya": {
        "availability": [0, 1, 3],
        "cost": 20
    }
}

ban_list = {
    ("Daenerys", "Jaime"),
    ("Daenerys", "Cersei"),
    ("Jon", "Jaime"),
    ("Jon", "Cersei"),
    ("Arya", "Jaime"),
    ("Arya", "Cersei"),
    ("Arya", "Melisandre"),
    ("Jaime", "Cersei")
}

DOTHRAKI_MAX = 10
DOTHRAKI_COST = 45


class StaffingVariables(VariableManager):
    vars = []

    def __init__(self):
        super(StaffingVariables, self).__init__()
        varkeys = []
        for employee, availability_info in workers.items():
            for shift in availability_info['availability']:
                varkeys.append((employee, shift))
        self.vars.append(BinaryVariableGroup('employee_shifts', varkeys))


class SufficientStaffingConstraint(Constraint):
    dependent_constraints = []

    def __init__(self):
        super(SufficientStaffingConstraint, self).__init__()
        for shift_num, shift_req in enumerate(shift_requirements):
            self.dependent_constraints.append(self.build_shift_constraint(shift_num, shift_req))

    def build_shift_constraint(self, sn, sr):
        class ShiftConstraint(Constraint):
            name = "shift_requirement_%d" % sn

            def define(self, employee_shifts):
                variables = [val for key, val in employee_shifts.items() if key[1] == sn]
                return sum(variables) >= sr
        return ShiftConstraint


class PersonalConflictsConstraint(Constraint):
    dependent_constraints = []

    def __init__(self):
        super(PersonalConflictsConstraint, self).__init__()
        for person_1, person_2 in ban_list:
            for shift in range(len(shift_requirements)):
                self.dependent_constraints.append(self.build_conflict_constraint(person_1, person_2, shift))

    def build_conflict_constraint(self, p1, p2, s):
        class ConflictConstraint(Constraint):
            name = "Conflict_%s_%s_%d" % (p1, p2, s)

            def define(self, employee_shifts):
                if (p1, s) in employee_shifts and (p2, s) in employee_shifts:
                    return employee_shifts[p1, s] + employee_shifts[p2, s] <= 1
                return True
        return ConflictConstraint

class CostObjective(ObjectiveComponent):
    def define(self, employee_shifts):
        costs = [
            workers[key[0]]['cost'] * var for key, var in employee_shifts.items()
        ]
        return sum(costs)


class GotShiftProblem(Problem):
    variables = StaffingVariables
    objective = CostObjective
    constraints = [SufficientStaffingConstraint]
    sense = MINIMIZE


if __name__ == '__main__':
    prob = GotShiftProblem()
    prob.solve()
    prob.print_results()

'''
GotShiftProblem: Optimal
employee_shifts[('Melisandre', 0)] 0.0
employee_shifts[('Melisandre', 1)] 1.0
employee_shifts[('Melisandre', 4)] 0.0
employee_shifts[('Bran', 1)] 1.0
employee_shifts[('Bran', 2)] 1.0
employee_shifts[('Bran', 3)] 1.0
employee_shifts[('Bran', 4)] 1.0
employee_shifts[('Cersei', 2)] 0.0
employee_shifts[('Cersei', 3)] 0.0
employee_shifts[('Daenerys', 3)] 1.0
employee_shifts[('Daenerys', 4)] 0.0
employee_shifts[('Theon', 1)] 1.0
employee_shifts[('Theon', 3)] 1.0
employee_shifts[('Theon', 4)] 1.0
employee_shifts[('Jon', 0)] 0.0
employee_shifts[('Jon', 2)] 1.0
employee_shifts[('Jon', 4)] 0.0
employee_shifts[('Tyrion', 1)] 0.0
employee_shifts[('Tyrion', 3)] 1.0
employee_shifts[('Tyrion', 4)] 0.0
employee_shifts[('Jaime', 1)] 0.0
employee_shifts[('Jaime', 2)] 1.0
employee_shifts[('Jaime', 4)] 0.0
employee_shifts[('Arya', 0)] 1.0
employee_shifts[('Arya', 1)] 1.0
employee_shifts[('Arya', 3)] 1.0
CostObjective: 280.00
shift_requirement_0: 1.00
shift_requirement_1: 4.00
shift_requirement_2: 3.00
shift_requirement_3: 5.00
shift_requirement_4: 2.00
'''