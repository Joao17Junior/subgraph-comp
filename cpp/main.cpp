#include <iostream>
#include <chrono>
#include <string>
#include "esu.cpp"
#include "loader.cpp" // ou "graph.cpp" conforme o nome do teu loader

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "{\"error\": \"missing arguments: ./main <graph_file> <subgraph_size_k>\"}" << std::endl;
        return 1;
    }

    std::string graph_file = argv[1];
    int target_k = std::stoi(argv[2]);

    // Carregar o grafo a partir do ficheiro
    Graph G = GraphLoader::load_from_file(graph_file, false);

    long long sum_subgraphs = 0;
    long long sum_recursive_steps = 0;

    auto start = std::chrono::steady_clock::now();

    if (target_k == 0) {
        // k = 0: Calcula para todos os tamanhos k de 1 ate |V(G)|
        ESUCounter esu;
        for (int k = 1; k <= static_cast<int>(G.get_size()); ++k) {
            sum_subgraphs += esu.count_subgraphs(G, k);
            sum_recursive_steps += esu.get_recursive_steps();
        }
    } else {
        // k especifico
        ESUCounter esu;
        sum_subgraphs = esu.count_subgraphs(G, target_k);
        sum_recursive_steps = esu.get_recursive_steps();
    }

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double, std::milli> duration = end - start;

    // --- OUTPUT FORMATADO EM JSON ---
    std::cout << "{"
              << "\"algorithm\": \"ESU (C++)\","
              << "\"subgraph_size_k\": " << target_k << ","
              << "\"graph_nodes\": " << G.get_size() << ","
              << "\"graph_edges\": " << G.get_num_edges() << ","
              << "\"total_subgraphs\": " << sum_subgraphs << ","
              << "\"recursive_steps\": " << sum_recursive_steps << ","
              << "\"execution_time_ms\": " << duration.count()
              << "}" << std::endl;

    return 0;
}