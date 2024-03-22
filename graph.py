"""
    Class for Graph, Nodes and Edges
"""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from functools import cache
import heapq
import math
from numbers import Number
import time
from typing import Any, Callable, Dict, Generator, List, Literal, Optional, Tuple, Union
from queue import SimpleQueue
from priority_queue import PriorityQueue
from heapq_priority_item import PriorityItem
import queue as q
import pandas as pd


@dataclass
class Timestamp:
    """
    Time is represented as integer seconds,
    where 0 is 00:00:00. Used for easier computation
    """

    time_str: str
    time: int

    @classmethod
    def create_timestamp(cls, time_str):
        components = time_str.split(":")
        if len(components) == 2:
            h, m = map(int, components)
            s = 0
        elif len(components) == 3:
            h, m, s = map(int, components)
        else:
            raise ValueError("Invalid time format!")

        time_int = h * 3600 + m * 60 + s
        return cls(time_str, time_int)

    def __hash__(self) -> int:
        return hash(self.time)

    def __eq__(self, other: "Timestamp") -> bool:
        return self.time == other.time

    def __gt__(self, other: "Timestamp") -> bool:
        return self.time > other.time

    def __ge__(self, other: "Timestamp") -> bool:
        return self.time >= other.time

    def __le__(self, other: "Timestamp") -> bool:
        return self.time <= other.time

    def __lt__(self, other: "Timestamp") -> bool:
        return self.time < other.time


@dataclass
class Node:
    stop_name: str
    latitude: float
    longitude: float
    neighbours: List["Edge"]

    @cache
    def distance(self, other: "Node") -> int:
        """
        Distance between two points, ignores earth curvture.
        Converts spherical coordinate into Carthesian x,y,z
        """
        radius = 6_371
        self_latitude_rad = math.radians(self.latitude)
        self_longitude_rad = math.radians(self.longitude)
        other_latitude_rad = math.radians(other.latitude)
        other_longitude_rad = math.radians(other.longitude)
        self_x = math.cos(self_latitude_rad) * math.cos(self_longitude_rad)
        self_y = math.sin(self_latitude_rad) * math.cos(self_longitude_rad)
        self_z = math.sin(self_longitude_rad)
        other_x = math.cos(other_latitude_rad) * math.cos(other_longitude_rad)
        other_y = math.sin(other_latitude_rad) * math.cos(other_longitude_rad)
        other_z = math.sin(other_longitude_rad)
        distance = math.sqrt(
            (self_x - other_x) ** 2 + (self_y - other_y) ** 2 + (self_z - other_z) ** 2
        )
        return radius * distance

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

    def get_seconds(self) -> int:
        return self.arrival_time.time - self.departure_time.time


class Graph:
    def __init__(self, filepath: str, cost_estimation_scale=1_500, hop_penalty=500):
        self.cost_estimation_scale = cost_estimation_scale
        self.hop_penalty = hop_penalty
        self.graph: Dict[str, Node] = {}
        connections = pd.read_csv(filepath, low_memory=False)

        start_stops = connections[["start_stop", "start_stop_lat", "start_stop_lon"]]
        start_stops.columns = ["stop", "lat", "lon"]
        end_stops = connections[["end_stop", "end_stop_lat", "end_stop_lon"]]
        end_stops.columns = ["stop", "lat", "lon"]

        stops_concat = pd.concat([start_stops, end_stops])
        stops_concat.drop_duplicates()
        stop_groups_df = stops_concat.groupby("stop").mean()
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

            start_node.neighbours.append(
                (Edge(dep_time, arr_time, end_node, company, line))
            )

    def distinct_edge_bfs(
        self, node: Node, func: Callable[[Node, Edge], Any]
    ) -> Generator:
        """
        Visits each distinct edge one time
        Distinct edge is one of the edges with same src and dest
        Used only for graph render
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

    def dijkstra(
        self, start_node: Node, end_node: Node, start_time: Timestamp
    ) -> Tuple[Optional[List[Edge]], Optional[Number], Optional[Number]]:
        """
        Inefficient dijkstra alghoritm on linked list priority queue,
        first solution
        """
        distance: Dict[Node, Number] = defaultdict(lambda: float("inf"))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict()
        distance[start_node] = 0

        def dijkstra_distance_strategy(node):
            return distance[node]

        queue = PriorityQueue(dijkstra_distance_strategy, start_node, start_time)
        while not queue.is_empty():
            current, arrival = queue.dequeue()
            if end_node is current:
                return self.get_path(prev, start_node, end_node), len(distance)

            edges = current.neighbours
            node_time_lookup: Dict[Node, Timestamp] = {}
            for edge in edges:
                if edge.departure_time >= arrival:
                    time_lookup = node_time_lookup.get(edge.dest)
                    if not time_lookup or time_lookup[0] > edge.arrival_time:
                        node_time_lookup[edge.dest] = edge.arrival_time, edge

            for node, (arival_time, edge) in node_time_lookup.items():
                if distance[node] > arival_time.time:
                    distance[node] = arival_time.time
                    prev[node] = current, edge
                    queue.enqueue(node, arival_time)

        return None, None

    def dijkstra_py_prority_que(
        self, start_node: Node, end_node: Node, start_time: Timestamp
    ) -> Tuple[Optional[List[Edge]], Optional[Number], Optional[Number]]:
        distance: Dict[Node, Number] = defaultdict(lambda: float("inf"))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict()
        distance[start_node] = 0

        queue: q.PriorityQueue[PriorityItem] = q.PriorityQueue()
        queue.put_nowait(PriorityItem(start_time, start_node))
        while not queue.empty():
            priority_item = queue.get_nowait()
            current = priority_item.item
            arrival = priority_item.priority
            if end_node is current:
                return (
                    self.get_path(prev, start_node, end_node),
                    len(distance),
                    distance[current],
                )

            edges = current.neighbours
            for edge in edges:
                if (
                    edge.departure_time >= arrival
                    and distance[edge.dest] > edge.arrival_time.time
                ):
                    queue.put_nowait(PriorityItem(edge.arrival_time, edge.dest))
                    distance[edge.dest] = edge.arrival_time.time
                    prev[edge.dest] = current, edge

        return None, None, None

    def get_path(
        self, prev: Dict[Node, Tuple[Edge, Node]], start_node: Node, end_node: Node
    ) -> List[Edge]:
        current_node = end_node
        path = []
        while current_node is not start_node:
            next_node, edge = prev[current_node]
            path.append(edge)
            current_node = next_node
        return list(reversed(path))

    def dijkstra_heapq(
        self, start_node: Node, end_node: Node, start_time: Timestamp
    ) -> Tuple[Optional[List[Edge]], Optional[Number], Optional[Number]]:
        distance: Dict[Node, Number] = defaultdict(lambda: float("inf"))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict(lambda: None)
        distance[start_node] = 0

        queue: List[PriorityItem] = [
            PriorityItem(start_time.time, start_time, start_node)
        ]
        while queue:
            priority_item = heapq.heappop(queue)
            current = priority_item.item
            arrival = priority_item.arrival
            if end_node is current:
                return (
                    self.get_path(prev, start_node, end_node),
                    len(distance),
                    distance[current],
                )

            edges = current.neighbours
            for edge in edges:
                if (
                    edge.departure_time >= arrival
                    and distance[edge.dest] > edge.arrival_time.time
                ):
                    heapq.heappush(
                        queue,
                        PriorityItem(
                            edge.arrival_time.time, edge.arrival_time, edge.dest, edge
                        ),
                    )
                    distance[edge.dest] = edge.arrival_time.time
                    prev[edge.dest] = current, edge

        return None, None, None

    def a_star(
        self,
        start_node: Node,
        end_node: Node,
        start_time: Timestamp,
        criteria: Union[Literal["time"], Literal["hops"]] = "time",
    ) -> Tuple[Optional[List[Edge]], Optional[Number], Optional[Number]]:
        distance: Dict[Node, Number] = defaultdict(lambda: float("inf"))
        prev: Dict[Node, Tuple[Node, Edge]] = defaultdict(lambda: None)
        distance[start_node] = 0

        def time_cost_func(source: Node, edge: Edge):
            return edge.arrival_time.time

        def least_line_change_cost_func(source: Node, edge: Edge):
            hop_penalty = self.hop_penalty
            previous = prev[source]
            if previous is not None:
                prev_edge = previous[1]
                prev_line = prev_edge.line
                if prev_line == edge.line:
                    hop_penalty = 0
            return distance[source] + hop_penalty

        def cost_estimate_func(edge: Edge):
            return self.cost_estimation_scale * end_node.distance(edge.dest)

        cost_func_reference = (
            time_cost_func if criteria == "time" else least_line_change_cost_func
        )

        queue: List[PriorityItem] = [PriorityItem(0, start_time, start_node)]
        while queue:
            priority_item = heapq.heappop(queue)
            current = priority_item.item
            arrival = priority_item.arrival
            if end_node is current:
                return (
                    self.get_path(prev, start_node, end_node),
                    len(distance),
                    distance[current],
                )

            edges = current.neighbours
            for edge in edges:
                destination_cost = cost_func_reference(current, edge)
                if (
                    edge.departure_time >= arrival
                    and distance[edge.dest] > destination_cost
                ):
                    distance[edge.dest] = destination_cost
                    estimated_cost = destination_cost + cost_estimate_func(edge)
                    heapq.heappush(
                        queue,
                        PriorityItem(estimated_cost, edge.arrival_time, edge.dest),
                    )
                    prev[edge.dest] = current, edge

        return None, None, None


if __name__ == "__main__":
    d = time.time()
    print(f"Started at: {d}")
    graph = Graph("connection_graph.csv")
    ld = time.time()
    print(f"Loaded graph at: {ld} delta {ld-d}")

    def print_edge(node: Node, edge: Edge):
        print(f"{node.stop_name} -> {edge.dest.stop_name}")

    bus_stops = list(graph.graph.keys())
    k = "Brücknera"
    k1 = "ZOO"
    n = graph.graph[k]
    n1 = graph.graph[k1]
    ld = time.time()
    print(f"Going from {n.stop_name} to {n1.stop_name} at 21:05")
    e = time.time()
    path, node, _ = graph.a_star(n, n1, Timestamp.create_timestamp("21:05:10"))
    print(n.stop_name, end="")
    for edge in path:
        print(
            f" {edge.departure_time.time_str} -> {edge.arrival_time.time_str} {edge.dest.stop_name} [{edge.line}]"
        )
    print(f"Delta {time.time()-e}")
    print(f"Visited {node}, path len {len(path)}")
