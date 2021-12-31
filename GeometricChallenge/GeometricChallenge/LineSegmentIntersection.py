from cgshop2022utils.io import read_instance  # Provided by the challenge
import random
import vertical_decomposition as vdclass
import geometry
import segment, vertex

INPUT_FILE = "instances/vispecn10178.instance.json"  # Name of the input file
#INPUT_FILE = "instances/small.instance.json"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file


# Incrementally build vertical decompositions of planar subgraphs
# Read instance and instantiate graph, bounding box and starting vertical decomposition
instance = read_instance(INPUT_FILE)  # read edges from input file
g = instance["graph"]

edges = list(g.edges)
#random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

bounding_box = geometry.find_bounding_box(g.nodes)
vds = [vdclass.VerticalDecomposition(bounding_box)]

# Init output file
file = open(OUTPUT_FILE, 'w')
file.write("%d %d \n" % (len(edges), len(g.nodes)))
file.close()

# Process all edges
counter = 0
for (edgenum, edge) in enumerate(edges):
    counter = counter + 1
    if __debug__:
        if counter % 100 == 0:
            print("-------Processed " + str(counter) + " edges ------------")
            break
    seg = segment.Segment(vertex.Vertex(edge[0][0], edge[0][1]), vertex.Vertex(edge[1][0], edge[1][1]), id=edgenum)
    for (key, vd) in enumerate(vds):
        if vd.add_segment(seg):
            # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
            break
        if key == len(vds) - 1:
            # If segment could not be added in any of the existing VDs, create a new VD
            new = vdclass.VerticalDecomposition(bounding_box)
            new.add_segment(seg)
            vds.append(new)
            print("Need new colour: %s" % len(vds))
            break

print("Checking validity")
#we gaan validity checken...

import test_draw
import matplotlib.pyplot as plt
#random.shuffle(vds)
biggestvd = 0
biglen = 0
colours = [-1 for _ in range(len(g.edges))]
for (vdnum, vd) in enumerate(vds):
    segments = test_draw.get_all_content_of_type(vd.dag, segment.Segment)
    if len(segments) > biglen:
        biglen = len(segments)
        biggestvd = vd

    for seg in segments:
        colours[seg.id] = vdnum

    if __debug__:
        for i in range(len(segments)):
            for j in range(i+1, len(segments)):
                if segments[i] == segments[j]:
                    continue
                if segments[i].intersects(segments[j]):
                    print("Not valid since we intersect: (%s, %s) <-> (%s, %s) and (%s, %s) <-> (%s, %s)"
                          % (segments[i].endpoint1.x, segments[i].endpoint1.y,
                             segments[i].endpoint2.x, segments[i].endpoint2.y,
                             segments[j].endpoint1.x, segments[j].endpoint1.y,
                             segments[j].endpoint2.x, segments[j].endpoint2.y,))
                    test_draw.test_draw_segment(segments[i])
                    test_draw.test_draw_segment(segments[j])
                    plt.show()

print("Min(colours): %s" % min(colours))
print("Max(colours): %s" % max(colours))

test_draw.test_draw_dag(biggestvd.dag)
plt.show()

for vd in vds:
    test_draw.test_draw_dag(vd.dag)
    plt.show()

# Return an upperbound on the edge-colouring
print(len(vds))
