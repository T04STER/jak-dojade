from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graph import Node, Timestamp


class PriorityQueueNode:
    def __init__(self, node: 'Node', next = None) -> None:
        self.node = node 
        self.next: Optional[PriorityQueueNode] = next

class PriorityQueue:
    """
        Priority queue implemented as linked list
        Note:
            - Time complexity for insert O(1)
            - Time complexity for dequeue O(N)
            
    """    
    def __init__(self, strategy: Callable, node: 'Node'=None) -> None:
        self._first: PriorityQueueNode =  PriorityQueueNode(node)
        self.startegy = strategy
        self._last: PriorityQueueNode = self._first
    
    def enqueue(self, node: 'Node', current_time: 'Timestamp') -> None: 
        new_node = PriorityQueueNode(node)
        if self._first is None:
            self._first = new_node
        self._last.next = new_node
        self._last = new_node

    def dequeue(self) -> 'Node':
        previous_node = self._first
        current = self._first.next
        
        previous_node_to_max = None
        min_priority_node = self._first
        min_priority = self.startegy(min_priority_node.node)
        while current is not None:
            current_priority = self.startegy(current.node)
            if current_priority > min_priority:
                min_priority_node = current
                min_priority = current_priority
                previous_node_to_max = previous_node

            previous_node = current
            current = current.next
            
        if previous_node_to_max is None:
            print(self._first.node)
            self._first = min_priority_node.next
            print(self._first.node)
        else:
            previous_node.next = min_priority_node.next

        return min_priority_node.node
    
    def is_empty(self):
        return self._first is None
    
