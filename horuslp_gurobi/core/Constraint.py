"""
Base class for the constraint class
"""

import inspect
import gurobipy as gr


def print_genconstr_stats(m: gr.Model, constr: gr.GenConstr):
    stats_str = ''
    if constr.GenConstrType == gr.GRB.GENCONSTR_ABS:
        lhs_var, rhs_var = m.getGenConstrAbs(constr)
        stats_str = f'{lhs_var.x} = |{rhs_var.x}|'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_AND:
        lhs_var, rhs_var = m.getGenConstrAnd(constr)
        stats_str = f'{lhs_var.x} = {" && ".join([str(v.x) for v in rhs_var])}'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_OR:
        lhs_var, rhs_var = m.getGenConstrOr(constr)
        stats_str = f'{lhs_var.x} = {" || ".join([str(v.x) for v in rhs_var])}'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_MAX:
        lhs_var, rhs_var, const_op = m.getGenConstrMax(constr)
        max_strs = [str(v.x) for v in rhs_var]
        if const_op > -gr.GRB.INFINITY:
            max_strs += ['%.2f' % const_op]
        stats_str = f'{lhs_var.x} = max({" && ".join([str(v.x) for v in rhs_var])})'
    elif constr.GenConstrType == gr.GRB.GENCONSTR_MIN:
        lhs_var, rhs_var, const_op = m.getGenConstrMin(constr)
        min_strs = [str(v.x) for v in rhs_var]
        if const_op < gr.GRB.INFINITY:
            min_strs += ['%.2f' % const_op]
        stats_str = f'{lhs_var.x} = min({" && ".join([str(v.x) for v in rhs_var])})'
    return stats_str


class GurobiConstraintFeatures:
    abs_ = gr.abs_
    and_ = gr.and_
    or_ = gr.or_
    min_ = gr.min_
    max_ = gr.max_


class Constraint:
    """
    Base constraint class. Holds some metadata and the definition of the constraint.
    """

    name = None
    dependent_constraints = None
    grb = GurobiConstraintFeatures

    def __init__(self, model: gr.Model):
        """
        The initialization for the constraint class. Creates names and initializes the dependent constraint class.
        """
        self.model = model
        if self.name is None:
            self.name = self.__class__.__name__
        if self.dependent_constraints is None:
            self.dependent_constraints = []

    def define(self, **kwargs):
        """
        The main function for the constraint function.

        :dictionary kwargs: variable that would be needed by the constraint in order to define it. If kwargs are used,
        then all variables will be passed in as a dictionary. If kwargs are not used, then the problem class checks
        for what variables are needed and pass them in

        :returns LPAffineExpression: The constraint expression. If the class is only intended to hold depended
        constraints, then simply return true.
        """
        return True

    def add_dependent_constraint(self, constraint):
        """
        Perform type checking and push the constraint to the dependent class.
        :Constraint(class) constraint: The constraint to add as a dependent constraint.
        """
        assert inspect.isclass(constraint), 'dependent constraint must be a class'
        assert issubclass(constraint, Constraint), 'dependent constraint must be a subclass of Constraint class'
        self.dependent_constraints.append(constraint)


