import os
import subprocess
import json
import time
import tracemalloc
import psutil
import networkx as nx

# --- PATHS AND CONFIGURATION ---
BIN_DIR = "bin"
DATASETS_DIR = "datasets"
CPP_SOURCE = "cpp/esu.cpp"
CPP_EXECUTABLE = os.path.join(BIN_DIR, "esu_counter")
RAND_CPP_SOURCE = "cpp/rand_esu.cpp"
RAND_CPP_EXECUTABLE = os.path.join(BIN_DIR, "rand_esu_counter")


def compile_cpp(force: bool = False) -> str:
    """Compiles the C++ code into the bin/ folder if needed."""
    os.makedirs(BIN_DIR, exist_ok=True)
    if not os.path.exists(CPP_EXECUTABLE) or force:
        cmd = ["g++", "-O3", CPP_SOURCE, "-o", CPP_EXECUTABLE]
        subprocess.run(cmd, check=True)
    return CPP_EXECUTABLE


def compile_rand_cpp(force: bool = False) -> str:
    """Compiles the Rand-ESU C++ code into the bin/ folder if needed."""
    os.makedirs(BIN_DIR, exist_ok=True)
    if not os.path.exists(RAND_CPP_EXECUTABLE) or force:
        cmd = ["g++", "-O3", RAND_CPP_SOURCE, "-o", RAND_CPP_EXECUTABLE]
        subprocess.run(cmd, check=True)
    return RAND_CPP_EXECUTABLE


def save_graph_to_txt(G: nx.Graph, filename: str) -> str:
    """Saves a NetworkX graph as an edge list in datasets/."""
    os.makedirs(DATASETS_DIR, exist_ok=True)
    if not filename.endswith(".txt"):
        filename += ".txt"
    filepath = os.path.join(DATASETS_DIR, filename)
    with open(filepath, "w") as f:
        for u, v in G.edges():
            f.write(f"{u} {v}\n")
    return filepath


def gen_random_graph(num_nodes: int, edge_prob: float, filename: str = None) -> tuple[nx.Graph, str]:
    """Generates an Erdős-Rényi graph and saves it."""
    G = nx.erdos_renyi_graph(num_nodes, edge_prob)
    if filename is None:
        filename = f"random_n{num_nodes}_p{int(edge_prob * 100)}.txt"
    filepath = save_graph_to_txt(G, filename)
    return G, filepath


def load_graph_from_txt(filepath: str) -> nx.Graph:
    """
    Loads a NetworkX graph from a txt edge list, ensuring nodes are integers
    and adding isolated nodes up to the maximum ID found.
    """
    G = nx.read_edgelist(filepath, nodetype=int)
    
    if len(G) > 0:
        max_node = max(G.nodes())
        for node in range(max_node + 1):
            if not G.has_node(node):
                G.add_node(node)
                
    return G


def run_cpp_esu(graph_path: str, k: int = 3) -> dict:
    """Runs C++ ESU engine and returns JSON data (including RAM usage measured internally by C++)."""
    executable = compile_cpp()
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Dataset não encontrado: {graph_path}")

    cmd = [executable, graph_path, str(k)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    data = json.loads(result.stdout)
    data["ram_usage_mb"] = max(0.01, round(data.get("ram_usage_mb", 0.01), 3))
    return data


def run_rand_cpp_esu(graph_path: str, k: int = 3, sampling_probability: float = 0.5, seed: int = 42) -> dict:
    """Runs Rand-ESU in C++ and returns JSON data (including RAM usage measured internally by C++)."""
    executable = compile_rand_cpp()

    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Dataset não encontrado: {graph_path}")

    cmd = [executable, graph_path, str(k), str(sampling_probability), str(seed)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    data = json.loads(result.stdout)
    data["ram_usage_mb"] = max(0.01, round(data.get("ram_usage_mb", 0.01), 3))
    return data


def run_python_esu(G: nx.Graph, k: int = 3) -> dict:
    """Runs Pure Python ESU and measures execution time + exact isolated peak RAM usage via tracemalloc."""
    from python.esu import GeneralESUCounter

    tracemalloc.start()
    counter = GeneralESUCounter()
    start_time = time.time()

    if k == 0:
        total_subgraphs = 0
        total_steps = 0
        for current_k in range(1, len(G) + 1):
            res = counter.count_subgraphs(G, current_k)
            total_subgraphs += res["total_subgraphs"]
            total_steps += res["recursive_steps"]
        
        elapsed_ms = (time.time() - start_time) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            "algorithm": "ESU (Python Pure)",
            "subgraph_size_k": 0,
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "total_subgraphs": total_subgraphs,
            "recursive_steps": total_steps,
            "execution_time_ms": elapsed_ms,
            "ram_usage_mb": max(0.01, round(peak_bytes / (1024 * 1024), 3))
        }
    else:
        res = counter.count_subgraphs(G, k)
        elapsed_ms = (time.time() - start_time) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        res["graph_nodes"] = G.number_of_nodes()
        res["graph_edges"] = G.number_of_edges()
        res["execution_time_ms"] = elapsed_ms
        res["ram_usage_mb"] = max(0.01, round(peak_bytes / (1024 * 1024), 3))
        return res


def run_rand_python_esu(G: nx.Graph, k: int = 3, sampling_probability: float = 0.5, seed: int = 42) -> dict:
    """Runs Rand-ESU in Python and measures execution time + exact isolated peak RAM usage via tracemalloc."""
    from python.rand_esu import RandESUCounter

    tracemalloc.start()
    counter = RandESUCounter(sampling_probability=sampling_probability, seed=seed)
    start_time = time.time()

    if k == 0:
        total_sampled = 0
        total_estimated = 0.0
        total_steps = 0

        for current_k in range(1, len(G) + 1):
            res = counter.count_subgraphs(G, current_k, sampling_probability=sampling_probability, seed=seed)
            total_sampled += res["sampled_subgraphs"]
            total_estimated += res["estimated_total_subgraphs"]
            total_steps += res["recursive_steps"]

        elapsed_ms = (time.time() - start_time) * 1000.0
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        return {
            "algorithm": "Rand-ESU (Python)",
            "graph_size": G.number_of_nodes(),
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "subgraph_size_k": 0,
            "sampling_probability": sampling_probability,
            "sampled_subgraphs": total_sampled,
            "estimated_total_subgraphs": total_estimated,
            "total_subgraphs": total_estimated,
            "recursive_steps": total_steps,
            "execution_time_ms": elapsed_ms,
            "ram_usage_mb": max(0.01, round(peak_bytes / (1024 * 1024), 3)),
        }

    res = counter.count_subgraphs(G, k, sampling_probability=sampling_probability, seed=seed)
    elapsed_ms = (time.time() - start_time) * 1000.0
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    res["graph_nodes"] = G.number_of_nodes()
    res["graph_edges"] = G.number_of_edges()
    res["execution_time_ms"] = elapsed_ms
    res["ram_usage_mb"] = max(0.01, round(peak_bytes / (1024 * 1024), 3))
    return res


if __name__ == "__main__":
    cpp_result = run_cpp_esu("datasets/random_n30.txt", k=0)
    print("C++ ESU Result:", cpp_result)