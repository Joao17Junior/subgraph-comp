#include <chrono>
#include <cmath>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <sys/resource.h>

#include "loader.cpp"

class RandESUCounter {
private:
    long long sampled_subgraphs;
    long long recursive_steps;
    double sampling_probability;
    std::mt19937 rng;
    std::uniform_real_distribution<double> distribution;

    std::vector<int> get_exclusive_neighborhood(const Graph& G, int u, const std::vector<int>& V_S) {
        return G.get_exclusive_neighborhood(u, V_S);
    }

    void extend_subgraph(std::vector<int>& V_S,
                         std::vector<int>& V_E,
                         int v_root,
                         int k,
                         const Graph& G) {
        recursive_steps++;

        if (V_S.size() == static_cast<size_t>(k)) {
            sampled_subgraphs++;
            return;
        }

        while (!V_E.empty()) {
            int u = V_E.back();
            V_E.pop_back();

            if (distribution(rng) > sampling_probability) {
                continue;
            }

            std::vector<int> V_S_next = V_S;
            V_S_next.push_back(u);

            std::vector<int> N_exc = get_exclusive_neighborhood(G, u, V_S);
            std::vector<int> V_E_next = V_E;
            for (int w : N_exc) {
                if (w > v_root) {
                    V_E_next.push_back(w);
                }
            }

            extend_subgraph(V_S_next, V_E_next, v_root, k, G);
        }
    }

public:
    RandESUCounter(double probability = 0.5, unsigned int seed = std::random_device{}())
        : sampled_subgraphs(0),
          recursive_steps(0),
          sampling_probability(probability),
          rng(seed),
          distribution(0.0, 1.0) {}

    long long count_sampled_subgraphs(const Graph& G, int k) {
        sampled_subgraphs = 0;
        recursive_steps = 0;

        int num_nodes = static_cast<int>(G.get_size());
        for (int v = 0; v < num_nodes; ++v) {
            std::vector<int> V_S = {v};
            std::vector<int> V_E;

            const auto& neighbors = G.get_node(v).get_neighborhood();
            for (int u : neighbors) {
                if (u > v) {
                    V_E.push_back(u);
                }
            }

            extend_subgraph(V_S, V_E, v, k, G);
        }

        return sampled_subgraphs;
    }

    double estimate_total_subgraphs(int k) const {
        if (sampling_probability <= 0.0) {
            return 0.0;
        }

        double scale = std::pow(sampling_probability, std::max(0, k - 1));
        if (scale <= 0.0) {
            return 0.0;
        }

        return static_cast<double>(sampled_subgraphs) / scale;
    }

    long long get_recursive_steps() const {
        return recursive_steps;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 3 || argc > 5) {
        std::cerr << "{\"error\": \"usage: ./rand_esu <graph_file> <subgraph_size_k> [sampling_probability] [seed]\"}" << std::endl;
        return 1;
    }

    std::string graph_file = argv[1];
    int target_k = std::stoi(argv[2]);
    double sampling_probability = argc >= 4 ? std::stod(argv[3]) : 0.5;
    unsigned int seed = argc >= 5 ? static_cast<unsigned int>(std::stoul(argv[4])) : std::random_device{}();

    Graph G = GraphLoader::load_from_file(graph_file, false);
    RandESUCounter rand_esu(sampling_probability, seed);

    long long sum_sampled_subgraphs = 0;
    double sum_estimated_subgraphs = 0.0;
    long long sum_recursive_steps = 0;

    auto start = std::chrono::steady_clock::now();

    if (target_k == 0) {
        for (int k = 1; k <= static_cast<int>(G.get_size()); ++k) {
            // Criar uma nova instancia para cada k garante independencia e reset de estado
            RandESUCounter rand_esu(sampling_probability, seed + k);
            
            long long sampled = rand_esu.count_sampled_subgraphs(G, k);
            double estimated = rand_esu.estimate_total_subgraphs(k);
            
            sum_sampled_subgraphs += sampled;
            sum_estimated_subgraphs += estimated;
            sum_recursive_steps += rand_esu.get_recursive_steps();
        }
    } else {
        sum_sampled_subgraphs = rand_esu.count_sampled_subgraphs(G, target_k);
        sum_estimated_subgraphs = rand_esu.estimate_total_subgraphs(target_k);
        sum_recursive_steps = rand_esu.get_recursive_steps();
    }

    auto end = std::chrono::steady_clock::now();
    std::chrono::duration<double, std::milli> duration = end - start;

    struct rusage usage;
    getrusage(RUSAGE_SELF, &usage);

    double peak_ram_mb = static_cast<double>(usage.ru_maxrss) / 1024.0; // Convert to MB

    std::cout << "{"
              << "\"algorithm\": \"Rand-ESU (C++)\"," 
              << "\"subgraph_size_k\": " << target_k << ","
              << "\"sampling_probability\": " << sampling_probability << ","
              << "\"graph_nodes\": " << G.get_size() << ","
              << "\"graph_edges\": " << G.get_num_edges() << ","
              << "\"sampled_subgraphs\": " << sum_sampled_subgraphs << ","
              << "\"estimated_total_subgraphs\": " << sum_estimated_subgraphs << ","
              << "\"total_subgraphs\": " << sum_estimated_subgraphs << ","
              << "\"recursive_steps\": " << sum_recursive_steps << ","
              << "\"execution_time_ms\": " << duration.count() << ","
              << "\"ram_usage_mb\": " << peak_ram_mb
              << "}" << std::endl;

    return 0;
}
