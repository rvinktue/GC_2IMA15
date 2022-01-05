import time
import gcsolver

def solve_instance(file):
    start = time.perf_counter()
    print(f"Starting {file}...")
    gcsolver.solve("instances/" + file, shuffle=False)
    print(f"Solved {file} in {time.perf_counter() - start} seconds...")

def solve_CG_challenge():

    from os import listdir

    from multiprocessing import Pool

    with Pool(8) as p:
        p.map(solve_instance, listdir("instances/"))
        p.close()
        p.join()

if __name__ == '__main__':
    #counter = 0
    #solve_CG_challenge()
    gcsolver.solve("instances/reecn50133.instance.json", shuffle=False)

'''
INPUT_FILE = "instances/reecn11799.instance.json"  # Name of the input file
#INPUT_FILE = "instances/small.instance.json"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file

import gcsolver
import time
start = time.perf_counter()
print(f"Starting {INPUT_FILE}...")
gcsolver.solve(INPUT_FILE, shuffle=False, verify=True, save_to_file=True)
print(f"Solved {INPUT_FILE} in {time.perf_counter() - start} seconds...")
'''