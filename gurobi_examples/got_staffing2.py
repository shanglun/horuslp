'''
11. Demo for solving something non-trivial
   a. The game of thrones staffing problem
'''
from horuslp_gurobi.core.Variables import BinaryVariableGroup, IntegerVariableGroup
from horuslp_gurobi.core import Constraint, VariableManager, Problem, ObjectiveComponent, CombinedObjective
from horuslp_gurobi.core.constants import MINIMIZE

shift_requirements = [1, 4, 3, 5, 2]  # the number of workers we need to staff for each shift
# the availability and pay rates of each of the employees
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

# the following people can't work together, sadly.
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

# Dothraki Staffing Corp will provide us expensive temp workers
DOTHRAKI_MAX = 10
DOTHRAKI_COST = 45


class StaffingVariables(VariableManager):
    vars = []

    def __init__(self, model):
        # like dependent constraints, we can dynamically define variables in the init function
        super(StaffingVariables, self).__init__(model)
        # regular workers
        varkeys = []
        for employee, availability_info in workers.items():
            for shift in availability_info['availability']:
                varkeys.append((employee, shift))
        self.vars.append(BinaryVariableGroup('employee_shifts', varkeys))
        # dothrakis
        dothraki_keys = [i for i in range(len(shift_requirements))]
        self.vars.append(IntegerVariableGroup('dothraki_workers', dothraki_keys, 0, DOTHRAKI_COST))


class SufficientStaffingConstraint(Constraint):
    # we need to staff people sufficiently
    dependent_constraints = []

    def __init__(self, model):
        super(SufficientStaffingConstraint, self).__init__(model)
        for shift_num, shift_req in enumerate(shift_requirements):
            self.dependent_constraints.append(self.build_shift_constraint(shift_num, shift_req))

    def build_shift_constraint(self, sn, sr):
        class ShiftConstraint(Constraint):
            name = "shift_requirement_%d" % sn

            def define(self, employee_shifts, dothraki_workers):
                variables = [val for key, val in employee_shifts.items() if key[1] == sn]
                variables.append(dothraki_workers[sn])
                return sum(variables) >= sr
        return ShiftConstraint


class PersonalConflictsConstraint(Constraint):
    # some people can't work together
    dependent_constraints = []

    def __init__(self, model):
        super(PersonalConflictsConstraint, self).__init__(model)
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


class LaborStandardsConstraint(Constraint):
    # we can make someone work more than two shifts a day.
    dependent_constraints = []

    def __init__(self, model):
        super(LaborStandardsConstraint, self).__init__(model)
        for worker in workers.keys():
            # we don't need a constraint builder function, but in those circumstances
            # we need to set the needed values as class variables and refer to them
            # via the self keyword due to how python's closure system works
            class LaborConstraint(Constraint):
                # we can't use worker directly!
                wk = worker
                name = "labor_standard_%s" % worker

                def define(self, employee_shifts):
                    # we need to access the worker using self. Change self.wk to worker to see
                    # why we need to do this
                    worker_vars = [var for key, var in employee_shifts.items() if key[0] == self.wk]
                    return sum(worker_vars) <= 2
            self.dependent_constraints.append(LaborConstraint)


class CostObjective(ObjectiveComponent):
    # this is the cost function for all the named workers
    def define(self, employee_shifts, dothraki_workers):
        costs = [
            workers[key[0]]['cost'] * var for key, var in employee_shifts.items()
        ]
        return sum(costs)


class DothrakiCostObjective(ObjectiveComponent):
    # don't forget the Dothrakis
    def define(self, dothraki_workers):
        dothraki_costs = [
            dothraki_workers[sn] * DOTHRAKI_COST for sn in dothraki_workers
        ]
        return sum(dothraki_costs)


class TotalCostObjective(CombinedObjective):
    objectives = [
        (CostObjective, 1),
        (DothrakiCostObjective, 1)
    ]


class StaffingProblem(Problem):
    variables = StaffingVariables
    objective = TotalCostObjective
    constraints = [SufficientStaffingConstraint, PersonalConflictsConstraint, LaborStandardsConstraint]
    sense = MINIMIZE


if __name__ == '__main__':
    prob = StaffingProblem()
    prob.solve()
    prob.print_results()

'''
GotShiftProblem: Optimal
employee_shifts[('Melisandre', 0)] 0.0
employee_shifts[('Melisandre', 1)] 1.0
employee_shifts[('Melisandre', 4)] 1.0
employee_shifts[('Bran', 1)] 0.0
employee_shifts[('Bran', 2)] 1.0
employee_shifts[('Bran', 3)] 1.0
employee_shifts[('Bran', 4)] 0.0
employee_shifts[('Cersei', 2)] 0.0
employee_shifts[('Cersei', 3)] 0.0
employee_shifts[('Daenerys', 3)] 1.0
employee_shifts[('Daenerys', 4)] 0.0
employee_shifts[('Theon', 1)] 1.0
employee_shifts[('Theon', 3)] 1.0
employee_shifts[('Theon', 4)] 0.0
employee_shifts[('Jon', 0)] 0.0
employee_shifts[('Jon', 2)] 1.0
employee_shifts[('Jon', 4)] 0.0
employee_shifts[('Tyrion', 1)] 1.0
employee_shifts[('Tyrion', 3)] 1.0
employee_shifts[('Tyrion', 4)] 0.0
employee_shifts[('Jaime', 1)] 1.0
employee_shifts[('Jaime', 2)] 0.0
employee_shifts[('Jaime', 4)] 1.0
employee_shifts[('Arya', 0)] 1.0
employee_shifts[('Arya', 1)] 0.0
employee_shifts[('Arya', 3)] 1.0
dothraki_workers[0] 0.0
dothraki_workers[1] 0.0
dothraki_workers[2] 1.0
dothraki_workers[3] 0.0
dothraki_workers[4] 0.0
TotalCostObjective: 335.00
CostObjective: 290.00 * 1
DothrakiCostObjective: 45.00 * 1
shift_requirement_0: 1.00
shift_requirement_1: 4.00
shift_requirement_2: 3.00
shift_requirement_3: 5.00
shift_requirement_4: 2.00
Conflict_Arya_Cersei_3: 1.00
Conflict_Daenerys_Jaime_4: 1.00
Conflict_Jon_Cersei_2: 1.00
Conflict_Daenerys_Cersei_3: 1.00
Conflict_Jaime_Cersei_2: 0.00
Conflict_Arya_Jaime_1: 1.00
Conflict_Arya_Melisandre_0: 1.00
Conflict_Arya_Melisandre_1: 1.00
Conflict_Jon_Jaime_2: 1.00
Conflict_Jon_Jaime_4: 1.00
labor_standard_Melisandre: 2.00
labor_standard_Bran: 2.00
labor_standard_Cersei: 0.00
labor_standard_Daenerys: 1.00
labor_standard_Theon: 2.00
labor_standard_Jon: 1.00
labor_standard_Tyrion: 2.00
labor_standard_Jaime: 2.00
labor_standard_Arya: 2.00
'''