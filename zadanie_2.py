import argparse
import re
import sys
import time
from typing import List
from graph import Edge, Graph, Node, Timestamp
from tabu import Tabu


DATA_FILE_PATH = "connection_graph.csv"
COST_ESTIMATION_SCALE = 1100
HOP_PENALTY = 920

def validate_time_format(time_str):
    patttern = r'^(0[0-9]|1[0-9]|2[0-9]):([0-5][0-9]):?([0-5][0-9])?$'
    if re.match(patttern, time_str):
        return time_str
    else:
        msg = "Nieprawidłowy format czasu! Wprowadź czas w formacie HH:MM[:SS]."
        raise argparse.ArgumentTypeError(msg)
   

def get_args():
    parser = argparse.ArgumentParser(
        prog="zadanie_2",
        description="""
            Program realizujący drugie zadanie z listy, tzn.
            algorytm wyszukujacy najlepsze połączenie między przystankami 
            zgodnie z kryterium: najszybszych dojazd lub najmniej przesiadek
        """.strip().replace("\t", "")
    )
    parser.add_argument("a", help="Przystanek startowy")
    parser.add_argument("b", help="Przystanki pośrednie odzielone średnikiem (;)")
    parser.add_argument("t", help="Czas pojawienia się na przystanku startowym (HH:MM[:SS])")
    parser.add_argument(
        "k",
        help="Kryterium optymalizacyjne t - optymalizacja czasu, p - optymalizacja ścieżki",
        choices=["t", "p"],
        default="t",
    )
    parser.add_argument('-d', '--detail', help="Wypisz dokładną ścieżkę krok po kroku", action="store_true")
    return parser.parse_args() 


def get_node(graph: Graph, stop_name) -> Node:
    node = graph.graph.get(stop_name)
    if not node:
        print(f"Nieznaleziono przystanku: {stop_name}", file=sys.stderr)
        exit(1)
    return node


def print_solution(path: List[Edge], start_stop: Node, solution: List[Node]):
    current_line = None
    prev_stop_name = start_stop
    prev_arrival = None
    for edge in path: 
        if edge.line != current_line:
            if current_line:
                print(f"Wysiądź z lini {current_line} na {prev_stop_name} o {prev_arrival.time_str}")
            current_line = edge.line           
            print(f"Wsiądź do lini {current_line} na {prev_stop_name} o {edge.departure_time.time_str}")
        elif prev_stop_name in solution:
            print(f"Jesteś na {prev_stop_name}")
        prev_arrival = edge.arrival_time
        prev_stop_name = edge.dest

    print(f"Wysiadź z lini {current_line} na {prev_stop_name} o {prev_arrival.time_str}")

def print_detailed_solution(path: List[Edge], start_stop: str):
    print(start_stop, end="")
    for edge in path:
        print(f" {edge.departure_time.time_str} -> {edge.arrival_time.time_str} {edge.dest.stop_name} [{edge.line}]\n{edge.dest.stop_name}", end='')

def get_stop_nodes(nodes_str:List[str], graph: Graph) -> List[Node]:
    return [
        get_node(graph, node_str) for node_str in nodes_str 
    ]

def main():
    args = get_args()
    
    start_stop_name = args.a
    end_stop_name_list_str = args.b
    end_stop_name_list = end_stop_name_list_str.split(';') 
    start_time = Timestamp.create_timestamp(args.t)
    criteria = 'time' if args.k == 't' else 'hops' 
    
    graph = Graph(DATA_FILE_PATH, COST_ESTIMATION_SCALE, HOP_PENALTY)
    tabu = Tabu(graph, criteria)
    alghoritm_start = time.time()
    start = get_node(graph, start_stop_name)
    stop_nodes = get_stop_nodes(end_stop_name_list, graph)
    path, solution, cost =tabu.tabu_search_v2(start, stop_nodes, start_time)
    alghoritm_end = time.time()
    print(f"Czas algorytmu {alghoritm_end-alghoritm_start}\nWartość funkcji kosztu {cost}", file=sys.stderr)
    if not path:
        print("Nieznaleziono trasy łączącej oba przystanki o podanej godzinie")
        exit(1)
    if not args.detail:
        print_solution(path, start_stop_name, solution)
    else:
        print_detailed_solution(path, start_stop_name)


if __name__ == '__main__':
    main()