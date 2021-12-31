from cgshop2022utils.io import read_instance  # Provided by the challenge
import random
import vertical_decomposition as vdclass
import geometry
import segment, vertex

INPUT_FILE = "instances/vispecn2518.instance.json"  # Name of the input file
#INPUT_FILE = "instances/small.instance.json"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file


# Incrementally build vertical decompositions of planar subgraphs
# Read instance and instantiate graph, bounding box and starting vertical decomposition
instance = read_instance(INPUT_FILE)  # read edges from input file
g = instance["graph"]

edges = g.edges
#random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

bounding_box = geometry.find_bounding_box(g.nodes)
vds = [vdclass.VerticalDecomposition(bounding_box)]

# Init output file
file = open(OUTPUT_FILE, 'w')
file.write("%d %d \n" % (len(edges), len(g.nodes)))
file.close()

# Process all edges
counter = 0
for edge in edges:
    counter = counter + 1
    if counter % 100 == 0:
        print("-------Processed " + str(counter) + " edges ------------")
        break
    seg = segment.Segment(vertex.Vertex(edge[0][0], edge[0][1]), vertex.Vertex(edge[1][0], edge[1][1]))
    for (key, vd) in enumerate(vds):
        if vd.add_segment(seg):
            # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
            break
        if key == len(vds) - 1:
            # If segment could not be added in any of the existing VDs, create a new VD
            new = vdclass.VerticalDecomposition(bounding_box)
            new.add_segment(seg)
            vds.append(new)
            break

import test_draw
import matplotlib.pyplot as plt
for vd in vds:
    test_draw.test_draw_dag(vd.dag)
    plt.show()

# Return an upperbound on the edge-colouring
print(len(vds))
