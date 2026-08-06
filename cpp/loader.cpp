#include <fstream>
#include <sstream>
#include <iostream>
#include <algorithm>
#include <vector>

// Inclui a definição da classe Graph
#include "graph.cpp"

class GraphLoader {
public:
    /**
     * Carrega um grafo a partir de um ficheiro de Lista de Arestas (Edge List).
     * Descobre automaticamente o número total de nós |V(G)|.
     */
    static Graph load_from_file(const std::string& filepath, bool is_directed = false) {
        std::ifstream file(filepath);
        if (!file.is_open()) {
            throw std::runtime_error("Erro ao abrir o ficheiro de grafo: " + filepath);
        }

        int u, v;
        int max_node_id = -1;
        std::vector<std::pair<int, int>> edge_list;

        // 1. Primeira passagem: Ler arestas e encontrar o maior ID de nó
        while (file >> u >> v) {
            edge_list.push_back({u, v});
            max_node_id = std::max({max_node_id, u, v});
        }
        file.close();

        // 2. Criar o Grafo com tamanho |V(G)| = max_node_id + 1 (labels 0 ate max_node_id)[cite: 2]
        int num_nodes = max_node_id + 1;
        Graph G(num_nodes, is_directed);

        // 3. Adicionar as arestas ao Grafo[cite: 2]
        for (const auto& edge : edge_list) {
            G.add_edge(edge.first, edge.second); // add_edge trata de atualizar N(u) e N(v)[cite: 2]
        }

        return G;
    }
};