"""
Base classes for defining variables of various types.
"""

import gurobipy as gr
from collections import OrderedDict

from horuslp.core.constants import BINARY, CONTINUOUS, INTEGER
from horuslp.core.Variables import Variable, BinaryVariable, IntegerVariable, VariableGroup, BinaryVariableGroup, \
        IntegerVariableGroup


class VariableManager:
    """
    The variable manager class that contains the variable logic
    """
    vars = None

    def __init__(self, model: gr.Model):
        """
        Initializes the instance specific variables
        """
        self.model = model
        if self.vars is None:
            self.vars = []
        self.variables = {}

    def define_variables(self):
        """
        Defines the variables using pulp and put them into the variables dictionary. Single variables are initialized
        as single variables and put into the variables dictionary, variable groups are defined as ordered dictionary
        and the ordered dictionary is put into the variables dictionary.

        variables = {
            <variable_name>: <variable>,
            <variable_group_name>: {
                <variable_name_1>: <variable>,
                <variable_name_2>: <variable>
            }
        }
        """
        for var in self.vars:
            assert isinstance(var, (Variable, VariableGroup))
            pl_var_type = {BINARY: gr.GRB.BINARY, CONTINUOUS: gr.GRB.CONTINUOUS, INTEGER: gr.GRB.INTEGER}[var.var_type]
            if isinstance(var, Variable):
                lp_var = self.model.addVar(var.lb, var.ub, vtype=pl_var_type, name=var.var_name)
                self.variables[var.var_name] = lp_var
            elif isinstance(var, VariableGroup):
                group = OrderedDict()
                for name in var.var_names:
                    lp_var = self.model.addVar(var.lb, var.ub, vtype=pl_var_type, name='%s[%s]' % (var.group_name, name))
                    group[name] = lp_var
                self.variables[var.group_name] = group
