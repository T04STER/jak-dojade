"""
    Class for Graph, Nodes and Edges
"""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Callable, Dict, Generator, List, Optional, Tuple
from queue import SimpleQueue
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
        return f"{self.stop_name} {self.longitude} {self.latitude}"
    
    def __repr__(self) -> str:
        return str(self)

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
        distance_lookup = defaultdict(lambda : (float('inf'), None))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict()
        distance_lookup[start_node] = 0

        def dijkstra_distance_strategy(node):
            return distance_lookup[node]


        queue = PriorityQueue(dijkstra_distance_strategy, start_node)
        queue.enqueue(start_node, start_time)
        while not queue.is_empty():
            current = queue.dequeue()
            if end_node == current:
                return self.get_path(prev, start_node, end_node)
            
            edges = current.neighbours
            node_time_lookup = {}
            for edge in edges:
                if edge.departure_time.time > start_time.time:
                    if node_time_lookup.get(edge.dest, (float('inf'), None))[0] > edge.arrival_time.time:
                        node_time_lookup[edge.dest] = edge.arrival_time.time, edge
            print(node_time_lookup)
            for node, (arival_time_int, edge) in node_time_lookup.items():
                print(f"{edge.line} {edge.departure_time.time_str} {current.stop_name} -> {edge.arrival_time.time_str} {node.stop_name}")
                distance_lookup[node] = arival_time_int
                prev[node] = current, edge
                queue.enqueue(node, edge.arrival_time.time)
    
    def get_path(prev: Dict[Node, Tuple[Edge, Node]], start_node: Node, end_node: Node):
        current_node = end_node 
        path = []
        while current_node is not start_node:
            next_node, edge = prev[current_node]
            path.append(edge)
            current_node = next_node 
        return edge


if __name__ == "__main__":
    # graph = Graph('connection_graph.csv')
    
    # def print_edge(node: Node, edge: Edge):
    #     print(f"{node.stop_name} -> {edge.dest.stop_name}" )
    # bus_stops = list(graph.graph.keys())
    # k = bus_stops[0]
    # k1 = bus_stops[1]
    # n = graph.graph[k]
    # n1 = graph.graph[k1]
    # print(f"Going from {n.stop_name} to {n1.stop_name} at 10:30:10")
    # gen = graph.dijkstra(n, n1, Timestamp.create_timestamp("10:30:10"))
    # print(gen)
    
    pq = PriorityQueue(lambda n: n.longitude, Node("xx", 2, 3, []))
    pq.enqueue(Node("sss", 0, 1, []), current_time=None)
    pq.dequeue()