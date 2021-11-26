from cgshop2022utils.verify import verify_coloring
from cgshop2022utils.io import read_instance, read_solution


instance_name = "reecn3382"
instance = read_instance("C:/Users/ruben/source/repos/GeometricChallenge/GeometricChallenge/instances/reecn3382.instance.json")
solution = read_solution("../sol.json")
error, num_colors = verify_coloring(instance, solution['colors'], expected_num_colors=solution['num_colors'])
if error is None:
    print("OK solution")
else:
    print("Wrong solution")
    print(error.message)
