from cgshop2022utils.io import read_instance  # Provided by the challenge

import segment
import vertex
import json


class SolutionCheck:
    def __init__(self, name, g, colors):
        self.g = g
        self.colors = colors
        self.subsets = []
        self.errors = []
        self.edges = list(g.edges)
        self.setup()
        self.check()
        self.name = name
        self.is_correct = all([len(error) == 0 for error in self.errors])
        print(f"Done checking {name}")

    def report_errors(self):
        print(f"Errors in {self.name}:")
        for (subsetnr, subset) in enumerate(self.errors):
            if len(subset) > 0:
                print(f"  {len(subset)} unexpected intersections in subset {subsetnr} with {len(self.subsets[subsetnr])} segments:")
                for seg1, seg2 in subset:
                    print(f"    Segment {seg1.index} - {seg2.index} \n"
                          f"      ({seg1.endpoint1.x},{seg1.endpoint1.y}) -- ({seg1.endpoint2.x},{seg1.endpoint2.y}) "
                          f"and ({seg2.endpoint1.x},{seg2.endpoint1.y}) -- ({seg2.endpoint2.x},{seg2.endpoint2.y})")

    def setup(self):
        for i in range(0, max(self.colors) + 1):
            cur = []
            for (j, col) in enumerate(self.colors):
                if col == i:
                    a = self.edges[j][0]
                    b = self.edges[j][1]
                    cur.append(segment.Segment(vertex.Vertex(a[0], a[1]), vertex.Vertex(b[0], b[1]), index=j))

            self.subsets.append(cur)

    def check(self):
        for (subsetnr, subset) in enumerate(self.subsets):
            error = []
            for i in range(len(subset)):
                for j in range(i + 1, len(subset)):
                    if subset[i].intersects(subset[j]):
                        # print(f"We have a problem between edge {subset[i].index} and {subset[j].index} in subset {subsetnr}")
                        error.append((subset[i], subset[j]))
            self.errors.append(error)


def check_instance(instance_name):
    instance = read_instance("instances/" + instance_name + ".instance.json")  # read edges from input file
    g = instance["graph"]
    solution_file = open("solutions/" + instance_name + ".solution.json", 'r')
    data = json.load(solution_file)
    solution_file.close()
    return SolutionCheck(instance_name, g, data["colors"])


if __name__ == "__main__":
    from os import listdir

    instance_names = [file.split('.')[0] for file in listdir("instances/")]

    from multiprocessing import Pool

    with Pool(8) as p:
        solution_checks = p.map(check_instance, instance_names)
        p.close()
        p.join()

    for solcheck in solution_checks:
        if not solcheck.is_correct:
            solcheck.report_errors()
