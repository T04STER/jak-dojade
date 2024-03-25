import itertools
import random
from graph import *
from zadanie_1 import print_detailed_solution, print_solution
random.seed(255)

class Tabu:
    STEP_LIMIT = 10
    OPERATION_LIMIT = 5
    TABU_LEN = 10
    def __init__(self, graph: Graph, criteria: Literal['time', 'hops'] = 'time') -> None:
        self.graph = graph
        self.criteria = criteria

    def compute_solution_cost(self, solution: List[Node], arrival_time: Timestamp) -> Tuple[List[Edge], Number]:
        cost = 0
        path = []
        for i in range(len(solution)-1):
            from_node = solution[i]
            to_node = solution[i+1]
            partial_path,  partial_cost = self.get_partial_solution(from_node, to_node, arrival_time)
            if partial_cost is None:
                return None, float('inf')
            cost += partial_cost
            arrival_time = partial_path[-1].arrival_time
            path.extend(partial_path)
        return path, cost

    @cache
    def get_partial_solution(self, from_node: Node, to_node: Node, from_time: Timestamp) -> Tuple[List[Edge], Number]:
        path, _, cost= self.graph.a_star(from_node, to_node, from_time, self.criteria)
        return path, cost
    
    def get_neighbours(self, solution: Tuple[Node, ...]) -> List[Tuple[Node, ...]]:
        neighbouring_solutions = []
        solution_length = len(solution)
        for i in range(solution_length-3, 0, -1):
            for j in range(solution_length-2, 0, -1):
                if i != j:
                    neighbour = list(solution)
                    neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
                    neighbouring_solutions.append(tuple(neighbour))

        return neighbouring_solutions
    

    def tabu_search(self, start_node: Node, node_list: List[Node], start: Timestamp) -> Tuple[List[Edge], Tuple[Node, ...], Number]:
        k = 0
        random.shuffle(node_list)
        best_solution = tuple([start_node]+node_list+[start_node])
        best_path, best_cost = self.compute_solution_cost(best_solution, start)
        tabu = set()
        local_min = best_solution
        while k < self.STEP_LIMIT:
            for _ in range(self.OPERATION_LIMIT):
                solutions = self.get_neighbours(local_min)
                local_min = solutions[0]
                local_min_path, local_min_cost = self.compute_solution_cost(local_min, start)
                for i in range(1, len(solutions)):
                    solution = solutions[i]
                    if solution in tabu:
                        continue
                    path, cost = self.compute_solution_cost(solution, start)
                    tabu.add(solution)
                    if cost < local_min_cost:
                        local_min = solution
                        local_min_path = path

            if local_min_cost <= best_cost:
                best_solution = local_min
                best_path = local_min_path
                best_cost = local_min_cost
            k += 1
        return best_path, best_solution, best_cost
    
    def get_neighbours_v2(self, solution: Tuple[Node, ...]) -> List[Tuple[Tuple[Node, ...], Tuple[Node, Node]]]:
        neighbouring_solutions = []
        solution_length = len(solution)
        for i in range(solution_length-3, 0, -1):
            for j in range(solution_length-2, 0, -1):
                if i != j:
                    neighbour = list(solution)
                    neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
                    neighbouring_solutions.append((tuple(neighbour), (neighbour[i], neighbour[j])))

        return neighbouring_solutions

    def get_neighbours_v2_1(self, solution: Tuple[Node, ...]) -> List[Tuple[Tuple[Node, ...], Tuple[Node, Node]]]:
        """Random neighbourhood probing"""
        max_solutions = len(solution)
        neighbouring_solutions = []
        solution_length = len(solution)
        for i in range(solution_length-3, 0, -1):
            for j in range(solution_length-2, 0, -1):
                if i != j:
                    neighbour = list(solution)
                    neighbour[i], neighbour[j] = neighbour[j], neighbour[i]
                    neighbouring_solutions.append((tuple(neighbour), (neighbour[i], neighbour[j])))
        return random.choices(neighbouring_solutions, k=max_solutions)
    def hash_nodes(self, node1: Node, node2: Node) -> int:
        """ Create distinct hash for nodes, ignore order"""
        return hash(node2.stop_name + node1.stop_name)

    def pick_best(self, solutions: List[Tuple[Node, ...]], tabu, start) -> Tuple[List[Edge], Tuple[Node, ...]]:
        local_min = None
        local_min_path, local_min_cost = None, None
        for solution, nodes in solutions:
            solution_hash = self.hash_nodes(*nodes)
            if solution_hash in tabu:
                continue
            path, cost = self.compute_solution_cost(solution, start)
            if len(tabu) > self.TABU_LEN:
                tabu.pop(0)
            tabu.append(solution_hash)
            if not local_min or cost < local_min_cost:
                local_min = solution
                local_min_path = path
                local_min_cost = cost
        return local_min, local_min_path, local_min_cost

    def tabu_search_v2(self, start_node: Node, node_list: List[Node], start: Timestamp) -> Tuple[List[Edge], Tuple[Node, ...], Number]:
        k = 0
        random.shuffle(node_list)
        best_solution = tuple([start_node]+node_list+[start_node])
        best_path, best_cost = self.compute_solution_cost(best_solution, start)
        tabu = []
        local_min = best_solution
        local_min_path, local_min_cost = self.compute_solution_cost(local_min, start) 
        while k < self.STEP_LIMIT:
            for _ in range(self.OPERATION_LIMIT):
                solutions = self.get_neighbours_v2_1(local_min)
                s_prim, s_prim_path, s_prim_cost = self.pick_best(solutions, tabu, start)
                if s_prim and s_prim_cost <= local_min_cost:
                    local_min = s_prim
                    local_min_path = s_prim_path
                    local_min_cost = s_prim_cost

            if local_min_cost <= best_cost:
                best_solution = local_min
                best_path = local_min_path
                best_cost = local_min_cost
            k += 1
        return best_path, best_solution, best_cost
    


if __name__ == '__main__':
    graph = Graph("connection_graph.csv")
    ld = time.time()
    
    k = "Brücknera"
    n = graph.graph[k]
    ns = [
        graph.graph["GALERIA DOMINIKAŃSKA"],
        graph.graph["PL. GRUNWALDZKI"],
        graph.graph["Kwidzyńska"],
        graph.graph["KARŁOWICE"],
        graph.graph["FAT"],
    graph.graph["GALERIA DOMINIKAŃSKA"],
    graph.graph["PL. GRUNWALDZKI"],
    graph.graph["Kwidzyńska"],
    graph.graph["KARŁOWICE"],
    graph.graph["pl. Orląt Lwowskich"],
    graph.graph["pl. Bema"],
    graph.graph["Poczta Główna"],
        ]
    tabu = Tabu(graph)
    path, solution, cost = tabu.tabu_search_v2(
        n,
        ns,
        Timestamp.create_timestamp("8:00")
    )
    for i in enumerate(solution):
        print(i)
    print(f"cost {cost}")
    print(f"from 8:00 to {path[-1].arrival_time.time_str}")
