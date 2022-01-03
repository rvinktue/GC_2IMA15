def solve_GC_challenge():
    import gcsolver

    from os import listdir
    import time
    for file in listdir("instances/"):
        start = time.perf_counter()
        print(f"Starting {file}...")
        gcsolver.solve("instances/" + file, shuffle=False)
        print(f"Solved {file} in {time.perf_counter() - start} seconds...")


INPUT_FILE = "instances/reecn17244.instance.json"  # Name of the input file
#INPUT_FILE = "instances/small.instance.json"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file

import gcsolver

gcsolver.solve(INPUT_FILE)