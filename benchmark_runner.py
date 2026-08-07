import os
import subprocess
import json
import time
import psutil
import networkx as nx

# --- PATHS AND CONFIGURATION ---
BIN_DIR = "bin"
DATASETS_DIR = "datasets"
CPP_SOURCE = "cpp/main.cpp"
CPP_EXECUTABLE = os.path.join(BIN_DIR, "esu_counter")


def compile_cpp(force: bool = False) -> str:
    """Compiles the C++ code into the bin/ folder if needed."""
    os.makedirs(BIN_DIR, exist_ok=True)
    if not os.path.exists(CPP_EXECUTABLE) or force:
        cmd = ["g++", "-O3", CPP_SOURCE, "-o", CPP_EXECUTABLE]
        subprocess.run(cmd, check=True)
    return CPP_EXECUTABLE


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
    # 1. Carregar arestas com o tipo int obrigatoriamente
    G = nx.read_edgelist(filepath, nodetype=int)
    
    # 2. Descobrir o ID máximo e adicionar nós isolados em falta (ex: 3 e 7)
    if len(G) > 0:
        max_node = max(G.nodes())
        for node in range(max_node + 1):
            if not G.has_node(node):
                G.add_node(node)  # Adiciona nó isolado
                
    return G


def run_cpp_esu(graph_path: str, k: int = 3) -> dict:
    """Runs C++ ESU engine and measures execution time + RAM usage."""
    executable = compile_cpp()
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Dataset não encontrado: {graph_path}")

    process = psutil.Process()
    mem_before = process.memory_info().rss / (1024 * 1024)

    cmd = [executable, graph_path, str(k)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    mem_after = process.memory_info().rss / (1024 * 1024)
    data = json.loads(result.stdout)
    data["ram_usage_mb"] = max(0.01, round(mem_after - mem_before, 3))
    return data


def run_python_esu(G: nx.Graph, k: int = 3) -> dict:
    """Runs Pure Python ESU and measures time + RAM usage."""
    from python.esu import GeneralESUCounter

    process = psutil.Process()
    mem_before = process.memory_info().rss / (1024 * 1024)

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
        mem_after = process.memory_info().rss / (1024 * 1024)
        
        return {
            "algorithm": "ESU (Python Pure)",
            "subgraph_size_k": 0,
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "total_subgraphs": total_subgraphs,
            "recursive_steps": total_steps,
            "execution_time_ms": elapsed_ms,
            "ram_usage_mb": max(0.01, round(mem_after - mem_before, 3))
        }
    else:
        res = counter.count_subgraphs(G, k)
        res["graph_nodes"] = G.number_of_nodes()
        res["graph_edges"] = G.number_of_edges()
        mem_after = process.memory_info().rss / (1024 * 1024)
        res["ram_usage_mb"] = max(0.01, round(mem_after - mem_before, 3))
        return res