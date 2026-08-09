#include <iostream>
#include <vector>
#include <chrono>
#include <string>
#include <sys/resource.h>

// Include the Node and Graph abstractions defined earlier
#include "loader.cpp"

class ESUCounter {
private:
    long long total_subgraphs; // Total count of subgraphs of size k[cite: 2]
    long long recursive_steps; // Number of recursive calls (tree steps)

    /**
     * Recursive ExtendSubgraph function (Wernicke, 2005)[cite: 2]
     * 
     * @param V_S Set of vertices that form the current subgraph[cite: 2]
     * @param V_E Expansion candidate set[cite: 2]
     * @param v_root Starting vertex (used for the symmetry break L(w) > L(v_root))[cite: 2]
     * @param k Size of the subgraph to count (k-graph)[cite: 2]
     * @param G Input graph[cite: 2]
     */
    void extend_subgraph(std::vector<int>& V_S, 
                         std::vector<int>& V_E, 
                         int v_root, 
                         int k, 
                         const Graph& G) {
        recursive_steps++;

        // Stopping condition: |V_S| = k (one k-subgraph occurrence found)[cite: 2]
        if (V_S.size() == static_cast<size_t>(k)) {
            total_subgraphs++;
            return;
        }

        // While V_E is not empty[cite: 2]
        while (!V_E.empty()) {
            // Remove a vertex u from V_E[cite: 2]
            int u = V_E.back();
            V_E.pop_back();

            // V_S' = V_S U {u}[cite: 2]
            std::vector<int> V_S_next = V_S;
            V_S_next.push_back(u);

            // Get N_exc(u, V_S)[cite: 2]
            std::vector<int> N_exc = G.get_exclusive_neighborhood(u, V_S);

            // V_E' = V_E U {w in N_exc(u, V_S) : L(w) > L(v_root)}[cite: 2]
            std::vector<int> V_E_next = V_E;
            for (int w : N_exc) {
                // The condition L(w) > L(v_root) guarantees symmetry breaking[cite: 2]
                if (w > v_root) { 
                    V_E_next.push_back(w);
                }
            }

            // Recursive call with the new state[cite: 2]
            extend_subgraph(V_S_next, V_E_next, v_root, k, G);
        }
    }

public:
    ESUCounter() : total_subgraphs(0), recursive_steps(0) {}

    /**
     * Performs the exact counting of size-k subgraphs in graph G[cite: 2].
     * 
     * @param G The simple graph[cite: 2]
     * @param k The subgraph size (e.g. k = 3 or k = 4)[cite: 2]
     * @return The total number of connected induced subgraphs found[cite: 2]
     */
    long long count_subgraphs(const Graph& G, int k) {
        total_subgraphs = 0;
        recursive_steps = 0;

        int num_nodes = static_cast<int>(G.get_size());

        // Apply the method to each vertex v in V(G)[cite: 2]
        for (int v = 0; v < num_nodes; ++v) {
            std::vector<int> V_S = {v}; // Initial V_S = {v}[cite: 2]
            std::vector<int> V_E;

            // Initial V_E = {u in N(v) : L(u) > L(v)}[cite: 2]
            const auto& neighbors = G.get_node(v).get_neighborhood();
            for (int u : neighbors) {
                if (u > v) { // Initial symmetry break L(u) > L(v)[cite: 2]
                    V_E.push_back(u);
                }
            }

            // Start exploration from root vertex v[cite: 2]
            extend_subgraph(V_S, V_E, v, k, G);
        }

        return total_subgraphs;
    }

    long long get_recursive_steps() const {
        return recursive_steps;
    }
};

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "{\"error\": \"missing arguments: ./main <graph_file> <subgraph_size_k>\"}" << std::endl;
        return 1;
    }

    std::string graph_file = argv[1];
    int target_k = std::stoi(argv[2]);

    // Load the graph from the file
    Graph G = GraphLoader::load_from_file(graph_file, false);

    long long sum_subgraphs = 0;
    long long sum_recursive_steps = 0;

    auto start = std::chrono::steady_clock::now();

    if (target_k == 0) {
        // k = 0: compute all k values from 1 to |V(G)|
        ESUCounter esu;
        for (int k = 1; k <= static_cast<int>(G.get_size()); ++k) {
            sum_subgraphs += esu.count_subgraphs(G, k);
            sum_recursive_steps += esu.get_recursive_steps();
        }
    } else {
        // Specific k
        ESUCounter esu;
        sum_subgraphs = esu.count_subgraphs(G, target_k);
        sum_recursive_steps = esu.get_recursive_steps();
    }

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double, std::milli> duration = end - start;

    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);

    double peak_ram_mb = static_cast<double>(usage.ru_maxrss) / 1024.0; // Convert to MB

    // --- FORMATTED JSON OUTPUT ---
    std::cout << "{"
            << "\"algorithm\": \"ESU (C++)\","
            << "\"subgraph_size_k\": " << target_k << ","
            << "\"graph_nodes\": " << G.get_size() << ","
            << "\"graph_edges\": " << G.get_num_edges() << ","
            << "\"total_subgraphs\": " << sum_subgraphs << ","
            << "\"recursive_steps\": " << sum_recursive_steps << ","
            << "\"execution_time_ms\": " << duration.count() << ","
            << "\"ram_usage_mb\": " << peak_ram_mb
            << "}" << std::endl;

    return 0;
}
