#Provided by the challenge
from cgshop2022utils.io import read_instance, write_instance
import networkx as nx
import random

#Class that represent the vertical decomposition of a planar graph
class VerticalDecomposition:
    def __init__(self):
        # see https://mungingdata.com/python/dag-directed-acyclic-graph-networkx/
        self.dag = nx.DiGraph() #initialize an empty dag

    #finds and returns the trapezoid in which the point lies
    def find_point_location(self, point):
        return None

    #adds a new segment to the vertical decomposition
    def add_segment(self, segment):
        intersecting_faces = find_intersecting_faces(segment)
        for face in intersecting_faces:
            if check_segment_intersects(segment, face):
                add_intersection_to_output(segment1, segment2)
        return None

    #Checks if the given segment has an intersection with another segment in the given trapezoid face
    def check_segment_intersects(self, segment, face):
        # @todo: also write intersecting segments to output file
        return None

    #Finds all trapezoids that intersect the segment
    def find_intersecting_faces(self, segment):
        return []

    #Checks if the segment has an intersection with another segment in this subgraph
    def check_segment_intersects_subgraph(self, segment):
        return None


#Incrementally build vertical decompositions of planar subgraphs
def main():
    edges = read_instance('insert_file_name_here') # read edges from input file
    random.shuffle(edges) # find random reordering of edges

    vds = [VerticalDecomposition()] # init first VD

    for edge in edges:
        for (key, vd) in vds:
            if vd.add_segment(edge):
                # if segment can be added to VD of level key, add it and continue to next edge
                continue
            elif key == count(vds):
                # if segment could not be added in any of the existing VDs, create a new VD
                vds.append(VerticalDecomposition())

    return count(vds)