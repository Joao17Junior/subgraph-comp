import random
import time
from typing import Optional

import networkx as nx


class RandESUCounter:
    """Randomized ESU counter for sampled connected induced subgraphs."""

    def __init__(self, sampling_probability: float = 0.5, seed: Optional[int] = None):
        self.sampling_probability = sampling_probability
        self.seed = seed
        self.sampled_subgraphs = 0
        self.recursive_steps = 0
        self._rng = random.Random(seed)

    def _reset_rng(self, seed: Optional[int] = None) -> None:
        seed_to_use = self.seed if seed is None else seed
        self._rng = random.Random(seed_to_use)

    def _get_exclusive_neighborhood(self, G: nx.Graph, u: int, V_S: set[int]) -> set[int]:
        """Return neighbors of u that are not in V_S and not adjacent to V_S."""
        u_nbrs = set(G.neighbors(u)) - V_S

        V_S_nbrs: set[int] = set()
        for v in V_S:
            if v != u:
                V_S_nbrs.update(G.neighbors(v))

        return u_nbrs - V_S_nbrs

    def _extend_subgraph(self, G: nx.Graph, V_S: set[int], V_E: list[int], v_root: int, k: int):
        self.recursive_steps += 1

        if len(V_S) == k:
            self.sampled_subgraphs += 1
            return

        while V_E:
            u = V_E.pop()

            if self._rng.random() > self.sampling_probability:
                continue

            V_S_next = V_S.copy()
            V_S_next.add(u)

            N_exc = self._get_exclusive_neighborhood(G, u, V_S)

            V_E_next = V_E.copy()
            for w in N_exc:
                if w > v_root:
                    V_E_next.append(w)

            self._extend_subgraph(G, V_S_next, V_E_next, v_root, k)

    def count_subgraphs(
        self,
        G: nx.Graph,
        k: int,
        sampling_probability: Optional[float] = None,
        seed: Optional[int] = None,
    ) -> dict:
        """Estimate the number of connected induced k-subgraphs using Rand-ESU."""
        if sampling_probability is not None:
            self.sampling_probability = sampling_probability

        self.sampled_subgraphs = 0
        self.recursive_steps = 0
        self._reset_rng(seed)

        start_time = time.time()

        if k == 0:
            total_sampled = 0
            total_estimated = 0.0
            total_steps = 0

            for current_k in range(1, len(G) + 1):
                res = self.count_subgraphs(G, current_k)
                total_sampled += res["sampled_subgraphs"]
                total_estimated += res["estimated_total_subgraphs"]
                total_steps += res["recursive_steps"]

            elapsed_ms = (time.time() - start_time) * 1000.0
            return {
                "algorithm": "Rand-ESU (Python)",
                "graph_size": G.number_of_nodes(),
                "graph_nodes": G.number_of_nodes(),
                "graph_edges": G.number_of_edges(),
                "subgraph_size_k": 0,
                "sampling_probability": self.sampling_probability,
                "sampled_subgraphs": total_sampled,
                "estimated_total_subgraphs": total_estimated,
                "total_subgraphs": total_estimated,
                "recursive_steps": total_steps,
                "execution_time_ms": elapsed_ms,
            }

        for v in G.nodes():
            V_S = {v}
            V_E = [u for u in G.neighbors(v) if u > v]
            self._extend_subgraph(G, V_S, V_E, v, k)

        elapsed_ms = (time.time() - start_time) * 1000.0
        scale = self.sampling_probability ** max(0, k - 1)
        estimated_total_subgraphs = self.sampled_subgraphs / scale if scale > 0 else 0.0

        return {
            "algorithm": "Rand-ESU (Python)",
            "graph_size": G.number_of_nodes(),
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "subgraph_size_k": k,
            "sampling_probability": self.sampling_probability,
            "sampled_subgraphs": self.sampled_subgraphs,
            "estimated_total_subgraphs": estimated_total_subgraphs,
            "total_subgraphs": estimated_total_subgraphs,
            "recursive_steps": self.recursive_steps,
            "execution_time_ms": elapsed_ms,
        }
