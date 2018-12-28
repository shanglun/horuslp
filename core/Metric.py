"""
Base class for the metrics class.
"""


class Metric:
    name = None

    def __init__(self):
        """
        Initialize the name variable for the metric.
        """
        if self.name is None:
            self.name = self.__class__.__name__

    def define(self, **kwargs):
        """
        The definition for the metric.
        :dictionary kwargs: variable that would be needed by the metric in order to define it. If kwargs are used,
        then all variables will be passed in as a dictionary. If kwargs are not used, then the problem class checks
        for what variables are needed and pass them in

        :LPAffineExpression/float: An expression for the intended metric
        """
        raise NotImplementedError("Metric must be implemented!")
