# 🕸️ GraphletArena: Subgraph Counting & Benchmarking

**GraphletArena** is a high-performance benchmarking suite designed for exact and probabilistic subgraph counting (graphlet/motif census) on simple undirected graphs.

The project features a **blazing-fast C++ engine** implementing both **ESU (Exact Subgraph Enumeration)** and **Rand-ESU (Randomized ESU)** algorithms, alongside a **pure Python baseline**, wrapped inside an interactive **Streamlit web dashboard** for comparative analysis.

---

## 🌟 Key Features

* **⚡ C++ Core Engine:** Blazing-fast implementation of ESU (Wernicke, 2005) and Rand-ESU with zero non-essential overhead.
* **🐍 Pure Python ESU Baseline:** Directly compare the algorithmic speedup of C++ vs Python on identical graph structures.
* **🎲 Rand-ESU Sampling Support:** Configurable sampling probability $p$ to estimate subgraph counts on larger networks.
* **📊 Interactive Dashboard (Streamlit):**
    * Visualize graph topologies in real time using interactive network layouts.
    * Compare **Execution Time (ms)**, **Memory Usage (RAM)**, **Recursive Search Steps**, and **Subgraph Census**.


* **📁 Dataset Manager:** Integrated Erdős-Rényi synthetic graph generator and custom Edge-List file loader (`.txt`).
* **🤖 Automated Pipeline:** Auto-compiles C++ binaries directly from Python runners.

---

## 📂 Project Structure

```text
subgraph-comp/
├── bin
│   ├── esu_counter
│   └── rand_esu_counter
├── datasets
│   ├── ds5.txt
│   └── ds20.txt
├── cpp
│   ├── esu.cpp
│   ├── graph.cpp
│   ├── loader.cpp
│   ├── node.cpp
│   └── rand_esu.cpp
├── python
│   ├── esu.py
│   └── rand_esu.py
├── app.py
├── benchmark_runner.py
├── README.md
└── requirements.txt

```

---

## 🛠️ Prerequisites & Setup

### 1. Requirements

* **G++ Compiler** with C++17 support (`g++`)
* **Python 3.9+**

### 2. Environment Setup

Clone the repository and navigate to the project root:

```bash
cd subgraph-comp

```

Create a virtual environment (`.venv`) and activate it:

```bash
# On Linux / macOS:
python3 -m venv .venv
source .venv/bin/activate

# On Windows:
python -m venv .venv
.venv\Scripts\activate

```

### 3. Install Dependencies

Install all required Python packages:

```bash
pip install -r requirements.txt

```

---

## 🚀 How to Run

### Launch the Interactive Web Dashboard (Streamlit)

To start the full GUI dashboard in your browser:

```bash
streamlit run app.py

```

1. Open the local URL provided by Streamlit (usually `http://localhost:8501`).
2. Select or generate a graph dataset in the **Main dashboard**.
3. Choose algorithms and subgraph size $k$ ($k=0$ calculates all sizes).
4. Click **Run benchmarks** and switch to **Charts and metrics** for charts and analytics!

---

## 🔬 Benchmark Metrics Collected

| Metric | Description |
| --- | --- |
| **Execution Time (ms)** | Total duration to complete the subgraph search. |
| **RAM Usage (MB)** | Memory consumed during processing (measured via `psutil`). |
| **Recursive Steps** | Total number of search tree nodes explored during backtracking. |
| **Total Subgraphs** | Exact count (or Monte Carlo estimate) of induced connected $k$-subgraphs. |






# 🕸️ GraphletArena: Subgraph Counting & Benchmarking Suite

[![C++17](https://img.shields.io/badge/C++-17-blue.svg)](https://en.cppreference.com/w/cpp/17)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-yellow.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**GraphletArena** is an open-source, high-performance benchmarking suite engineered for exact and probabilistic subgraph counting (network motifs and graphlet census) on simple undirected graphs.

This repository serves as a reproducible experimental testbed comparing core algorithms implemented in **C++17** and **pure Python 3**, complete with an interactive **Streamlit analytics dashboard**.

---

## 📌 Algorithmic Core & Foundations

The core algorithms implemented in GraphletArena follow the exact subgraph enumeration taxomony described in literature:

1. **ESU (Exact Subgraph Enumeration)** (*Wernicke, 2005*):
   - Backtracking search tree exploration for induced $k$-subgraphs.
   - **Symmetry Breaking:** Enforces vertex labeling constraints $L(w) > L(v_{root})$ to eliminate duplicate subgraph enumeration.
   - **Exclusive Neighborhood $N_{exc}(u, V_S)$:** Dynamically tracks candidate expansion nodes while preventing redundant traversal.

2. **Rand-ESU (Randomized ESU)** (*Wernicke, 2006*):
   - Unbiased probabilistic estimator for subgraph counts in large-scale networks.
   - Configurable sampling probability $p \in (0, 1]$ per recursion depth level.

---

## ⚡ Features & Analytics

- **Core Engines:** Blazing-fast C++17 engine vs. Pure Python baseline.
- **System Metrics Tracked:**
  - Execution Time ($\text{ms}$)
  - Peak Memory Usage / Memory Delta ($\text{MB}$ via `psutil`)
  - Total Search Tree Traversal Steps (`recursive_steps`)
  - Subgraph Census ($k$-subgraph exact/estimated count)
- **Node Scaling Analysis:** Automated scaling experiments across varying graph order $\vert{}V\vert{}$ and edge density $p$.
- **Interactive Dashboard:** Built with Streamlit, Plotly, and NetworkX for real-time visual graph representation and metric comparison.
- **Data Export:** Export detailed benchmark logs to CSV/JSON format.

---

## 📂 Repository Architecture

```text
graphlet-arena/
├── app.py                   # Streamlit interactive GUI dashboard
├── benchmark_runner.py      # Automated orchestrator & psutil profiler
├── bin/                     # Compiled C++ binaries (auto-built)
├── cpp/                     # C++17 Engine Source Code
│   ├── esu.cpp              # Exact ESU implementation
│   ├── rand_esu.cpp         # Randomized ESU implementation
│   ├── graph.cpp            # Graph adjacency and $N_{exc}$ computations
│   ├── loader.cpp           # Fast edge-list loader
│   └── node.cpp             # Node & neighborhood abstraction
├── python/                  # Pure Python Baseline
│   ├── esu.py               # Pure Python ESU implementation
│   └── rand_esu.py          # Pure Python Rand-ESU implementation
├── datasets/                # Synthetic and real network edge-lists
└── requirements.txt         # Python dependency definitions

```

---

## 🛠️ Quick Start

### 1. Prerequisites

* **C++ Compiler:** `g++` with C++17 support.
* **Python:** Version 3.9 or higher.

### 2. Setup Environment

```bash
git clone https://github.com/Joao17Junior/subgraph-comp.git # Via HTTP
git clone git@github.com:Joao17Junior/subgraph-comp.git # Via SSH

cd subgraph-comp

python3 -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run Interactive Dashboard

```bash
streamlit run app.py
```

---

## 🎯 Alignment with INESC TEC Research (BII AE2026-0234)

This project was developed as a preliminary research prototype aligned with the research goals of the INESC TEC project on Subgraph Counting (*Ribeiro et al., ACM Computing Surveys, 2021*).

**Future Roadmap:**

* [ ] Integration of Prefix-Tree based algorithms (**GTrie**, **FaSE**).
* [ ] Benchmark integration for additional exact algorithms (**Kavosh**, **ORCA**, **PGD**, **ESCAPE**).
* [ ] Evaluation on real-world biological and social network datasets.

---

## 📜 References

* **Ribeiro, P., et al.** (2021). *A Survey on Subgraph Counting: Concepts, Algorithms and Applications to Network Motifs and Graphlets*. ACM Computing Surveys (CSUR), 54(2), 1-36.
* **Wernicke, S.** (2006). *Efficient enumeration of induced subgraphs*. IEEE/ACM Transactions on Computational Biology and Bioinformatics, 3(2), 104-119.
