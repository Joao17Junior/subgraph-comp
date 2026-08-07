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
