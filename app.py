import os
import streamlit as st
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import plotly.express as px

# Importa o orquestrador de benchmarks
from benchmark_runner import (
    compile_cpp,
    gen_random_graph,
    load_graph_from_txt,
    run_cpp_esu,
    run_python_esu,
    DATASETS_DIR
)

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="GraphletArena",
    page_icon="🕸️",
    layout="wide"
)

# Garantir compilação inicial do C++ e existência da pasta datasets/
compile_cpp()
os.makedirs(DATASETS_DIR, exist_ok=True)

# Estado da sessão para guardar resultados do benchmark
if "benchmark_results" not in st.session_state:
    st.session_state["benchmark_results"] = None
if "current_graph_details" not in st.session_state:
    st.session_state["current_graph_details"] = None


# --- FUNÇÃO PARA DESENHAR O GRAFO COM PLOTLY ---
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
        line=dict(width=1, color='#888'),
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
            colorscale='YlGnBu',
            color='#1f77b4',
            size=16,
            line_width=2
        )
    )

    fig = go.Figure(data=[edge_trace, node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0, l=0, r=0, t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=380
                   ))
    return fig


# --- TITULO PRINCIPAL ---
st.title("🕸️ GraphletArena")
st.caption("Plataforma de Benchmarking para Contagem Exata de Subgrafos (C++ vs Python)")

# --- ABAS / NAVEGAÇÃO ---
tab_main, tab_charts = st.tabs(["🎮 Painel Principal", "📊 Gráficos & Métricas"])

# ==============================================================================
# SEGMENTO 1: PÁGINA PRINCIPAL
# ==============================================================================
with tab_main:
    col_left, col_right = st.columns([1, 1], gap="medium")

    with col_left:
        st.subheader("1. Seleção / Geração do Dataset")
        
        mode = st.radio("Origem do Grafo:", ["Escolher Existente", "Gerar Novo Grafo Aleatório"], horizontal=True)
        
        selected_file_path = None
        current_G = None

        if mode == "Escolher Existente":
            existing_files = [f for f in os.listdir(DATASETS_DIR) if f.endswith(".txt")]
            if not existing_files:
                st.warning("Nenhum dataset encontrado na pasta `datasets/`. Gere um novo grafo ao lado!")
            else:
                chosen_file = st.selectbox("Selecione o ficheiro:", existing_files)
                selected_file_path = os.path.join(DATASETS_DIR, chosen_file)
                current_G = load_graph_from_txt(selected_file_path)

        else:
            with st.form("gen_graph_form"):
                n_nodes = st.number_input("Número de Nós (|V|):", min_value=3, max_value=500, value=15)
                p_prob = st.slider("Probabilidade de Aresta (p):", min_value=0.01, max_value=1.0, value=0.2)
                filename_input = st.text_input("Nome do Ficheiro:", value=f"random_n{n_nodes}")
                submit_gen = st.form_submit_button("🔨 Gerar Grafo")

                if submit_gen:
                    current_G, selected_file_path = gen_random_graph(n_nodes, p_prob, filename_input)
                    st.success(f"Grafo gerado e guardado em `{selected_file_path}`!")

        st.divider()

        st.subheader("2. Configuração do Benchmark")
        
        # Seleção dos Algoritmos
        selected_algos = st.multiselect(
            "Selecione os Algoritmos a Executar:",
            ["ESU (C++)", "ESU (Python)"],
            default=["ESU (C++)", "ESU (Python)"]
        )

        # Seleção do valor de k
        k_val = st.number_input(
            "Tamanho do Subgrafo (k) [Use 0 para calcular todos]:",
            min_value=0, max_value=10, value=3,
            help="k=3 conta triângulos e caminhos. k=0 executa iterativamente para todo o k <= |V|."
        )

        st.write("")
        run_button = st.button("🚀 Correr Benchmarks", type="primary", use_container_width=True)

    with col_right:
        st.subheader("Visualização do Dataset")
        if current_G is not None:
            st.plotly_chart(plot_network_graph(current_G), use_container_width=True)
            st.info(f"📍 **Grafo Atual:** {current_G.number_of_nodes()} Nós | {current_G.number_of_edges()} Arestas")
        else:
            st.info("Selecione ou gere um grafo para visualizar a rede aqui.")

    # --- LÓGICA AO CLICAR NO BOTÃO ---
    if run_button:
        if not selected_algos:
            st.error("Por favor selecione pelo menos um algoritmo!")
        elif selected_file_path is None or not os.path.exists(selected_file_path):
            st.error("Por favor selecione ou gere um grafo válido primeiro!")
        else:
            results = []
            with st.spinner("A executar benchmarks..."):
                if "ESU (C++)" in selected_algos:
                    res_cpp = run_cpp_esu(selected_file_path, k=k_val)
                    results.append(res_cpp)
                
                if "ESU (Python)" in selected_algos:
                    res_py = run_python_esu(current_G, k=k_val)
                    results.append(res_py)

            # Guardar no session state
            st.session_state["benchmark_results"] = pd.DataFrame(results)
            st.session_state["current_graph_details"] = {
                "nodes": current_G.number_of_nodes(),
                "edges": current_G.number_of_edges(),
                "k": k_val,
                "file": os.path.basename(selected_file_path)
            }
            st.success("Benchmark concluído! Mude para a aba '📊 Gráficos & Métricas' para ver os resultados.")


# ==============================================================================
# SEGMENTO 2: PÁGINA DE GRÁFICOS E MÉTRICAS
# ==============================================================================
with tab_charts:
    df_res = st.session_state["benchmark_results"]
    details = st.session_state["current_graph_details"]

    if df_res is None or df_res.empty:
        st.write("")
        st.info("💡 **Faça a primeira comparação** no Painel Principal para visualizar aqui os gráficos de desempenho.")
    else:
        # Cabeçalho com o Popover "Ver detalhes do Grafo"
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.subheader("📈 Comparativo de Desempenho")
        with header_col2:
            with st.popover("🔍 Ver detalhes do Grafo"):
                st.markdown(f"""
                **Ficheiro:** `{details['file']}`  
                **Tamanho (|V|):** {details['nodes']} nós  
                **Arestas (|E|):** {details['edges']} conexões  
                **Valor de k usado:** `{details['k']}`
                """)

        st.divider()

        # Seleção de Modo de Visualização dos Gráficos
        chart_view = st.radio(
            "Modo de Visualização:",
            ["Painel Geral (Todas as Métricas)", "Métrica Individual"],
            horizontal=True
        )

        metrics_map = {
            "execution_time_ms": "Tempo de Execução (ms)",
            "ram_usage_mb": "Uso de Memória RAM (MB)",
            "recursive_steps": "Passos Recursivos",
            "total_subgraphs": "Total de Subgrafos"
        }

        if chart_view == "Painel Geral (Todas as Métricas)":
            c1, c2 = st.columns(2)
            
            with c1:
                fig_time = px.bar(df_res, x="algorithm", y="execution_time_ms", color="algorithm",
                                  title="⏱️ Tempo de Execução (ms) [Menor é Melhor]", text_auto='.2f')
                st.plotly_chart(fig_time, use_container_width=True)

                fig_ram = px.bar(df_res, x="algorithm", y="ram_usage_mb", color="algorithm",
                                 title="💾 Uso de Memória RAM (MB) [Menor é Melhor]", text_auto='.3f')
                st.plotly_chart(fig_ram, use_container_width=True)

            with c2:
                fig_steps = px.bar(df_res, x="algorithm", y="recursive_steps", color="algorithm",
                                   title="🌳 Passos Recursivos (Árvore de Procura)", text_auto=True)
                st.plotly_chart(fig_steps, use_container_width=True)

                fig_subs = px.bar(df_res, x="algorithm", y="total_subgraphs", color="algorithm",
                                  title="🔢 Total de Subgrafos Encontrados", text_auto=True)
                st.plotly_chart(fig_subs, use_container_width=True)

        else:
            selected_metric_key = st.selectbox(
                "Selecione a Métrica a Analisar:",
                options=list(metrics_map.keys()),
                format_func=lambda x: metrics_map[x]
            )

            fig_single = px.bar(
                df_res, x="algorithm", y=selected_metric_key, color="algorithm",
                title=f"Comparativo: {metrics_map[selected_metric_key]}",
                text_auto=True
            )
            st.plotly_chart(fig_single, use_container_width=True)

        # Tabela Resumo com os dados brutos
        st.subheader("📋 Tabela Resumo de Dados")
        st.dataframe(
            df_res[["algorithm", "execution_time_ms", "ram_usage_mb", "recursive_steps", "total_subgraphs"]].rename(
                columns=metrics_map
            ),
            use_container_width=True
        )