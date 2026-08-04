from typing import List, Set

class Node:
    """
    Represents a Node u in a graph.
    """
    def __init__(self, id: int = 0):
        self.label: int = id
        self.neighbors: List[int] = []

    def get_label(self) -> int:
        """Get Node Label L(u)."""
        return self.label

    def add_neighbor(self, v_label: int) -> None:
        """Add an edge target to N(u), avoiding duplicates (simple graph property)."""
        if v_label != self.label and not self.has_neighbor(v_label):
            self.neighbors.append(v_label)

    def has_neighbor(self, v_label: int) -> bool:
        """Check if v in N(u)."""
        return v_label in self.neighbors

    def get_neighborhood(self) -> List[int]:
        """Get Neighborhood N(u)."""
        return self.neighbors

    def get_degree(self) -> int:
        """Get Degree deg(u) = |N(u)|."""
        return len(self.neighbors)

    def get_exclusive_neighborhood(self, S: List[int], all_nodes: List['Node']) -> List[int]:
        """
        Exclusive Neighborhood N_exc(u, S):
        Returns neighbors of u that are not neighbors of any v in S (where u != v).
        """
        N_exc: List[int] = []

        # Collect all neighbors of nodes in S (excluding u)
        S_neighbors: Set[int] = set()
        for v_label in S:
            if v_label == self.label:
                continue
            v_nbrs = all_nodes[v_label].get_neighborhood()
            S_neighbors.update(v_nbrs)

        # Find neighbors of u that do NOT belong to S and are NOT in S_neighbors
        S_set = set(S)
        for neighbor in self.neighbors:
            if neighbor not in S_set and neighbor not in S_neighbors:
                N_exc.append(neighbor)

        return N_exc
