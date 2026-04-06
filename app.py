import math
import heapq
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Алгоритм Дейкстры", layout="wide")

# ----------------------------
# Настройки
# ----------------------------
N = 7
#VERTICES = [f"V{i}" for i in range(1, N + 1)]
VERTICES = ["Иваново", "Родники", "Вичуга", "Кинешма", "Шуя", "Савино", "Лежнево",]

st.title("Демонстрация алгоритма Дейкстры (Евгений Пеньков 11А)")
# ----------------------------
# Картинка сверху
# ----------------------------
# Положите файл dijkstra.png рядом с app.py
try:
    st.image("Dijkstra1.png", use_container_width=True)
except Exception:
    st.info("Если хотите картинку сверху, положите в проект файл Dijkstra1.png")

st.markdown("Задайте веса рёбер графа, выберите стартовую вершину и получите минимальные расстояния.")
st.markdown(
    """
    **Как заполнять таблицу:**
    - `0` на диагонали
    - положительное число = есть ребро с таким весом
    - `-1` = ребра нет
    - граф считается **неориентированным**, поэтому таблица должна быть симметричной
    """
)

# ----------------------------
# Начальная матрица
# ----------------------------
default_matrix = [
    [0, 7, 9, -1, -1, 14, -1],
    [7, 0, 10, 15, -1, -1, -1],
    [9, 10, 0, 11, -1, 2, -1],
    [-1, 15, 11, 0, 6, -1, -1],
    [-1, -1, -1, 6, 0, 9, 3],
    [14, -1, 2, -1, 9, 0, 12],
    [-1, -1, -1, -1, 3, 12, 0],
]

if "matrix" not in st.session_state:
    st.session_state.matrix = pd.DataFrame(default_matrix, index=VERTICES, columns=VERTICES)

st.subheader("1) Задайте граф")
edited_df = st.data_editor(
    st.session_state.matrix,
    num_rows="fixed",
    use_container_width=True,
    key="editor"
)

# ----------------------------
# Функции
# ----------------------------
def validate_matrix(df: pd.DataFrame):
    errors = []

    # Проверка размеров
    if df.shape != (N, N):
        errors.append("Матрица должна быть размером 7×7.")

    # Проверка чисел
    for i in range(N):
        for j in range(N):
            value = df.iloc[i, j]
            try:
                float(value)
            except Exception:
                errors.append(f"Ячейка ({VERTICES[i]}, {VERTICES[j]}) должна быть числом.")

    # Преобразуем к float
    try:
        m = df.astype(float)
    except Exception:
        return None, errors

    # Диагональ
    for i in range(N):
        if m.iloc[i, i] != 0:
            errors.append(f"На диагонали должно быть 0: {VERTICES[i]} -> {VERTICES[i]}.")

    # Отрицательные веса, кроме -1
    for i in range(N):
        for j in range(N):
            val = m.iloc[i, j]
            if val < 0 and val != -1:
                errors.append(
                    f"Недопустимое значение в ({VERTICES[i]}, {VERTICES[j]}): {val}. "
                    "Используйте положительное число, 0 на диагонали или -1 если ребра нет."
                )

    # Симметрия
    for i in range(N):
        for j in range(N):
            if m.iloc[i, j] != m.iloc[j, i]:
                errors.append(
                    f"Матрица должна быть симметричной для неориентированного графа: "
                    f"{VERTICES[i]}->{VERTICES[j]} и {VERTICES[j]}->{VERTICES[i]}."
                )

    return m, errors


def build_graph_from_matrix(m: pd.DataFrame):
    graph = {v: [] for v in VERTICES}
    edges = []

    for i in range(N):
        for j in range(i + 1, N):
            w = m.iloc[i, j]
            if w != -1 and w != 0:
                u = VERTICES[i]
                v = VERTICES[j]
                graph[u].append((v, w))
                graph[v].append((u, w))
                edges.append((u, v, w))

    return graph, edges


def dijkstra(graph, start):
    dist = {v: math.inf for v in graph}
    dist[start] = 0
    pq = [(0, start)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        if current_dist > dist[u]:
            continue

        for neighbor, weight in graph[u]:
            new_dist = current_dist + weight
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))

    return dist


def make_dot(edges, start_vertex):
    lines = ["graph G {"]
    lines.append('  layout="neato";')
    lines.append('  overlap=false;')
    lines.append('  splines=true;')
    lines.append('  node [shape=circle, style=filled, fillcolor="lightblue", fontsize=18];')

    for v in VERTICES:
        if v == start_vertex:
            lines.append(f'  "{v}" [fillcolor="gold"];')
        else:
            lines.append(f'  "{v}";')

    for u, v, w in edges:
        lines.append(f'  "{u}" -- "{v}" [label="{int(w)}"];')

    lines.append("}")
    return "\n".join(lines)

# ----------------------------
# Выбор стартовой вершины
# ----------------------------
st.subheader("2) Выберите стартовую вершину")
start_vertex = st.selectbox("Стартовая вершина", VERTICES, index=0)

# ----------------------------
# Кнопка расчёта
# ----------------------------
if st.button("Найти минимальные расстояния"):
    matrix, errors = validate_matrix(edited_df)

    if errors:
        st.error("Исправьте ошибки в таблице:")
        for e in errors:
            st.write(f"- {e}")
    else:
        graph, edges = build_graph_from_matrix(matrix)

        if not edges:
            st.warning("В графе нет рёбер.")
        else:
            dist = dijkstra(graph, start_vertex)

            col1, col2 = st.columns([1.2, 1])

            with col1:
                st.subheader("3) Визуализация графа")
                dot = make_dot(edges, start_vertex)
                st.graphviz_chart(dot, use_container_width=True)

            with col2:
                st.subheader("4) Результат")
                result_df = pd.DataFrame({
                    "Вершина": list(dist.keys()),
                    "Минимальное расстояние": [
                        "∞" if math.isinf(d) else int(d) for d in dist.values()
                    ]
                })
                st.dataframe(result_df, use_container_width=True, hide_index=True)

                st.markdown("**Пояснение:**")
                for vertex, d in dist.items():
                    if math.isinf(d):
                        st.write(f"Из {start_vertex} в {vertex}: пути нет")
                    else:
                        st.write(f"Из {start_vertex} в {vertex}: {int(d)}")
