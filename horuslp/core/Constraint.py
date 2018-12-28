"""
Base class for the constraint class
"""

import inspect


class Constraint:
    """
    Base constraint class. Holds some metadata and the definition of the constraint.
    """

    name = None
    dependent_constraints = None

    def __init__(self):
        """
        The initialization for the constraint class. Creates names and initializes the dependent constraint class.
        """
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
