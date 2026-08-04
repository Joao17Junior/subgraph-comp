#include <vector>
#include <algorithm>
#include <set>
#include <iostream>

class Node {
private:
    int label;                   // L(u): Node label where 0 <= label < |V(G)|
    std::vector<int> neighbors;  // N(u): Neighborhood set of adjacent node labels

public:
    // Constructor initializing node label L(u)
    explicit Node(int id = 0) : label(id) {}

    // Get Node Label L(u)
    int get_label() const {
        return label;
    }

    // Add an edge target to N(u), avoiding duplicates (simple graph property)
    void add_neighbor(int v_label) {
        if (v_label != label && !has_neighbor(v_label)) { // No self-loops or multi-edges[cite: 2]
            neighbors.push_back(v_label);
        }
    }

    // Check if v in N(u)[cite: 2]
    bool has_neighbor(int v_label) const {
        return std::find(neighbors.begin(), neighbors.end(), v_label) != neighbors.end();
    }

    // Get Neighborhood N(u)[cite: 2]
    const std::vector<int>& get_neighborhood() const {
        return neighbors;
    }

    // Get Degree deg(u) = |N(u)|[cite: 2]
    size_t get_degree() const {
        return neighbors.size();
    }

    /**
     * Exclusive Neighborhood N_exc(u, S)[cite: 2]:
     * Returns neighbors of u that are not neighbors of any v in S (where u != v)[cite: 2].
     */
    std::vector<int> get_exclusive_neighborhood(const std::vector<int>& S, 
                                               const std::vector<Node>& all_nodes) const {
        std::vector<int> N_exc;

        // Collect all neighbors of nodes in S (excluding u)
        std::set<int> S_neighbors;
        for (int v_label : S) {
            if (v_label == this->label) continue;
            const auto& v_nbrs = all_nodes[v_label].get_neighborhood();
            S_neighbors.insert(v_nbrs.begin(), v_nbrs.end());
        }

        // Find neighbors of u that do NOT belong to S and are NOT in S_neighbors
        for (int neighbor : neighbors) {
            bool in_S = (std::find(S.begin(), S.end(), neighbor) != S.end());
            if (!in_S && S_neighbors.find(neighbor) == S_neighbors.end()) {
                N_exc.push_back(neighbor);
            }
        }

        return N_exc;
    }
};