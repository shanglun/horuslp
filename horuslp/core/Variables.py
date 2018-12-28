"""
Base classes for defining variables of various types.
"""

import pulp as pl
from collections import OrderedDict

from horuslp.core.constants import BINARY, CONTINUOUS, INTEGER


class Variable:
    """Basic variable definition class. Essentially a data container class"""

    def __init__(self, var_name, lb, ub, var_type=CONTINUOUS):
        """
        Initializes the variable class with the passed in data. Variables are continuous by default
        :string var_name: name of the variable
        :float lb: lower bound
        :float ub: upper bound
        :constant var_type: variable type
        """
        self.var_name = var_name
        self.lb = lb
        self.ub = ub
        self.var_type = var_type


class BinaryVariable(Variable):
    """
    A variable, but of the binary type. Only need to supply the variable name
    """
    def __init__(self, var_name):
        """
        :string var_name: name of the variable
        """
        super(BinaryVariable, self).__init__(var_name, 0, 1, BINARY)


class IntegerVariable(Variable):
    """
    A variable, but of the integer type. Only need to supply the variable name, lower bound, and upper bound
    """
    def __init__(self, var_name, lb, ub):
        """
        :string var_name: name of the variable
        :integer lb: lower bound of the variable
        :integer ub: upper bound of the variable
        """
        super(IntegerVariable, self).__init__(var_name, lb, ub, INTEGER)


class VariableGroup:
    """
    A group of variables. It will be passed into the define functions as a dictionary.
    Functions a data container. The manager class contains the handler logic
    """
    def __init__(self, group_name, var_names, lb, ub, var_type=CONTINUOUS):
        """
        :string group_name: the group's name
        :list<string> var_names: the names of the individual variables in the group
        :float/int lb: lower bound of the variables
        :flat/int ub: upper bound of the variables
        :constant var_type: variable type
        """
        self.group_name = group_name
        self.var_names = var_names
        self.lb = lb
        self.ub = ub
        self.var_type = var_type


class BinaryVariableGroup(VariableGroup):
    """
    A variable group, but specifically Binary Variables
    """
    def __init__(self, group_name, var_names):
        """
        :string group_name: the group's name
        :list<string> var_names: the names of the individual variables in the group
        """
        super(BinaryVariableGroup, self).__init__(group_name, var_names, 0, 1, BINARY)


class IntegerVariableGroup(VariableGroup):
    """
    A variable group, but specifically integer variables
    """
    def __init__(self, group_name, var_names, lb, ub):
        """
        :string group_name: the group's name
        :list<string> var_names: the names of the individual variables in the group
        :float/int lb: lower bound of the variables
        :flat/int ub: upper bound of the variables
        """
        super(IntegerVariableGroup, self).__init__(group_name, var_names, lb, ub, INTEGER)


class VariableManager:
    """
    The variable manager class that contains the variable logic
    """
    vars = None

    def __init__(self):
        """
        Initializes the instance specific variables
        """
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
            pl_var_type = {BINARY: pl.LpBinary, CONTINUOUS: pl.LpContinuous, INTEGER: pl.LpInteger}[var.var_type]
            if isinstance(var, Variable):
                lp_var = pl.LpVariable(var.var_name, var.lb, var.ub, pl_var_type)
                self.variables[var.var_name] = lp_var
            elif isinstance(var, VariableGroup):
                group = OrderedDict()
                for name in var.var_names:
                    lp_var = pl.LpVariable('%s[%s]' % (var.group_name, name), var.lb, var.ub, pl_var_type)
                    group[name] = lp_var
                self.variables[var.group_name] = group
