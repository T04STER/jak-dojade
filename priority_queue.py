from typing import Callable, Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from graph import Node, Timestamp


class PriorityQueueNode:
    def __init__(self, node: 'Node', arrival_time: 'Timestamp', next = None) -> None:
        self.node = node
        self.arrival_time = arrival_time
        self.next: Optional[PriorityQueueNode] = next
    def __str__(self):
        return f"{str(self.node)} {str(self.next.node) if self.next else 'last'}"
    
    
class PriorityQueue:
    """
        Priority queue implemented as linked list
        Note:
            - Time complexity for enqueue O(1)
            - Time complexity for dequeue O(N)
            
    """    
    def __init__(self, strategy: Callable, node: 'Node', arrival_time: 'Timestamp') -> None:
        self._first: PriorityQueueNode =  PriorityQueueNode(node, arrival_time)
        self.strategy = strategy
        self._last: PriorityQueueNode = self._first
    
    def enqueue(self, node: 'Node', arrival_time: 'Timestamp') -> None: 
        new_node = PriorityQueueNode(node, arrival_time)
        if self._first is None:
            self._first = new_node
        else:
            self._last.next = new_node
        self._last = new_node

    def dequeue(self) -> Tuple['Node', 'Timestamp']:
        min_priority_node = self._first
        previous_node_to_min = None
        previous_node = self._first
        current = self._first.next
        
        
        previous_node_to_min = None
        min_priority_node = self._first
        min_priority = self.strategy(min_priority_node.node)

        while current is not None:
            current_priority = self.strategy(current.node)
            if current_priority < min_priority:
                min_priority_node = current
                previous_node_to_min = previous_node

            previous_node = current
            current = current.next

        if previous_node_to_min is None:
            self._first = min_priority_node.next
        else:
            previous_node_to_min.next = min_priority_node.next
        
        if min_priority_node is self._last:
            self._last = previous_node_to_min 

        return min_priority_node.node, min_priority_node.arrival_time
    
    def print_queue(self) -> None:
        current = self._first
        print('[ ', end='')
        while current is not None:
            print(f"({str(current.node)})", end=', ')
            current = current.next
        print(' ]')
    
    def is_empty(self):
        return self._first is None
    
