import os
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

# Import the benchmark orchestrator.
from benchmark_runner import (
    compile_cpp,
    gen_random_graph,
    load_graph_from_txt,
    run_cpp_esu,
    run_rand_cpp_esu,
    run_rand_python_esu,
    run_python_esu,
    DATASETS_DIR
)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Graphlet Arena",
    page_icon=":material/analytics:",
    layout="wide"
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --bg: #050608;
    --bg-elevated: #0b1117;
    --bg-surface: #0f1720;
    --bg-surface-2: #111f28;
    --petrol: #2aa9a1;
    --petrol-strong: #1f6f78;
    --petrol-soft: rgba(42, 169, 161, 0.16);
    --text: #f5fbff;
    --muted: #9fb1bb;
    --border: rgba(122, 177, 186, 0.18);
    --shadow: 0 24px 80px rgba(0, 0, 0, 0.42);
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background:
        radial-gradient(circle at top left, rgba(42, 169, 161, 0.10), transparent 35%),
        radial-gradient(circle at top right, rgba(31, 111, 120, 0.18), transparent 28%),
        linear-gradient(180deg, #050608 0%, #090d11 42%, #050608 100%);
    color: var(--text);
    font-family: 'Inter', sans-serif;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071016 0%, #091319 100%);
    border-right: 1px solid var(--border);
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2.5rem;
}

h1, h2, h3, h4, h5 {
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: -0.035em;
    color: var(--text);
}

p, label, span, div, input, textarea, button {
    font-family: 'Inter', sans-serif;
}

.eyebrow {
    color: var(--petrol);
    font-family: 'IBM Plex Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.24em;
    font-size: 0.72rem;
    margin-bottom: 0.4rem;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.3rem, 4.5vw, 4.4rem);
    line-height: 0.98;
    font-weight: 700;
    color: var(--text);
    margin: 0;
}

.hero-subtitle {
    margin-top: 0.8rem;
    max-width: 760px;
    color: var(--muted);
    font-size: 1rem;
    line-height: 1.7;
}

[data-testid="stContainer"] {
    color: var(--text);
}

[data-testid="stContainer"] > div {
    border-color: var(--border);
}

[data-testid="stButton"] button {
    background: linear-gradient(135deg, var(--petrol), var(--petrol-strong));
    color: #f5fbff;
    border: 1px solid rgba(122, 177, 186, 0.26);
    border-radius: 16px;
    font-weight: 700;
    box-shadow: 0 12px 32px rgba(31, 111, 120, 0.22);
    transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
}

[data-testid="stButton"] button:hover {
    transform: translateY(-1px);
    border-color: rgba(123, 231, 223, 0.62);
    box-shadow: 0 16px 40px rgba(31, 111, 120, 0.28);
}

[data-testid="stButton"] button:active {
    transform: translateY(0);
}

[data-testid="stMetric"] {
    background: rgba(15, 23, 32, 0.72);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 18px;
    overflow: hidden;
    box-shadow: var(--shadow);
}

[data-baseweb="tab-list"] {
    gap: 0.5rem;
}

[data-baseweb="tab"] {
    background: rgba(15, 23, 32, 0.72);
    border: 1px solid var(--border);
    border-radius: 999px;
    padding: 0.55rem 1rem;
    color: var(--muted);
}

[data-baseweb="tab"][aria-selected="true"] {
    color: var(--text);
    border-color: rgba(42, 169, 161, 0.45);
    background: linear-gradient(135deg, rgba(42, 169, 161, 0.22), rgba(31, 111, 120, 0.16));
}

[data-testid="stSelectbox"] div[data-baseweb="select"],
[data-testid="stMultiSelect"] div[data-baseweb="select"],
[data-testid="stRadio"] div[role="radiogroup"],
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input,
[data-testid="stSlider"] {
    color: var(--text);
}

[data-testid="stAlert"] {
    border-radius: 16px;
    border: 1px solid var(--border);
    background: rgba(15, 23, 32, 0.8);
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Ensure initial C++ compilation and datasets folder exist.
compile_cpp()
os.makedirs(DATASETS_DIR, exist_ok=True)

# Session state initialization.
if "benchmark_results" not in st.session_state:
    st.session_state["benchmark_results"] = None
if "scaling_results" not in st.session_state:
    st.session_state["scaling_results"] = None
if "current_graph_details" not in st.session_state:
    st.session_state["current_graph_details"] = None
if "current_graph" not in st.session_state:
    st.session_state["current_graph"] = None
if "current_graph_path" not in st.session_state:
    st.session_state["current_graph_path"] = None
if "current_graph_name" not in st.session_state:
    st.session_state["current_graph_name"] = None
if "graph_source_mode" not in st.session_state:
    st.session_state["graph_source_mode"] = "Use an existing dataset"
if "existing_dataset_choice" not in st.session_state:
    st.session_state["existing_dataset_choice"] = None


PALETTE = ["#2aa9a1", "#1f6f78", "#79d6cf", "#7be7df", "#e6f4f1", "#0b1117"]
GRID_COLOR = "rgba(159, 177, 187, 0.12)"
TEXT_COLOR = "#f5fbff"


def style_plotly_figure(fig: go.Figure, *, height: int = 360) -> go.Figure:
    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=TEXT_COLOR),
        title=dict(font=dict(family="Space Grotesk, sans-serif", color=TEXT_COLOR, size=20)),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,0)",
            font=dict(color=TEXT_COLOR),
        ),
        margin=dict(l=12, r=12, t=64, b=12),
    )
    fig.update_xaxes(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))
    fig.update_yaxes(gridcolor=GRID_COLOR, zeroline=False, linecolor=GRID_COLOR, tickfont=dict(color=TEXT_COLOR))
    return fig


# --- GRAPH RENDERING WITH PLOTLY ---
def plot_network_graph(G: nx.Graph):
    pos = nx.spring_layout(G, seed=42)
    
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.2, color='#35545a'),
        hoverinfo='none',
        mode='lines'
    )

    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        text=[str(node) for node in G.nodes()],
        textposition="top center",
        marker=dict(
            showscale=False,
            color='#2aa9a1',
            size=17,
            line=dict(color='#f5fbff', width=1.5)
        )
    )

    fig = go.Figure(
        data=[edge_trace, node_trace],
        layout=go.Layout(
            showlegend=False,
            hovermode='closest',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(b=0, l=0, r=0, t=0),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=420,
            font=dict(color=TEXT_COLOR, family='Inter, sans-serif')
        )
    )
    return fig


def set_current_graph(graph: nx.Graph, path: str) -> None:
    st.session_state["current_graph"] = graph
    st.session_state["current_graph_path"] = path
    st.session_state["current_graph_name"] = os.path.basename(path)


def sync_existing_dataset_choice(chosen_file: str) -> None:
    selected_path = os.path.join(DATASETS_DIR, chosen_file)
    graph = load_graph_from_txt(selected_path)
    set_current_graph(graph, selected_path)


# --- HERO ---
with st.container(border=True):
    st.markdown('<div class="eyebrow">Graphlet Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-title">Subgraph Benchmarking</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Compare exact and randomized subgraph enumeration algorithms across custom datasets, multiple k-sizes, and node scale limits.</div>',
        unsafe_allow_html=True,
    )

# --- TABS / NAVIGATION ---
tab_main, tab_scaling, tab_charts = st.tabs(["Main dashboard", "Node scaling benchmark", "Charts and metrics"])

# ==============================================================================
# SECTION 1: MAIN DASHBOARD
# ==============================================================================
with tab_main:
    control_col, preview_col = st.columns([0.95, 1.05], gap="medium")

    with control_col:
        with st.container(border=True):
            st.subheader("Graph generation panel")

            mode = st.segmented_control(
                "Graph source",
                ["Use an existing dataset", "Generate a random graph"],
                default=st.session_state["graph_source_mode"],
            )
            st.session_state["graph_source_mode"] = mode

            if mode == "Use an existing dataset":
                existing_files = [f for f in os.listdir(DATASETS_DIR) if f.endswith(".txt")]
                if not existing_files:
                    st.warning("No dataset was found in the datasets folder. Generate a new graph below.")
                else:
                    chosen_file = st.selectbox(
                        "Select a file",
                        existing_files,
                        index=existing_files.index(st.session_state["existing_dataset_choice"]) if st.session_state["existing_dataset_choice"] in existing_files else 0,
                    )
                    st.session_state["existing_dataset_choice"] = chosen_file
                    sync_existing_dataset_choice(chosen_file)

            else:
                with st.form("gen_graph_form"):
                    n_nodes = st.number_input("Number of nodes (|V|)", min_value=3, max_value=500, value=15)
                    p_prob = st.slider("Edge probability (p)", min_value=0.01, max_value=1.0, value=0.2)
                    filename_input = st.text_input("File name", value=f"random_n{n_nodes}")
                    submit_gen = st.form_submit_button("Generate graph")

                    if submit_gen:
                        generated_graph, generated_path = gen_random_graph(n_nodes, p_prob, filename_input)
                        set_current_graph(generated_graph, generated_path)
                        st.success(f"Graph generated and saved to {generated_path}.")

        st.space("small")

        with st.container(border=True):
            st.subheader("Benchmark panel")

            selected_algos = st.multiselect(
                "Select the algorithms to run",
                ["ESU (C++)", "ESU (Python)", "Rand-ESU (C++)", "Rand-ESU (Python)"],
                default=["ESU (C++)", "ESU (Python)"],
            )

            rand_sampling_probability = st.slider(
                "Rand-ESU sampling probability",
                min_value=0.05,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Used only for the Rand-ESU variants. Lower values sample fewer branches and run faster.",
            )

            rand_seed = st.number_input(
                "Rand-ESU random seed",
                min_value=0,
                value=42,
                step=1,
                help="Used only for the Rand-ESU variants to keep sampling repeatable.",
            )

            # --- MULTI-K SELECTION ---
            selected_ks = st.multiselect(
                "Subgraph size(s) k (select multiple or 0 for all sizes)",
                options=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                default=[3],
                help="Select one or multiple values of k to evaluate. k = 0 evaluates all sizes up to |V|.",
            )

            st.space("small")
            run_button = st.button("Run benchmarks", type="primary", width="stretch")

    with preview_col:
        with st.container(border=True):
            st.subheader("Dataset preview")

            current_G = st.session_state["current_graph"]
            current_graph_path = st.session_state["current_graph_path"]

            if current_G is not None:
                metric_col1, metric_col2, metric_col3 = st.columns(3)
                metric_col1.metric("Nodes", current_G.number_of_nodes())
                metric_col2.metric("Edges", current_G.number_of_edges())
                metric_col3.metric("Source", st.session_state["current_graph_name"] or "Selected dataset")

                st.plotly_chart(style_plotly_figure(plot_network_graph(current_G), height=420), width="stretch")
                if current_graph_path:
                    st.caption(f"Current graph file: {current_graph_path}")
            else:
                st.caption("Select or generate a graph to preview it here.")

    if run_button:
        if not selected_algos:
            st.error("Select at least one algorithm.")
        elif not selected_ks:
            st.error("Select at least one subgraph size k.")
        elif st.session_state["current_graph"] is None or st.session_state["current_graph_path"] is None:
            st.error("Select or generate a valid graph first.")
        else:
            results = []
            with st.spinner("Running benchmarks across selected algorithms and k-values..."):
                for k_val in selected_ks:
                    if "ESU (C++)" in selected_algos:
                        res_cpp = run_cpp_esu(st.session_state["current_graph_path"], k=k_val)
                        results.append(res_cpp)
                    
                    if "ESU (Python)" in selected_algos:
                        res_py = run_python_esu(st.session_state["current_graph"], k=k_val)
                        results.append(res_py)

                    if "Rand-ESU (C++)" in selected_algos:
                        res_rand_cpp = run_rand_cpp_esu(
                            st.session_state["current_graph_path"],
                            k=k_val,
                            sampling_probability=rand_sampling_probability,
                            seed=int(rand_seed),
                        )
                        results.append(res_rand_cpp)

                    if "Rand-ESU (Python)" in selected_algos:
                        res_rand_py = run_rand_python_esu(
                            st.session_state["current_graph"],
                            k=k_val,
                            sampling_probability=rand_sampling_probability,
                            seed=int(rand_seed),
                        )
                        results.append(res_rand_py)

            df_temp = pd.DataFrame(results)
            # Create a composite display label for grouping algorithms with k
            df_temp["label_algo_k"] = df_temp["algorithm"] + " (k=" + df_temp["subgraph_size_k"].astype(str) + ")"

            st.session_state["benchmark_results"] = df_temp
            st.session_state["current_graph_details"] = {
                "nodes": st.session_state["current_graph"].number_of_nodes(),
                "edges": st.session_state["current_graph"].number_of_edges(),
                "ks": selected_ks,
                "file": st.session_state["current_graph_name"] or os.path.basename(st.session_state["current_graph_path"]),
                "sampling_probability": rand_sampling_probability if any("Rand-ESU" in algo for algo in selected_algos) else None,
            }
            st.success("Benchmark finished. Open the Charts and metrics tab to inspect the results.")


# ==============================================================================
# SECTION 2: NODE SCALING BENCHMARK (FEATURE 3)
# ==============================================================================
with tab_scaling:
    st.subheader("📈 Node Scaling & Execution Curve Analysis")
    st.caption("Evaluate how algorithms scale as the graph size |V| increases.")

    with st.container(border=True):
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            scale_min_n = st.number_input("Min nodes (|V|_min)", min_value=5, max_value=200, value=10, step=5)
            scale_max_n = st.number_input("Max nodes (|V|_max)", min_value=10, max_value=500, value=40, step=10)
            scale_step_n = st.number_input("Step size", min_value=1, max_value=50, value=10)
        with col_s2:
            scale_p = st.slider("Edge probability (p)", min_value=0.05, max_value=1.0, value=0.15, step=0.05)
            scale_k = st.number_input("Subgraph size k for scaling", min_value=1, max_value=10, value=3)
        with col_s3:
            scale_algos = st.multiselect(
                "Algorithms to evaluate",
                ["ESU (C++)", "ESU (Python)", "Rand-ESU (C++)", "Rand-ESU (Python)"],
                default=["ESU (C++)", "ESU (Python)"],
            )
            scale_prob = st.slider("Rand-ESU p (if selected)", min_value=0.05, max_value=1.0, value=0.5, step=0.05)

        run_scale_btn = st.button("🚀 Run Scaling Analysis", type="primary", width="stretch")

    if run_scale_btn:
        if scale_min_n >= scale_max_n:
            st.error("Min nodes must be smaller than Max nodes.")
        elif not scale_algos:
            st.error("Select at least one algorithm.")
        else:
            scale_results = []
            node_range = list(range(int(scale_min_n), int(scale_max_n) + 1, int(scale_step_n)))
            progress_bar = st.progress(0)
            
            for idx, n in enumerate(node_range):
                g, path = gen_random_graph(n, scale_p, f"scale_n{n}")
                
                if "ESU (C++)" in scale_algos:
                    r = run_cpp_esu(path, k=scale_k)
                    r["graph_nodes"] = n
                    scale_results.append(r)
                if "ESU (Python)" in scale_algos:
                    r = run_python_esu(g, k=scale_k)
                    r["graph_nodes"] = n
                    scale_results.append(r)
                if "Rand-ESU (C++)" in scale_algos:
                    r = run_rand_cpp_esu(path, k=scale_k, sampling_probability=scale_prob, seed=42)
                    r["graph_nodes"] = n
                    scale_results.append(r)
                if "Rand-ESU (Python)" in scale_algos:
                    r = run_rand_python_esu(g, k=scale_k, sampling_probability=scale_prob, seed=42)
                    r["graph_nodes"] = n
                    scale_results.append(r)
                
                progress_bar.progress((idx + 1) / len(node_range))

            st.session_state["scaling_results"] = pd.DataFrame(scale_results)
            st.success("Scaling benchmark completed!")

    df_scale = st.session_state["scaling_results"]
    if df_scale is not None and not df_scale.empty:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_time_line = px.line(
                df_scale, x="graph_nodes", y="execution_time_ms", color="algorithm",
                markers=True, title="Execution Time (ms) vs. Number of Nodes (|V|)",
                color_discrete_sequence=PALETTE
            )
            st.plotly_chart(style_plotly_figure(fig_time_line, height=400), width="stretch")

        with col_c2:
            fig_ram_line = px.line(
                df_scale, x="graph_nodes", y="ram_usage_mb", color="algorithm",
                markers=True, title="RAM Usage (MB) vs. Number of Nodes (|V|)",
                color_discrete_sequence=PALETTE
            )
            st.plotly_chart(style_plotly_figure(fig_ram_line, height=400), width="stretch")

        # --- FEATURE 4: DOWNLOAD SCALING RESULTS ---
        st.subheader("📥 Export Scaling Data")
        sc_csv, sc_json = st.columns(2)
        with sc_csv:
            st.download_button(
                "Download Scaling Results (CSV)",
                data=df_scale.to_csv(index=False).encode('utf-8'),
                file_name="scaling_benchmark_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with sc_json:
            st.download_button(
                "Download Scaling Results (JSON)",
                data=df_scale.to_json(orient="records", indent=2),
                file_name="scaling_benchmark_results.json",
                mime="application/json",
                use_container_width=True
            )


# ==============================================================================
# SECTION 3: CHARTS AND METRICS PAGE
# ==============================================================================
with tab_charts:
    df_res = st.session_state["benchmark_results"]
    details = st.session_state["current_graph_details"]

    if df_res is None or df_res.empty:
        st.caption("Run your first comparison from the Main dashboard to see the charts here.")
    else:
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.subheader("Performance comparison")
        with header_col2:
            with st.popover("View graph details"):
                st.markdown(f"""
                **File:** {details['file']}  
                **Nodes (|V|):** {details['nodes']}  
                **Edges (|E|):** {details['edges']}  
                **k values used:** {details['ks']}
                """)
                if details.get("sampling_probability") is not None:
                    st.markdown(f"**Rand-ESU sampling probability:** {details['sampling_probability']}")

        chart_view = st.radio(
            "Chart view",
            ["Overview", "Single metric"],
            horizontal=True
        )

        metrics_map = {
            "execution_time_ms": "Execution time (ms)",
            "ram_usage_mb": "RAM usage (MB)",
            "recursive_steps": "Recursive steps",
            "total_subgraphs": "Total subgraphs",
            "estimated_total_subgraphs": "Estimated total subgraphs",
            "sampled_subgraphs": "Sampled subgraphs",
            "sampling_probability": "Sampling probability",
        }

        if chart_view == "Overview":
            c1, c2 = st.columns(2)
            
            with c1:
                fig_time = px.bar(
                    df_res,
                    x="label_algo_k",
                    y="execution_time_ms",
                    color="algorithm",
                    title="Execution time (ms) - lower is better",
                    text_auto='.2f',
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(style_plotly_figure(fig_time, height=360), width="stretch")

                fig_ram = px.bar(
                    df_res,
                    x="label_algo_k",
                    y="ram_usage_mb",
                    color="algorithm",
                    title="RAM usage (MB) - lower is better",
                    text_auto='.3f',
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(style_plotly_figure(fig_ram, height=360), width="stretch")

            with c2:
                fig_steps = px.bar(
                    df_res,
                    x="label_algo_k",
                    y="recursive_steps",
                    color="algorithm",
                    title="Recursive steps in search tree",
                    text_auto=True,
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(style_plotly_figure(fig_steps, height=360), width="stretch")

                fig_subs = px.bar(
                    df_res,
                    x="label_algo_k",
                    y="total_subgraphs",
                    color="algorithm",
                    title="Total subgraphs found",
                    text_auto=True,
                    color_discrete_sequence=PALETTE,
                )
                st.plotly_chart(style_plotly_figure(fig_subs, height=360), width="stretch")

        else:
            selected_metric_key = st.selectbox(
                "Select a metric",
                options=list(metrics_map.keys()),
                format_func=lambda x: metrics_map[x]
            )

            fig_single = px.bar(
                df_res, x="label_algo_k", y=selected_metric_key, color="algorithm",
                title=f"Comparison: {metrics_map[selected_metric_key]}",
                text_auto=True,
                color_discrete_sequence=PALETTE
            )
            st.plotly_chart(style_plotly_figure(fig_single, height=420), width="stretch")

        st.subheader("Results table")
        summary_columns = [
            "algorithm",
            "subgraph_size_k",
            "execution_time_ms",
            "ram_usage_mb",
            "recursive_steps",
            "total_subgraphs",
            "estimated_total_subgraphs",
            "sampled_subgraphs",
            "sampling_probability",
        ]
        summary_columns = [column for column in summary_columns if column in df_res.columns]
        st.dataframe(
            df_res[summary_columns].rename(columns=metrics_map),
            width="stretch",
            hide_index=True
        )

        # --- FEATURE 4: EXPORT BENCHMARK DATA (CSV / JSON) ---
        st.subheader("📥 Export Benchmark Data")
        dl_col1, dl_col2 = st.columns(2)
        with dl_col1:
            st.download_button(
                label="Download Results (CSV)",
                data=df_res.to_csv(index=False).encode('utf-8'),
                file_name="subgraph_benchmark_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with dl_col2:
            st.download_button(
                label="Download Results (JSON)",
                data=df_res.to_json(orient="records", indent=2),
                file_name="subgraph_benchmark_results.json",
                mime="application/json",
                use_container_width=True
            )