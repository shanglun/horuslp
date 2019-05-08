"""
Utility functions for the library to support some syntax sugar and reporting functionality
"""
import inspect
import pulp as pl
import gurobipy as gr
from horuslp.core.utils import call_with_required_args


def get_constraints_value(constr):
    """
    Gets the final resulting number for the constraint expression so we can see how far we got from the limit.
    :LPAffineExpression constr: The constraint expression
    :returns float: The final resulting number
    """
    return constr._lhs.getValue()

