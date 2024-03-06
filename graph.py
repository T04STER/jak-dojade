"""
    Class for Graph, Nodes and Edges
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Dict, Generator, List, Tuple
import pandas as pd

@dataclass
class Timestamp():
    """
        Time is represented as integer seconds,
        where 0 is 00:00:00. Used for easier computation 
    """
    time_str: str
    time: int
    @classmethod
    def create_timestamp(cls, time_str):
        h, m, s = map(int, time_str.split(':'))
        time_int = h*3600 + m * 60 + s
        return cls(time_str, time_int)

@dataclass(unsafe_hash=True)
class Node:
    stop_name: str
    latitude: float
    longitude: float
    neighbours: List['Edge']

@dataclass
class Edge:
    departure_time: Timestamp
    arrival_time: Timestamp
    dest: Node
    company: str
    line: str





class Graph:
    def __init__(self, filepath: str):
        self.graph: Dict[str, Node] = {}
        connections = pd.read_csv(filepath, low_memory=False)
        bus_stop_tuples = set(connections[['start_stop']+['start_stop_lat']+['start_stop_lon']].itertuples(index=False, name=None))
        bus_stop_tuples.update(set(connections[['end_stop']+['end_stop_lat']+['end_stop_lon']].itertuples(index=False, name=None)))

        stops = set(connections[['start_stop']+['start_stop_lat']+['start_stop_lon']].itertuples(index=False, name=None))
        stops.update(set(connections[['end_stop']+['end_stop_lat']+['end_stop_lon']].itertuples(index=False, name=None)))
        
        # TODO: decide how to handle same name stops
        # Now each is treated as a sepparate stop
        # Ideas:
        # - grouping 
        # - avarage location (maybe check avarage distance for it???)
        for stop in stops:
            self.graph[f"{stop[0]} {stop[1]} {stop[2]}"] = Node(*stop, [])
        
        
        for connection in connections.to_numpy():  
            company = connection[1]
            line = connection[2]
            dep_time = Timestamp.create_timestamp(connection[3])
            arr_time = Timestamp.create_timestamp(connection[4])
            start_stop_id = f"{connection[5]} {connection[7]} {connection[8]}"
            end_stop_id = f"{connection[6]} {connection[9]} {connection[10]}"

            start_node = self.graph[start_stop_id]
            end_node = self.graph[end_stop_id]
            
            start_node.neighbours.append((Edge(dep_time, arr_time, end_node, company, line)))

    def distinct_edge_bfs(self, node: Node, func: Callable[[Node, Edge], Any]) -> Generator:
        """
            Visits each distinct edge one time
            Distinct edge is one of the edges with same src and dest 
        """
        visited: Tuple[Node, Node] = set()
        queue = [node]
        while queue:
            current = queue.pop()
            edges = current.neighbours
            for edge in edges:
                dest = edge.dest
                id_tuple = (id(current), id(dest))
                if id_tuple not in visited:
                    visited.add(id_tuple)
                    queue.append(dest)
                    yield func(current, edge)
    



if __name__ == "__main__":
    graph = Graph('connection_graph.csv')
    
    def print_edge(node: Node, edge: Edge):
        print(f"{node.stop_name} -> {edge.dest.stop_name}" )

    k = list(graph.graph.keys())[0]
    n = graph.graph[k]
    gen = graph.distinct_edge_bfs(n, print_edge)

    
    for _ in gen:
        pass