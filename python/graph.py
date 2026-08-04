from typing import List, Set, Tuple
try:
    from node import Node
except ImportError:
    from .node import Node


class Graph:
    """
    Represents a simple graph G = (V, E).
    """
    def __init__(self, size: int, is_directed: bool = False):
        self.directed: bool = is_directed
        self.V: List[Node] = [Node(i) for i in range(size)]
        self.E: Set[Tuple[int, int]] = set()

    def get_size(self) -> int:
        """Size of Graph |V(G)|."""
        return len(self.V)

    def is_directed(self) -> bool:
        """Check if graph is directed."""
        return self.directed

    def get_node(self, u: int) -> Node:
        """Access node u in V(G)."""
        if u < 0 or u >= len(self.V):
            raise IndexError("Node label out of bounds [0, |V(G)| - 1]")
        return self.V[u]

    def add_edge(self, u: int, v: int) -> bool:
        """
        Add Edge (u, v) to E(G):
        Enforces simple graph properties: no self-loops (u != v).
        """
        if u < 0 or u >= len(self.V) or v < 0 or v >= len(self.V):
            return False

        # Simple graph condition: no self-loops
        if u == v:
            return False

        # Add directed edge (u -> v)
        if (u, v) not in self.E:
            self.E.add((u, v))
            self.V[u].add_neighbor(v)

            # If undirected, add reciprocal edge (v -> u)
            if not self.directed:
                self.E.add((v, u))
                self.V[v].add_neighbor(u)
            return True

        return False  # Edge already exists (no multi-edges)

    def get_num_edges(self) -> int:
        """Get total number of edges |E(G)|."""
        return len(self.E) if self.directed else len(self.E) // 2

    def has_edge(self, u: int, v: int) -> bool:
        """Check if edge (u, v) exists in E(G)."""
        return (u, v) in self.E

    def get_exclusive_neighborhood(self, u: int, S: List[int]) -> List[int]:
        """Get Exclusive Neighborhood N_exc(u, S) wrapper."""
        return self.V[u].get_exclusive_neighborhood(S, self.V)
