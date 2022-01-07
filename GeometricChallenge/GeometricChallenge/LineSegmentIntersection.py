import time
import gcsolver


def solve_instance(file):
    start = time.perf_counter()
    print(f"Starting {file}...")
    gcsolver.solve("instances/" + file, shuffle=True)
    print(f"Solved {file} in {time.perf_counter() - start} seconds...")


def solve_cg_challenge():
    from os import listdir
    from multiprocessing import Pool

    with Pool(8) as p:
        p.map(solve_instance, listdir("instances/"))
        p.close()
        p.join()


if __name__ == '__main__':
    solve_cg_challenge()
