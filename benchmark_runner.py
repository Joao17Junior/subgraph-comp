import os
import subprocess
import json
import time
import networkx as nx

# --- PATHS AND CONFIGURATION ---
BIN_DIR = "bin"
CPP_SOURCE = "cpp/main.cpp"          # Adjust the path to your main.cpp if needed
CPP_EXECUTABLE = os.path.join(BIN_DIR, "esu_counter")


def compile_cpp(force: bool = False) -> str:
    """
    Compiles the C++ code into the bin/ folder if the executable does not exist.
    """
    os.makedirs(BIN_DIR, exist_ok=True)
    
    if not os.path.exists(CPP_EXECUTABLE) or force:
        print(f"🔨 Compilando {CPP_SOURCE} -> {CPP_EXECUTABLE}...")
        cmd = ["g++", "-O3", CPP_SOURCE, "-o", CPP_EXECUTABLE]
        try:
            subprocess.run(cmd, check=True)
            print("✅ Compilação concluída com sucesso!")
        except subprocess.CalledProcessError as e:
            print("❌ Erro ao compilar o código C++.")
            raise e
            
    return CPP_EXECUTABLE


def run_cpp_esu(graph_path: str, k: int = 3) -> dict:
    """
    Runs the C++ ESU engine via subprocess and returns the result as a Python dictionary (JSON).
    If k = 0, the C++ code computes all subgraphs.
    """
    executable = compile_cpp()
    
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Ficheiro de grafo não encontrado: {graph_path}")

    # Run ./bin/esu_counter <graph_path> <k>
    cmd = [executable, graph_path, str(k)]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)

    # Convert stdout (JSON) directly into a Python dictionary
    return json.loads(result.stdout)


def run_python_esu(G: nx.Graph, k: int = 3) -> dict:
    """
    Runs ESU in pure Python / NetworkX for comparison.
    """
    from python.esu import GeneralESUCounter # Assuming the ESU class in Python

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
        
        return {
            "algorithm": "ESU (Python Pure)",
            "subgraph_size_k": 0,
            "graph_nodes": G.number_of_nodes(),
            "graph_edges": G.number_of_edges(),
            "total_subgraphs": total_subgraphs,
            "recursive_steps": total_steps,
            "execution_time_ms": elapsed_ms
        }
    else:
        res = counter.count_subgraphs(G, k)
        res["graph_nodes"] = G.number_of_nodes()
        res["graph_edges"] = G.number_of_edges()
        return res


def run_networkx_baseline(G: nx.Graph, k: int = 3) -> dict:
    """
    Runs connected induced subgraph counting using NetworkX as a baseline.
    """
    from python.nx import NetworkXCounter

    if k < 3 or k > 4:
        raise ValueError("NetworkX baseline only supports k=3 or k=4 for fast comparison.")
    
    return NetworkXCounter.count_subgraphs(G, k)

# --- CALL TEST ---
if __name__ == "__main__":
    compile_cpp(force=True)
    print("Hello World")