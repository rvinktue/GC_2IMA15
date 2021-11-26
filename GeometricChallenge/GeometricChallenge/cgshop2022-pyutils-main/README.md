# Official Utilities for the CG:SHOP 2022 Challenge

This package provides some utilities for handling instances and solutions for the
*CG:SHOP 2022 Challenge on Minimum Partition into Plane Subgraphs*.
These are the tools that are used by us, the (technical) organizers, to handle our
instances and your solutions.
* Reading and writing instances.
* Reading and writing solutions.
* Verifying solutions for correctness.

The source code can be found [here](https://gitlab.ibr.cs.tu-bs.de/alg/cgshop2022-pyutils).

## Installation

The installation is simple. Clone this repository, change into the folder, and execute
```shell
pip install .
```
This automatically builds the native C++-core (requires g++). There can be linking issues when using conda because conda uses a different clib than your system.

If `pip` does not install the dependencies for you you may also need
```shell
pip install networkx
```

The verification component is implemented in C++ and requires a C++17-capable C++ compiler to be installed.
On Linux and MacOS systems, installing a current version of the default C++ compiler (g++ or clang++) should be sufficient.

## Reading and Writing Instances

Instances can be read as follows.

```python
from cgshop2022utils.io import read_instance

instance = read_instance("path or file object to instance")
```
The instance is a dict of the following format:
```python
{
        "type": "Instance_CGSHOP2022",
        "id": "unique name of instance",
        "meta": dict, # with information on the instance (e.g., the polygon for visibility instances)
        "graph": networkx.Graph, # The instance graph with typing.Tuple[int, int] as vertices.
}
```

Check out the documentation of [networkx](https://networkx.org/documentation/stable/) on how to deal with the graphs.
It is fairly straight forward.
For example:
```python
print("Points:")
for v in graph.nodes:
    print(v)
print("Edges:")
for v,w in graph.edges:
    print(v, "<->", w)
```

Conversely, instance files can also be written to files:
```python
from cgshop2022utils.io import write_instance

write_instance('path_or_stream', graph, 'unique_instance_name', {'some': 'meta', 'info': 1})
```
## Reading and Writing Solutions

Similarly to instances, solutions can be read and written using the `cgshop2022utils.io` package.
```python
from cgshop2022utils.io import read_solution, write_solution

# read a solution; this returns a dict {'instance': 'unique_instance_name', 'num_colors': 42, 'colors': [0, 1, ...]}
# raises ValueError if the file contents do not seem to be a valid solution
some_solution = read_solution('path_or_stream')
#list_of_colors = ... # compute a List[int] of colors such that list_of_colors[i] is the color of edge i in the instance
write_solution('path_or_stream', 'unique_instance_name', list_of_colors)
```

## Verifying a Solution for an Instance

Verifying a coloring can be done using the method `verify_coloring` as follows.

```python
from cgshop2022utils.verify import verify_coloring
from cgshop2022utils.io import read_instance, read_solution

instance = read_instance('some_instance_file')
solution = read_solution('some_solution_for_that_instance') # solution['instance'] should be instance['id']
error, num_colors = verify_coloring(instance, solution['colors'], expected_num_colors=solution['num_colors'])
if error is None:
    # solution is valid and uses exactly num_colors distinct colors
else:
    # solution is invalid. error is a ColoringError object and error.message describes the error
```

The `expected_num_colors` parameter is optional.
It causes the method to return a ColoringError if the coloring uses more colors than `expected_num_colors`.
The first parameter can also be a `networkx` graph as in `instance['graph']`.
If it has an `idx` edge attribute (as the graphs returned by `read_instance` have), that attribute determines the order of edges.
If the graph has no such attribute, the order of edges in `instance.edges` is used.
It is also possible to pass a list of `Tuple[Tuple[int,int], Tuple[int,int]]` or 
`Tuple[int, int, int, int]` as first parameter.
