#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <vector>

// Include the Graph class definition
#include "graph.cpp"

class GraphLoader {
public:
    /**
     * Loads a graph from an edge list file.
     * Automatically infers the total number of nodes |V(G)|.
     */
    static Graph load_from_file(const std::string& filepath, bool is_directed = false) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            throw std::runtime_error("Error opening graph file: " + filepath);
        }

        int u, v;
        int max_node_id = -1;
        std::vector<std::pair<int, int>> edge_list;

        // 1. First pass: read edges and find the largest node ID
        while (file >> u >> v) {
            edge_list.push_back({u, v});
            max_node_id = std::max({max_node_id, u, v});
        }
        file.close();

        // 2. Create the graph with size |V(G)| = max_node_id + 1 (labels 0 through max_node_id)[cite: 2]
        int num_nodes = max_node_id + 1;
        Graph G(num_nodes, is_directed);

        // 3. Add the edges to the graph[cite: 2]
        for (const auto& edge : edge_list) {
            G.add_edge(edge.first, edge.second); // add_edge updates N(u) and N(v)[cite: 2]
        }

        return G;
    }
};