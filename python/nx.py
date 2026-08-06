import time
import networkx as nx

class NetworkXCounter:
    """
    Python baseline using standard NetworkX for exact induced 
    connected subgraph counting.
    """
    
    @staticmethod
    def count_subgraphs(G: nx.Graph, k: int) -> dict:
        """
        G: Native NetworkX graph
        k: Subgraph size (e.g., k=3 or k=4)
        """
        start_time = time.time()
        
        if k == 3:
            # Induced 3-node triangles in NetworkX
            # nx.triangles returns {node: number_of_triangles_touching_node}
            triangles_dict = nx.triangles(G)
            total_subgraphs = sum(triangles_dict.values()) // 3
            
        elif k == 4:
            # For k=4, using clique enumeration as a standard baseline comparison
            total_subgraphs = 0
            for clique in nx.enumerate_all_cliques(G):
                if len(clique) == 4:
                    total_subgraphs += 1
                elif len(clique) > 4:
                    break
        else:
            raise ValueError("Unsupported k value for fast baseline comparison.")

        elapsed_ms = (time.time() - start_time) * 1000.0

        return {
            "algorithm": "NetworkX (Python Native)",
            "subgraph_size_k": k,
            "total_subgraphs": total_subgraphs,
            "execution_time_ms": elapsed_ms
        }