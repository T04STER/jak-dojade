"""
    Class for Graph, Nodes and Edges
"""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from numbers import Number
import time
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from queue import SimpleQueue
from unittest.mock import Mock
from priority_queue import PriorityQueue
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

    def __eq__(self, other: 'Timestamp') -> bool:
        return self.time == other.time 

    def __gt__(self, other: 'Timestamp') -> bool:
        return self.time > other.time
    
    def __ge__(self, other: 'Timestamp') -> bool:
        return self.time >= other.time

    def __le__(self, other: 'Timestamp') -> bool:
        return self.time <= other.time
    
    def __lt__(self, other: 'Timestamp') -> bool:
        return self.time < other.time
    


@dataclass
class Node:
    stop_name: str
    latitude: float
    longitude: float
    neighbours: List['Edge']
    def __hash__(self) -> int:
        return hash((self.stop_name, self.latitude, self.longitude))
    
    def __eq__(self, __value: object) -> bool:
        return hash(self) == hash(__value) 
    
    def __str__(self) -> str:
        return self.stop_name
    
    def __repr__(self) -> str:
        return str(self) + f" {self.longitude} {self.latitude}"

@dataclass(unsafe_hash=True)
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
        
        start_stops = connections[['start_stop', 'start_stop_lat', 'start_stop_lon']]
        start_stops.columns = ['stop', 'lat', 'lon']
        end_stops = connections[['end_stop', 'end_stop_lat', 'end_stop_lon']]
        end_stops.columns = ['stop', 'lat', 'lon']

        stops_concat = pd.concat(
            [
                start_stops,
                end_stops
            ])
        stops_concat.drop_duplicates()
        stop_groups_df = stops_concat.groupby('stop').mean()
        stop_groups = list(stop_groups_df.itertuples(index=True, name=None))
        for stop in stop_groups:
            self.graph[stop[0]] = Node(*stop, [])
        
        for connection in connections.to_numpy():  
            company = connection[1]
            line = connection[2]
            dep_time = Timestamp.create_timestamp(connection[3])
            arr_time = Timestamp.create_timestamp(connection[4])
            start_stop_id = connection[5]
            end_stop_id = connection[6]

            start_node = self.graph[start_stop_id]
            end_node = self.graph[end_stop_id]
            
            start_node.neighbours.append((Edge(dep_time, arr_time, end_node, company, line)))

    def distinct_edge_dfs(self, node: Node, func: Callable[[Node, Edge], Any]) -> Generator:
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
    
    def distinct_edge_bfs(self, node: Node, func: Callable[[Node, Edge], Any]) -> Generator:
        """
            Visits each distinct edge one time
            Distinct edge is one of the edges with same src and dest 
        """
        visited: Tuple[Node, Node] = set()
        queue = SimpleQueue()
        queue.put_nowait(node)
        while not queue.empty():
            current = queue.get_nowait()
            edges = current.neighbours
            for edge in edges:
                dest = edge.dest
                id_tuple = (id(current), id(dest))
                if id_tuple not in visited:
                    visited.add(id_tuple)
                    queue.put_nowait(dest)
                    yield func(current, edge)


    def dijkstra(self, start_node: Node, end_node: Node, start_time: Timestamp) -> Optional[List[Edge]]:
        distance_lookup: Dict[Node, Number] = defaultdict(lambda : float('inf'))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict()
        distance_lookup[start_node] = 0

        def dijkstra_distance_strategy(node):
            return distance_lookup[node]

        queue = PriorityQueue(dijkstra_distance_strategy, start_node, start_time)
        while not queue.is_empty():
            current, arrival = queue.dequeue()
            if end_node is current:
                return self.get_path(prev, start_node, end_node)

            edges = current.neighbours
            node_time_lookup: Dict[Node, Timestamp] = {}
            for edge in edges:
                if edge.departure_time >= arrival:
                    time_lookup = node_time_lookup.get(edge.dest)
                    if not time_lookup or time_lookup[0] > edge.arrival_time:
                        node_time_lookup[edge.dest] = edge.arrival_time, edge
            

            for node, (arival_time, edge) in node_time_lookup.items():
                if distance_lookup[node] > arival_time.time:
                    distance_lookup[node] = arival_time.time
                    prev[node] = current, edge
                    queue.enqueue(node, arival_time)
        
        return None
    
    def get_path(self, prev: Dict[Node, Tuple[Edge, Node]], start_node: Node, end_node: Node):
        current_node = end_node 
        path = []
        while current_node is not start_node:
            next_node, edge = prev[current_node]
            path.append(edge)
            current_node = next_node 
        return list(reversed(path))


if __name__ == "__main__":
    d = time.time()
    print(f"Started at: {d}")
    graph = Graph('connection_graph.csv')
    ld = time.time()
    print(f"Loaded graph at: {ld} delta {ld-d}")
    def print_edge(node: Node, edge: Edge):
        print(f"{node.stop_name} -> {edge.dest.stop_name}" )
    bus_stops = list(graph.graph.keys())
    k = "Brücknera"
    k1 = "ZOO"
    n = graph.graph[k]
    n1 = graph.graph[k1]
    print(f"Going from {n.stop_name} to {n1.stop_name} at 21:05")
    path = graph.dijkstra(n, n1, Timestamp.create_timestamp("21:05:10"))
    
    print(n.stop_name, end="")
    for edge in path:
        print(f" {edge.departure_time.time_str} -> {edge.arrival_time.time_str} {edge.dest.stop_name} [{edge.line}]")
    e=time.time()
    print(f"Finished at: { e }, it took {e-d}")