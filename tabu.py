import itertools
import random
from graph import *
from zadanie_1 import print_solution
random.seed(255)

class Tabu:
    STEP_LIMIT = 10
    OPERATION_LIMIT = 10
    def __init__(self, graph: Graph, criteria: Literal['time', 'hops'] = 'time') -> None:
        self.graph = graph
        self.criteria = criteria

    def compute_solution_cost(self, solution: List[Node], arrival_time: Timestamp) -> Tuple[List[Node], Number]:
        cost = 0
        path = []
        for i in range(len(solution)-1):
            from_node = solution[i]
            to_node = solution[i+1]
            partial_path,  partial_cost = self.get_cost(from_node, to_node, arrival_time)
            if partial_cost is None:
                return None, float('inf')
            cost += partial_cost
            arrival_time = partial_path[-1].arrival_time
            path.extend(partial_path)
        return path, cost

    @cache
    def get_cost(self, from_node: Node, to_node: Node, from_time: Timestamp) -> Tuple[List[Node], Number]:
        path, _, cost= graph.a_star(from_node, to_node, from_time, self.criteria)
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
    

    def tabu_search(self, start_node: Node, node_list: List[Node], start: Timestamp):
        k = 0
        best_solution = [start_node]
        random.shuffle(node_list)
        best_solution.extend(node_list)
        best_solution.append(start_node)
        best_solution = tuple(best_solution)
        best_path, best_cost = self.compute_solution_cost(best_solution, start)
        tabu = [] 
        local_min = best_solution
        while k < self.STEP_LIMIT:
            for _ in range(len(self.OPERATION_LIMIT)):
                solutions = self.get_neighbours(local_min)
                local_min = solutions[0]
                local_min_path, local_min_cost = self.compute_solution_cost(local_min, start)
                for i in range(1, len(solutions)):
                    solution = solutions[i]
                    if solution in tabu:
                        continue
                    path, cost = self.compute_solution_cost(solution, start)
                    tabu.append(solution)
                    if cost < local_min_cost:
                        local_min = solution
                        local_min_path = path

            if local_min_cost < best_cost:
                best_solution = local_min
                best_path = local_min_path
                best_cost = local_min_cost
            k += 1
        return best_path, solution, best_cost
    

if __name__ == '__main__':
    graph = Graph("connection_graph.csv")
    ld = time.time()
    
    k = "Brücknera"
    n = graph.graph[k]
    n1 = graph.graph["GALERIA DOMINIKAŃSKA"]
    n2 = graph.graph["PL. GRUNWALDZKI"]
    n3 = graph.graph["Kwidzyńska"]
    n4 = graph.graph["KROMERA"]
    tabu = Tabu(graph)
    path, solution, cost = tabu.tabu_search(
        n,
        [n1, n2, n3, n4],
        Timestamp.create_timestamp("8:00")
    )
    for i in enumerate(solution):
        print(i)
    print_solution(path, k)
    
    print(cost)