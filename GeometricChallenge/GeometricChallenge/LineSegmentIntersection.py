from cgshop2022utils.io import read_instance, write_instance  # Provided by the challenge
import random
import vertical_decomposition as vdclass
import geometry

INPUT_FILE = "input_file_name"  # Name of the input file
OUTPUT_FILE = "intersection_output.txt"  # Name of the output file


# Incrementally build vertical decompositions of planar subgraphs
def main():
    # Read instance and instantiate graph, bounding box and starting vertical decomposition
    instance = read_instance(INPUT_FILE)  # read edges from input file
    g = instance["graph"]

    edges = g.edges
    random.shuffle(edges)  # Find random reordering of edges to decrease expected running time complexity

    bounding_box = geometry.find_bounding_box(g.nodes)
    vds = [vdclass.VerticalDecomposition(bounding_box)]

    # Init output file
    file = open(OUTPUT_FILE, 'w')
    file.write("%d %d \n" % (len(edges), len(g.nodes)))
    file.close()

    # Process all edges
    for edge in edges:
        for (key, vd) in vds:
            if vd.add_segment(edge):
                # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
                continue
            elif key == len(vds):
                # If segment could not be added in any of the existing VDs, create a new VD
                new = vdclass.VerticalDecomposition(bounding_box)
                new.add_segment(edge)
                vds.append(new)

    # Return an upperbound on the edge-colouring
    return len(vds)
