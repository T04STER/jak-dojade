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


def graph_benchmark(graph_func, test_nodes:List[Tuple[Node, Node, Timestamp]]):
    visited_nodes =  0
    path_nodes = 0
    failed = 0
    test_quantity = len(test_nodes)
    test_start = time.time()
    for start, stop, start_time in test_nodes:
        p, v, _= graph_func(start, stop, start_time)
        if not p:
            failed += 1
        else:
            visited_nodes+=v
            path_nodes +=len(p)
    test_end = time.time()
    delta = test_end-test_start
    print(f"RESULTS {graph_func.__name__}{ f' cost {graph.cost_estimation_scale}' if 'a_star' in graph_func.__name__ else ''}")
    print(f"Total time: {delta:.4f}")
    print(f"Mean time per route: {delta/test_quantity:.4f}")
    print(f"Mean visited nodes: {visited_nodes/test_quantity:.4f}")
    print(f"Mean path nodes: {path_nodes/test_quantity:.4f}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    graph = Graph('connection_graph.csv')
    test_data = get_test_data(graph, 50)
    for i, (n1, n2, t) in enumerate(test_data):
        print(f"{i+1}. {n1.stop_name} -> {n2.stop_name} @ {t.time_str}")

    graph_benchmark(graph.dijkstra_heapq, test_data)
    graph_benchmark(graph.a_star, test_data)
    graph.cost_estimation_scale = 0
    graph_benchmark(graph.a_star, test_data)
    graph.cost_estimation_scale = 500
    graph_benchmark(graph.a_star, test_data)
    graph.cost_estimation_scale = 2_000
    graph_benchmark(graph.a_star, test_data)