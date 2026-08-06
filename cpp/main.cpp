#include <iostream>
#include "esu.cpp"

int main() {
    // Create a simple undirected graph G with 5 nodes (0 to 4)
    Graph G(5, false);

    // Add edges to the graph G
    G.add_edge(0, 1);
    G.add_edge(0, 2);
    G.add_edge(1, 2);
    G.add_edge(1, 3);
    G.add_edge(2, 4);
    G.add_edge(3, 4);

    ESUCounter esu;
    int k = 3;

    long long subgraphs_k3 = esu.count_subgraphs(G, k);

    std::cout << "--- Resultado do ESU (Survey Subgraph Counting) ---" << std::endl;
    std::cout << "Tamanho do Grafo |V(G)|: " << G.get_size() << " nos" << std::endl;
    std::cout << "Tamanho do Subgrafo (k): " << k << std::endl;
    std::cout << "Total de Subgrafos Encontrados: " << subgraphs_k3 << std::endl;
    std::cout << "Passos Recursivos Dados: " << esu.get_recursive_steps() << std::endl;

    return 0;
}