import time
import networkx as nx

class GeneralESUCounter:
    """
    Universal ESU Subgraph Counter in Python.
    Works for any arbitrary k >= 1 on any NetworkX graph.
    """
    
    def __init__(self):
        self.total_subgraphs = 0
        self.recursive_steps = 0

    def _get_exclusive_neighborhood(self, G: nx.Graph, u: int, V_S: set) -> set:
        """Calculates N_exc(u, V_S): neighbors of u not in V_S and not adjacent to V_S"""
        # Neighbors of u excluding V_S
        u_nbrs = set(G.neighbors(u)) - V_S
        
        # Neighbors of all other nodes in V_S
        V_S_nbrs = set()
        for v in V_S:
            if v != u:
                V_S_nbrs.update(G.neighbors(v))
                
        return u_nbrs - V_S_nbrs

    def _extend_subgraph(self, G: nx.Graph, V_S: set, V_E: list, v_root: int, k: int):
        self.recursive_steps += 1

        # Stop condition: |V_S| == k
        if len(V_S) == k:
            self.total_subgraphs += 1
            return

        while V_E:
            u = V_E.pop()
            
            V_S_next = V_S.copy()
            V_S_next.add(u)

            # Get exclusive neighborhood N_exc(u, V_S)
            N_exc = self._get_exclusive_neighborhood(G, u, V_S)

            # Symmetry breaking: L(w) > L(v_root)
            V_E_next = V_E.copy()
            for w in N_exc:
                if w > v_root:
                    V_E_next.append(w)

            self._extend_subgraph(G, V_S_next, V_E_next, v_root, k)

    def count_subgraphs(self, G: nx.Graph, k: int) -> dict:
        """
        Main function to count all connected induced k-subgraphs.
        Accepts any integer k >= 1.
        """
        self.total_subgraphs = 0
        self.recursive_steps = 0
        
        start_time = time.time()

        for v in G.nodes():
            V_S = {v}
            # Initial candidates with symmetry breaking
            V_E = [u for u in G.neighbors(v) if u > v]
            
            self._extend_subgraph(G, V_S, V_E, v, k)

        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "algorithm": "ESU (Python)",
            "graph_size": G.number_of_nodes(),
            "subgraph_size_k": k,
            "total_subgraphs": self.total_subgraphs,
            "recursive_steps": self.recursive_steps,
            "execution_time_ms": elapsed_ms
        }