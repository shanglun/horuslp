# HorusLP

HorusLP is a python framework for architecting linear programming algorithsms.

  - Define optimization models using a simple, declarative API
  - Reporting functionality to speed up development and production monitoring
  - Simple architecture that makes iterative development easy and intuitive

## Getting Started
A tutorial has been published on the [Toptal Blog](https://www.toptal.com/algorithms/horuslp-python-optimization-library). More guides and tutorials will be published here as they are published.

## Core Concepts
HorusLP operates on relatively few core components. The goal of the framework is to provide a small, tightly integrated classes that allows models to be constructed declaratively rather than imperatively.
  - Variable, VariableGroup, and VariableManager
    - These classes provide the foundation for creating variables that are then used by the rest of the classes. Variables can delcared one by one or as a group using VariableGroup.
  - Constraint
    - This class provides away to define and organize constraints. Each constraint has a `define` function that can be implemented.
    - The class can also be used as a container that groups other constraints. Do this by appending to the `dependent_constraints` variable in the `__init__` function. This is useful when you have constraints that only make sense when implemented togather, for example when you use several constraints to impose absolute value relationships between two groups of variables.
  - ObjectiveComponent and CombinedObjective
    - These classes are used to define obejctives. One can either define a simple objective using only ObjectiveComponent or create a multi-part, weighted objective using CombinedObjective.
    - If a problem has objective components that are logically distinct, it is best to use CombinedObjective so that weighin objectives is easier and so that the result value for each ObjectiveComponent will be reported separately.
  - Metric
    - This class provides a utility for defining custom metric that you want to report/automatically calculate. Simply implement the `define` function as if it were an objective component or a constraint.
  - Problem
    - This is the main class of the HorusLP system. Define a problem by delcaring the objectives, constraints, variables, and metrics. The `solve` function will build the problem and solve for you.
    - The `print_results` function automaticlaly print the calculated values of all the constraints, objective components, and metrics. This allows for quick iteration and debugging during development.
    - After the solve, the resulting variables and their values will be held in `result_variables`
## Example
A very simple implmenetation of the knapsack variables can be found below:
```python
from horuslp.core.Variables import BinaryVariable # we will be using binary variables, so we will import the BinaryVariable class, which is a variant of the Variable class
from horuslp.core import Constraint, VariableManager, Problem, ObjectiveComponent # We will also need to import the constraint class, variable manager class, the main problem class, and the objective class to define the objective.
from horuslp.core.constants import MAXIMIZE  # since we're maximizing the resulting value, we want to import this constant

class KnapsackVariables(VariableManager): # define the variables
    vars = [
        BinaryVariable('camera'), # the first argument is the name of the variable
        BinaryVariable('figurine'),
        BinaryVariable('cider'),
        BinaryVariable('horn')
    ]

class SizeConstraint(Constraint): # define the size constraint
    def define(self, camera, figurine, cider, horn):
        return 2 * camera + 4 * figurine + 7 * cider + 10 * horn <= 15

class ValueObjective(ObjectiveComponent): # define the objective
    def define(self, camera, figurine, cider, horn):
        return 5 * camera + 7 * figurine + 2 * cider + 10 * horn

class KnapsackProblem(Problem): # now define the problem
    variables = KnapsackVariables
    objective = ValueObjective
    constraints = [SizeConstraint]
    sense = MAXIMIZE

# instantiate and solve!
prob = KnapsackProblem()
prob.solve()
prob.print_results()
```
Run this code and you should see the below output:
```KnapsackProblem: Optimal
camera 0.0
figurine 1.0
cider 0.0
horn 1.0
ValueObjective: 17.00
SizeConstraint: 14.00
```
## Contributing
HorusLP welcomes suggestions and code contributions! To discuss code related matters, file an issue on GitHub or shoot me an email (available on my GitHub page). If you have code suggestions, feel free issue a PR but please also open an issue explaining what you're trying to accomplish with your PR.

To keep the code in good shape, please make sure all PRs follow PEP8 guidelines as much as possible. If you write a feature, please also be sure to provide unit and integration tests so that we can test it!
## Licensing
My goald is to help as many users and possible. By default, HorusLP is provided under the LGPL. However, if you have needs that conflicts with the license, please drop me a line and we can discuss!

