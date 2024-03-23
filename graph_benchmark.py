import random
from typing import List, Tuple
from graph import *

def random_time():
    hour = random.randint(5, 23)
    minute = random.randint(0, 59)
    return f"{hour:02d}:{minute:02d}:00"


def get_test_data(graph: Graph, quantity: int) -> List[Tuple[Node, Node, Timestamp]]: 
    test_nodes = random.sample(list(graph.graph.values()), quantity*2)
    node_pairs = [(test_nodes[i], test_nodes[i + 1]) for i in range(0, len(test_nodes), 2)]
    return [ (n1, n2, Timestamp.create_timestamp(random_time())) for n1, n2  in node_pairs ]

def get_test_data_between_distance(
        graph: Graph,
        quantity: int,
        min_d=0,
        max_d=10,
    ) -> List[Tuple[Node, Node, Timestamp]]:
    nodes = list(graph.graph.values())
    node_pairs = []
    while len(node_pairs) < quantity:
        src, dest = random.choices(nodes, k=2)
        distance = src.distance(dest)
        if min_d <= distance <= max_d:
            node_pairs.append((src, dest))

    return [ (n1, n2, Timestamp.create_timestamp(random_time())) for n1, n2  in node_pairs ]


def graph_benchmark(graph_func, test_nodes:List[Tuple[Node, Node, Timestamp]], **kwargs):
    visited_nodes =  0
    path_nodes = 0
    failed = 0
    test_quantity = len(test_nodes)
    test_start = time.time()
    for start, stop, start_time in test_nodes:
        p, v, _ = graph_func(start, stop, start_time, **kwargs)
        if not p:
            failed += 1
        else:
            visited_nodes+=v
            path_nodes +=len(p)
    test_end = time.time()
    delta = test_end-test_start
    print(f"RESULTS {graph_func.__name__}{ f' cost graph.cost_estimation_scale' if 'a_star' in graph_func.__name__ else ''}")
    print(f"Total time: {delta:.4f}")
    print(f"Mean time per route: {delta/test_quantity:.4f}")
    print(f"Mean visited nodes: {visited_nodes/test_quantity:.4f}")
    print(f"Mean path nodes: {path_nodes/test_quantity:.4f}")
    print(f"Failed: {failed}")

def graph_benchmark_silent(graph_func, test_nodes:List[Tuple[Node, Node, Timestamp]], **kwargs):
    failed = 0
    test_quantity = len(test_nodes)
    test_start = time.time()
    total_cost = 0
    for start, stop, start_time in test_nodes:
        p, _, cost = graph_func(start, stop, start_time, **kwargs)
        if not p:
            failed += 1
        else:
            total_cost += cost
    test_end = time.time()
    delta = test_end-test_start
    avg_time = delta/test_quantity
    avg_cost = total_cost/test_quantity
    return delta,  avg_time, avg_cost


if __name__ == "__main__":
    graph = Graph('connection_graph.csv')
    test_data = get_test_data_between_distance(graph, 5, 0.1, 1)
    for i, (n1, n2, t) in enumerate(test_data):
        print(f"{i+1}. {n1.stop_name} -> {n2.stop_name} @ {t.time_str}")

    print(graph_benchmark_silent(graph.a_star, test_data, criteria='hops'))
