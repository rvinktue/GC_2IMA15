import time
import gcsolver


def solve_instance(file, shuffle=False):
    start = time.perf_counter()
    print(f"Starting {file}...")
    gcsolver.solve("instances/" + file, shuffle=shuffle)
    print(f"Solved {file} in {time.perf_counter() - start} seconds...")


def solve_cg_challenge():
    from os import listdir
    from multiprocessing import Pool

    with Pool(14) as p:
        p.map(solve_instance, listdir("instances/"))
        p.close()
        p.join()


if __name__ == '__main__':
    # solve_cg_challenge()
    while True:
        solve_instance("rsqrp4637.instance.json", shuffle=True)

