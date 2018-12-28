"""
The problem class that manages the main logic for the library
"""

import itertools
import pulp as pl
from collections import OrderedDict
from horuslp.core.Objective import CombinedObjective
from horuslp.core.constants import MAXIMIZE, MINIMIZE

from horuslp.core.utils import get_constraints_value, call_with_required_args


class Problem:
    """
    The main problem class
    """
    name = None
    variables = None
    objective = None
    constraints = None
    metrics = None
    sense = MINIMIZE
    _flatten_constraints = True

    def __init__(self):
        """
        Initialize the problem instance with context variables, and defaults. Also defines the variables and
        flattens the constraints to preprocess for model definition and solution
        """
        self.name = self.__class__.__name__ if self.name is None else self.name
        self.constraints = [] if self.constraints is None else self.constraints
        self.metrics = [] if self.metrics is None else self.metrics
        self.variables_obj = self.variables()
        self.variables_obj.define_variables()
        self.vars = self.variables_obj.variables
        self.objective_obj = self.objective()
        self.model_built = False
        self.state = 0
        self.prob = None
        self.status = None
        self.result_variables = {}
        self.implemented_constraints = {}
        self.constraint_results = {}
        self.metrics_results = {}
        self.constraint_objs = [c() for c in self.constraints]
        if self._flatten_constraints:
            self.flattened_constraints = self.flatten_constraints(self.constraint_objs)
        else:
            self.flattened_constraints = self.constraint_objs

    def flatten_constraints(self, constraint_objs):
        """
        Recursively look into the constraints' dependents to create a flattened list of constraints to implement.
        :list<constraint> constraint_objs: List of initialized constraint objects
        :return: the list of all constraints that need to be implemented for the model
        """
        flat_constraints = []
        for constraint_obj in constraint_objs:
            flat_constraints.append(constraint_obj)
            dependent_objs = [c() for c in constraint_obj.dependent_constraints]
            flat_constraints.extend(self.flatten_constraints(dependent_objs))
        return flat_constraints

    def implement_constraint(self, prob, constraint):
        """
        Implements the constraint and puts them into a context dictionary.

        :LPProblem prob: The Pulp LPProblem instance
        :Constraint constraint: the constraint object to be implemented
        """
        constraint_spec = call_with_required_args(constraint.define, self.vars)

        if constraint_spec is not None:
            self.implemented_constraints[constraint.name] = constraint_spec
            prob += constraint_spec

    def implement_constraints(self, prob):
        """
        Implement all the constraints required for the model.
        :LPProblem prob: the Pulp LPProblem instance
        """
        for constraint in self.flattened_constraints:
            self.implement_constraint(prob, constraint)

    def implement_objective(self, prob):
        """
        Implement the objective for the model.
        :LPProblem prob: the Pulp LPProblem instance
        """
        prob += call_with_required_args(self.objective_obj.define, self.vars)

    def build_model(self):
        """
        Checks if the model has been built, and if negative, build the LPProblem model.
        :return:
        """
        if self.model_built:
            return
        pl_sense = pl.LpMaximize if self.sense == MAXIMIZE else pl.LpMinimize
        prob = pl.LpProblem(self.name, pl_sense)
        self.implement_constraints(prob)
        self.implement_objective(prob)
        self.prob = prob
        self.model_built = True

    def get_pulp_problem(self):
        """
        Returns the LPProblem model for those who want to use lower level APIs.
        """
        if not self.model_built:
            self.build_model()
        return self.prob

    def read_result_var_group(self, var_name, pl_var):
        """
        Take the resulting value of the VariableGroup variables and put them into the result dictionary.
        :string var_name: name of the variable group
        :dictionary<LPVariable> pl_var: dictionary of the LPVariable in the group
        """
        result_dict = {}
        for key, var in pl_var.items():
            result_dict[key] = pl.value(var)
        self.result_variables[var_name] = result_dict

    def read_result_variables(self):
        """
        Read the resulting variables values into the result dictionary. The structure mirrors the variable group
        """
        for var_name, pl_var in self.vars.items():
            if isinstance(pl_var, OrderedDict):
                self.read_result_var_group(var_name, pl_var)
            else:
                self.result_variables[var_name] = pl.value(pl_var)

    def read_constraint_values(self):
        """
        Look through the constraints and calculates the resulting value of the constraints. The resulting values
        are then put into the constraint results dictionary
        """
        for constr_name, constr_expr in self.implemented_constraints.items():
            if constr_expr is True:
                continue
            self.constraint_results[constr_name] = get_constraints_value(constr_expr)

    def read_metric_values(self):
        """
        Look through the constraints and calculates the resulting value of the metrics. The resulting values
        are then put into the metrics results dictionary
        """
        for metric in self.metrics:
            metric_obj = metric()
            self.metrics_results[metric_obj.name] = call_with_required_args(metric_obj.define, self.result_variables)

    def solve(self, solve_args=None):
        """
        Builds the model and calls the LPProblem solve function. The result variables are then read into the result
        data containers.

        :dictionary solve_args: The arguments to pass into the solve function for those who want to access specific
        solvers or other low level API functions

        :returns the status of the model after solve:
        """
        if solve_args is None:
            solve_args = {}
        self.build_model()
        self.status = self.prob.solve(**solve_args)
        self.read_result_variables()
        self.read_constraint_values()
        self.read_metric_values()
        return pl.LpStatus[self.status]

    def build_subproblem(self, constraint_subset, flatten):
        """
        Builds a subproblem for to support searching for the constraint subset that is infeasible
        :tuple<Constraint> constraint_subset: the subset of constraints to build the subproblem out of
        :boolean flatten: whether to flatten the constraints
        :returns SubProblem, tuple<string>: the defined subproblem and the list of constraint names
        """
        constr_names = tuple(constr.name for constr in constraint_subset)

        class SubProblem(Problem):
            variables = self.variables
            constraints = [c.__class__ for c in constraint_subset]
            sense = self.sense
            objective = self.objective
            name = '%s[%s]' % (self.__class__.__name__, str(constr_names))
            _flatten_constraints = flatten

        sub_prob = SubProblem()
        return sub_prob, constr_names

    def find_infeasible_constraints(self, already_done=None):
        """
        Recursively create smaller and smaller subsets of constraints to find the smallest possible combination of
        constraints that causes the infeasibility. This flattens out the constraints and therefore can take quite some
        time

        :set<string> already_done: the set of names that have already been explored for infeasibility
        :returns list<tuple<string>>: subset of the constraints that are infeasible
        """
        if already_done is None:
            already_done = set()
        infeasible_subsets = [tuple(constr.name for constr in self.flattened_constraints)]
        for constraint_subset in itertools.combinations(self.flattened_constraints, len(self.flattened_constraints) - 1):
            sub_prob, constr_names = self.build_subproblem(constraint_subset, False)
            if constr_names in already_done:
                continue
            already_done.add(constr_names)
            if sub_prob.solve() == 'Infeasible':
                infeasible_subsets.append(constr_names)
                infeasible_subsets.extend(sub_prob.find_infeasible_constraints(already_done))
        return infeasible_subsets

    def find_infeasible_constraint_groups(self, already_done=None):
        """
            Recursively create smaller and smaller subsets of constraints to find the smallest possible combination of
            constraints that causes the infeasibility. This looks at the first level only without flattening out the
            constraints, and will be much quicker than find_infeasible_constraints

            :set<string> already_done: the set of names that have already been explored for infeasibility
            :returns list<tuple<string>>: subset of the constraints that are infeasible
            """
        if already_done is None:
            already_done = set()
        infeasible_subsets = [tuple(constr.name for constr in self.constraint_objs)]
        for constraint_subset in itertools.combinations(self.constraint_objs, len(self.constraint_objs) - 1):
            sub_prob, constr_names = self.build_subproblem(constraint_subset, True)
            if constr_names in already_done:
                continue
            already_done.add(constr_names)
            if sub_prob.solve() == 'Infeasible':
                infeasible_subsets.append(constr_names)
                infeasible_subsets.extend(sub_prob.find_infeasible_constraint_groups(already_done))
        return infeasible_subsets

    def find_incompatibility(self, flatten=False):
        """
        Find incompatible constraints that are causing model infeasibility.
        :boolean flatten: Whether to perform a deep search (flatten the constraints first, taking a long time) or a
        shallow search (don't flatten, just find the infeasibility in the constraint groups)
        :return: the smallest subset of constraints that causes infeasibility.
        """
        if flatten:
            infeasible_subsets = self.find_infeasible_constraints()
        else:
            infeasible_subsets = self.find_infeasible_constraint_groups()
        if len(infeasible_subsets) == 0:
            return None
        return sorted(infeasible_subsets, key=lambda x: len(x))[0]

    def print_result_variables(self):
        """
        Print all the result variable by name
        """
        for var_name, pl_var in self.result_variables.items():
            if isinstance(pl_var, dict):
                for var_subscript, var_val in pl_var.items():
                    print('%s[%s]' % (var_name, var_subscript), var_val)
            else:
                print(var_name, pl_var)

    def print_result_objectives(self):
        """
        Print the objectives to stdout. If the objective is a CombinedObjective, print the value and weights for the
        combined objectives as well.
        """
        print("%s: %.2f" % (self.objective_obj.name,
                            call_with_required_args(self.objective_obj.define, self.result_variables)))
        if isinstance(self.objective_obj, CombinedObjective):
            for objective_component_class, weight in self.objective_obj.objectives:
                print("%s: %.2f * %d" % (
                    objective_component_class.__name__,
                    call_with_required_args(objective_component_class().define, self.result_variables),
                    weight
                ))

    def print_result_constraints(self):
        """
        Print the resulting value and name of all the constraints
        """
        for constr_name, constr_val in self.constraint_results.items():
            print('%s: %.2f' % (constr_name, constr_val))

    def print_result_metrics(self):
        """
        Print the name and resulting value of all the metrics.
        """
        for metric_name, metric_value in self.metrics_results.items():
            print("%s: %.2f" % (metric_name, metric_value))

    def print_optimal_results(self):
        """
        Print all the results to stdout
        """
        self.print_result_variables()
        self.print_result_objectives()
        self.print_result_constraints()
        self.print_result_metrics()

    def print_infeasible_results(self, deep_infeasibility_search):
        """
        Finds and prints to stdout the smallest possible combination of constraints that causes infeasibility.
        :boolean deep_infeasibility_search: whether to flatten the constraints and perform a deep search
        """
        print("Finding incompatible constraints...")
        print("Incompatible Constraints:", self.find_incompatibility(flatten=deep_infeasibility_search))

    def print_results(self, find_infeasible=False, deep_infeasibility_search=False):
        """
        Checks if the results are infeasible or optimal. If the results are in infeasible, find the infeasibility.
        If optimal, print the results. If other then just print the status.
        :boolean find_infeasible:
        :boolean deep_infeasibility_search:
        """
        status = pl.LpStatus[self.status]
        print('%s: %s' % (self.name, status))
        if status == 'Optimal':
            self.print_optimal_results()
        elif status == 'Infeasible' and find_infeasible:
            self.print_infeasible_results(deep_infeasibility_search)
