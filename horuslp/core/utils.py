"""
Utility functions for the library to support some syntax sugar and reporting functionality
"""
import inspect
import pulp as pl


def get_constraints_value(constr):
    """
    Gets the final resulting number for the constraint expression so we can see how far we got from the limit.
    :LPAffineExpression constr: The constraint expression
    :returns float: The final resulting number
    """
    final_sum = 0
    for var, weight in constr.items():
        final_sum += pl.value(var) * weight
    return final_sum


def call_with_required_args(func, arg_dict):
    """
    Checks which arguments are needed by a given function and calls with only the required arguments in the args dict
    If kwargs is present in the function, then all of the arguments are passed in.

    :function func: The function to be called
    :dictionary arg_dict: The dictionary from which the arguments are taken
    :returns: The result of invoking the function with the required arguments.
    """
    required = inspect.getfullargspec(func)
    if required.varkw is None:
        required_args = {k: v for k, v in arg_dict.items() if k in required.args}
    else:
        required_args = arg_dict
    return func(**required_args)
