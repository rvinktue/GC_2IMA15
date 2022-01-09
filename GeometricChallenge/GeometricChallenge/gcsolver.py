import copy
import json
from cgshop2022utils.io import read_instance  # Provided by the challenge
import random
import vertical_decomposition as vdclass
import geometry
import segment
import vertex


def perform_decompositions(g, shuffle) -> [vdclass.VerticalDecomposition]:
    edges = list(g.edges)
    indices = list(range(len(edges)))
    if shuffle:
        random.shuffle(indices)  # Find random reordering of edges to decrease expected running time complexity

    bounding_box = geometry.find_bounding_box(g.nodes)
    vds = [vdclass.VerticalDecomposition(copy.copy(bounding_box))]

    # Process all edges
    for edgenum in indices:
        edge = edges[edgenum]
        seg = segment.Segment(vertex.Vertex(edge[0][0], edge[0][1]), vertex.Vertex(edge[1][0], edge[1][1]), index=edgenum)
        for (key, vd) in enumerate(vds):
            if vd.add_segment(seg):
                # If segment can be added to the vertical decomposition of level key: add it and continue to next edge
                break
            if key == len(vds) - 1:
                # If segment could not be added in any of the existing VDs, create a new VD
                new = vdclass.VerticalDecomposition(copy.copy(bounding_box))
                new.add_segment(seg)
                vds.append(new)
                break
    return vds


# takes file name outputs json string with solution encoded, no debug info
# Expected format of file_name "instances/<INSTANCE_NAME>.instance.json"
def solve(file_name: str, save_to_file=True, shuffle=False, verify=False) -> str:
    # Incrementally build vertical decompositions of planar subgraphs
    # Read instance and instantiate graph, bounding box and starting vertical decomposition
    instance = read_instance(file_name)  # read edges from input file
    g = instance["graph"]

    vds = perform_decompositions(g, shuffle)

    colours = [-1] * len(g.edges)
    lengths = []

    for (vdnum, vd) in enumerate(vds):
        segments = [x.content for x in vd.dag.find_all(segment.Segment)]
        lengths.append(len(segments))

        for seg in segments:
            colours[seg.index] = vdnum

        if verify:
            print(f"Starting verification on {len(segments)} segments...")
            for (ind, seg1) in enumerate(segments):
                for seg2 in segments[ind+1:]:
                    if seg1 == seg2:
                        continue
                    if seg1.intersects(seg2):
                        print("Verification failed...")
                        return "None"
            print("Verification successful!")
    assert min(colours) >= 0, "Some edges are uncoloured..."
    num_colours = max(colours) - min(colours) + 1
    instance_name = file_name.split('.')[0][10:]

    output_string = "{\n" \
                    "  \"type\": \"Solution_CGSHOP2022\",\n" \
                    "  \"instance\": \"" + instance_name + "\", \n" \
                    "  \"num_colors\": " + str(num_colours) + ", \n" \
                    "  \"colors\": " + str(colours) + "\n" \
                    "}"

    if save_to_file:
        # check if solution is better than existing solution
        score = 1e99
        try:
            json_file = open(f"solutions/{instance_name}.solution.json", 'r')
            data = json.load(json_file)
            score = data["num_colors"]
        except Exception as e:
            # file does not exist
            pass
        finally:
            if num_colours < score:
                f = open("solutions/" + instance_name + ".solution.json", 'w')
                f.write(output_string)
                f.close()
                print(f"{instance_name}: existing solution found with score {score}, worse than new score {num_colours}. Saved!")
            else:
                print(f"{instance_name}: existing solution found with score {score}, better than new score {num_colours}. Not saved.")

    return output_string
