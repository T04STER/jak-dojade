from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from graph import Node, Timestamp, Edge



@dataclass(order=True)
class PriorityItem:
    """Utility class for heapq and queue.PriorityQueue"""
    priority: int
    arrival: 'Timestamp' = field(compare=False) 
    item: 'Node' = field(compare=False)
    edge: Optional['Edge'] = field(default= None, compare=False)
