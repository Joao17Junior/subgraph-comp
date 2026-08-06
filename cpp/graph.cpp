#ifndef GRAPH_CPP
#define GRAPH_CPP

#include <vector>
#include <set>
#include <utility>
#include <iostream>
#include <stdexcept>

// Including Node abstraction definition
#include "node.cpp" 

class Graph {
private:
    std::vector<Node> V;                   // V(G): Set/Vector of nodes[cite: 2]
    std::set<std::pair<int, int>> E;       // E(G): Set of edges (u, v)[cite: 2]
    bool directed;                         // True if directed, False if undirected[cite: 2]

public:
    // Construct a simple graph G of size |V(G)|[cite: 2]
    Graph(int size, bool is_directed = false) : directed(is_directed) {
        V.reserve(size);
        for (int i = 0; i < size; ++i) {
            V.emplace_back(i); // L(u) labeled from 0 to |V(G)| - 1[cite: 2]
        }
    }

    // Size of Graph |V(G)|[cite: 2]
    size_t get_size() const {
        return V.size();
    }

    // Check if graph is directed[cite: 2]
    bool is_directed() const {
        return directed;
    }

    // Access node u in V(G)[cite: 2]
    const Node& get_node(int u) const {
        if (u < 0 || u >= static_cast<int>(V.size())) {
            throw std::out_of_range("Node label out of bounds [0, |V(G)| - 1]");
        }
        return V[u];
    }

    /**
     * Add Edge (u, v) to E(G)[cite: 2]:
     * Enforces simple graph properties: no self-loops (u != v)[cite: 2].
     */
    bool add_edge(int u, int v) {
        if (u < 0 || u >= static_cast<int>(V.size()) || 
            v < 0 || v >= static_cast<int>(V.size())) {
            return false;
        }

        // Simple graph condition: no self-loops[cite: 2]
        if (u == v) return false;

        // Add directed edge (u -> v)[cite: 2]
        if (E.find({u, v}) == E.end()) {
            E.insert({u, v});
            V[u].add_neighbor(v);

            // If undirected, add reciprocal edge (v -> u)[cite: 2]
            if (!directed) {
                E.insert({v, u});
                V[v].add_neighbor(u);
            }
            return true;
        }

        return false; // Edge already exists (no multi-edges)[cite: 2]
    }

    // Get total number of edges |E(G)|[cite: 2]
    size_t get_num_edges() const {
        return directed ? E.size() : E.size() / 2;
    }

    // Check if edge (u, v) exists in E(G)[cite: 2]
    bool has_edge(int u, int v) const {
        return E.find({u, v}) != E.end();
    }

    // Get Exclusive Neighborhood N_exc(u, S) wrapper[cite: 2]
    std::vector<int> get_exclusive_neighborhood(int u, const std::vector<int>& S) const {
        return V[u].get_exclusive_neighborhood(S, V);
    }
};

#endif // GRAPH_CPP