"""
Base classes for definition of objectives
"""

from horuslp.core.utils import call_with_required_args


class CombinedObjective:
    """
    Combined objective class for multiple weighted objectives
    """
    objectives = None
    name = None

    def __init__(self):
        """
        Initialize some context variables
        """
        if self.name is None:
            self.name = self.__class__.__name__
        if self.objectives is None:
            self.objectives = []

    def define(self, **kwargs):
        """
        Defines the combined objective. Called by the problem class to define the final objective expression.
        :param kwargs: all the variables as a dictionary.
        :return: combined objective expression for the problem class
        """
        combined = 0
        for objective, weight in self.objectives:
            combined += weight * call_with_required_args(objective().define, kwargs)
        return combined


class ObjectiveComponent:
    """
    The class for a component of the objective. Can also be used stand-alone if the objective is a single expression.
    """
    name = None

    def __init__(self):
        """
        Initialiaze context variables
        """
        if self.name is None:
            self.name = self.__class__.__name__

    def define(self, **kwargs):
        """
        :dictionary kwargs: variable that would be needed by the objective in order to define it. If kwargs are used,
        then all variables will be passed in as a dictionary. If kwargs are not used, then the problem class checks
        for what variables are needed and pass them in
        :returns LPAffineExpression: The expression for the objective.
        """
        raise NotImplementedError("Objective must be implemented!")
