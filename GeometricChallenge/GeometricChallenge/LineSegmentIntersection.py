import time
import gcsolver


def solve_instance(file, shuffle=True):
    start = time.perf_counter()
    print(f"Starting {file}...")
    gcsolver.solve("instances/" + file, shuffle=shuffle)
    print(f"Solved {file} in {time.perf_counter() - start} seconds...")


def solve_cg_challenge():
    from os import listdir
    from multiprocessing import Pool

    with Pool(8) as p:
        instance_names = listdir("instances/")
        p.map(solve_instance, ["reecn3382.instance.json", "reecn3988.instance.json", "reecn6910.instance.json", "rsqrp4637.instance.json", "rsqrpecn8051.instance.json", "rvisp3499.instance.json"])
        p.close()
        p.join()


if __name__ == '__main__':
    while True:
        solve_cg_challenge()



