from cgshop2022utils.io import read_instance  # Provided by the challenge

import geometry
import segment
import test_draw
import vertex
import json

import vertical_decomposition


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
                          f"      ({seg1.endpoint1.x},{seg1.endpoint1.y}) -- ({seg1.endpoint2.x},{seg1.endpoint2.y}) and ({seg2.endpoint1.x},{seg2.endpoint1.y}) -- ({seg2.endpoint2.x},{seg2.endpoint2.y})")


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
                        #print(f"We have a problem between edge {subset[i].index} and {subset[j].index} in subset {subsetnr}")
                        error.append((subset[i], subset[j]))
            self.errors.append(error)



def check_instance(instance_name):
    instance = read_instance("instances/"+ instance_name + ".instance.json")  # read edges from input file
    g = instance["graph"]
    solution_file = open("solutions/" + instance_name + ".solution.json", 'r')
    data = json.load(solution_file)
    solution_file.close()
    return SolutionCheck(instance_name, g, data["colors"])



if False and __name__ == "__main__":
    from os import listdir

    instance_names = [file.split('.')[0] for file in listdir("instances/")]

    error_instances = [ "reecn50133", "sqrp18603", "sqrp20166", "sqrp39917", "sqrp41955", "sqrp53087", "sqrp53628", "sqrp55426", "sqrp57865", "sqrp62212", "sqrp63419", "sqrp69435", "sqrp70811", "sqrp73525", "sqrpecn15605", "sqrpecn17395", "sqrpecn27255", "sqrpecn29223", "sqrpecn30017", "sqrpecn30957", "sqrpecn31026", "sqrpecn32073", "sqrpecn35230", "sqrpecn37744", "sqrpecn39689", "sqrpecn44118", "sqrpecn45700", "sqrpecn45811", "sqrpecn48383", "sqrpecn51856", "sqrpecn52587", "sqrpecn54576", "sqrpecn56236", "sqrpecn57317", "sqrpecn58790", "sqrpecn61354", "sqrpecn62891", "sqrpecn65041", "sqrpecn69904", "sqrpecn71261", "sqrpecn71571", "visp70702", "vispecn19370", "vispecn26914", "vispecn27480", "vispecn47378", "vispecn55775", "vispecn58391"]

    from multiprocessing import Pool

    with Pool(8) as p:
        solution_checks = p.map(check_instance, error_instances)
        p.close()
        p.join()

    for solcheck in solution_checks:
        if not solcheck.is_correct:
            solcheck.report_errors()


#print(segment.Segment(vertex.Vertex(0, 0), vertex.Vertex(0, 1)).intersects(segment.Segment(vertex.Vertex(0, 2), vertex.Vertex(0, 3))))

import matplotlib.pyplot as plt
g = read_instance("instances/reecn50133.instance.json")["graph"]
solcheck = check_instance("reecn50133")
solcheck.report_errors()


min = 1241241241124
best = 0
for i in range(len(solcheck.subsets)):
    if len(solcheck.errors[i]) > 0 and len(solcheck.subsets[i]) < min:
        best = i
        min = len(solcheck.subsets[i])

subset = solcheck.errors[best]
print(f"  {len(subset)} unexpected intersections in subset {best} with {len(solcheck.subsets[best])} segments:")
for seg1, seg2 in subset:
    print(f"    Segment {seg1.index} - {seg2.index} \n"
          f"      ({seg1.endpoint1.x},{seg1.endpoint1.y}) -- ({seg1.endpoint2.x},{seg1.endpoint2.y}) and ({seg2.endpoint1.x},{seg2.endpoint1.y}) -- ({seg2.endpoint2.x},{seg2.endpoint2.y})")
print(f"Segment ids: {[(segnr, seg.index) for (segnr, seg) in enumerate(solcheck.subsets[best])]}")
vd = vertical_decomposition.VerticalDecomposition(geometry.find_bounding_box(g.nodes))

for (segnr, seg) in enumerate(solcheck.subsets[best]):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, sharex=True, sharey=True)
    test_draw.test_draw_dag(vd.dag,ax=ax1)
    test_draw.test_draw_dag(vd.dag,ax=ax3)
    node1, node2 = vd.point_location_segment(seg)
    for node in vd.find_intersecting_trapezoids(seg):
        test_draw.test_draw_trapezoid(node.content, (0, 1, 0), ax=ax1, linestyle='-')
    test_draw.test_draw_trapezoid(node1.content, (1, 0, 1), ax=ax1)
    test_draw.test_draw_trapezoid(node2.content, (1, 1, 0), ax=ax1)
    test_draw.test_draw_segment(seg, (0, 1, 1), ax=ax1)
    ax1.set_title(f"Segment {segnr}, {seg.index} to be added.")

    vd.add_segment(seg)
    test_draw.test_draw_dag(vd.dag, ax=ax2)
    test_draw.test_draw_dag(vd.dag, ax=ax4)
    test_draw.test_draw_segment(seg, (0, 1, 1), ax=ax2)
    ax2.set_title(f"Segment {segnr}, {seg.index} added.")
    plt.show()

