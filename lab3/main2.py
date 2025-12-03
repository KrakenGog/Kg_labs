import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import time
import math

# --- Конфигурация страницы ---
st.set_page_config(page_title="Лаб 3: Растровые алгоритмы", layout="wide")

# --- Логика алгоритмов (возвращают точки и логи) ---
class Algorithms:
    def log(self, msg, logs_list):
        logs_list.append(msg)

    def step_by_step(self, x0, y0, x1, y1):
        points = []
        logs = []
        
        if x0 == x1 and y0 == y1:
            return [(x0, y0)], logs

        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))
        
        self.log(f"dx={dx}, dy={dy}, steps={steps}", logs)

        if abs(dx) >= abs(dy):
            k = dy / dx if dx != 0 else 0
            b = y0 - k * x0
            self.log(f"Ось X основная. k={k:.2f}, b={b:.2f}", logs)
            step = 1 if x1 > x0 else -1
            for x in range(x0, x1 + step, step):
                y = k * x + b
                points.append((x, round(y)))
                self.log(f"x={x}, y={y:.2f} -> round={round(y)}", logs)
        else:
            m = dx / dy
            c = x0 - m * y0
            self.log(f"Ось Y основная. m={m:.2f}, c={c:.2f}", logs)
            step = 1 if y1 > y0 else -1
            for y in range(y0, y1 + step, step):
                x = m * y + c
                points.append((round(x), y))
                self.log(f"y={y}, x={x:.2f} -> round={round(x)}", logs)
        return points, logs

    def dda(self, x0, y0, x1, y1):
        points = []
        logs = []
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy))
        
        if steps == 0: return [(x0, y0)], logs

        x_inc = dx / steps
        y_inc = dy / steps
        
        self.log(f"Steps={steps}, X_inc={x_inc:.2f}, Y_inc={y_inc:.2f}", logs)

        x = x0
        y = y0
        for i in range(steps + 1):
            points.append((round(x), round(y)))
            x += x_inc
            y += y_inc
        return points, logs

    def bresenham_line(self, x0, y0, x1, y1):
        points = []
        logs = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        self.log(f"Init: dx={dx}, dy={dy}, err={err}", logs)

        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1: break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
        return points, logs

    def bresenham_circle(self, xc, yc, r):
        points = []
        logs = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        self.log(f"Circle: R={r}, Init d={d}", logs)

        def get_octant_points(cx, cy, x, y):
            return [
                (cx + x, cy + y), (cx - x, cy + y),
                (cx + x, cy - y), (cx - x, cy - y),
                (cx + y, cy + x), (cx - y, cy + x),
                (cx + y, cy - x), (cx - y, cy - x)
            ]

        while y >= x:
            points.extend(get_octant_points(xc, yc, x, y))
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
        return points, logs

# --- Интерфейс Streamlit ---
st.title("🖥️ Растровые алгоритмы (Streamlit)")

# Сайдбар с настройками
with st.sidebar:
    st.header("Настройки")
    
    # Выбор алгоритма
    alg_type = st.selectbox(
        "Выберите алгоритм",
        ("Пошаговый", "ЦДА (DDA)", "Брезенхем (Линия)", "Брезенхем (Окружность)")
    )
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        x0 = st.number_input("X0 (Начало)", value=-5, step=1)
        y0 = st.number_input("Y0 (Начало)", value=-2, step=1)
    with col2:
        x1 = st.number_input("X1 / Радиус", value=8, step=1)
        y1 = st.number_input("Y1 (Конец)", value=6, step=1)

    if alg_type == "Брезенхем (Окружность)":
        st.info("ℹ️ Для окружности X1 используется как Радиус. Y1 игнорируется.")

    st.divider()
    view_range = st.slider("Масштаб обзора (Range)", 5, 50, 15, help="Насколько далеко видно оси координат")

# Основная логика
algo = Algorithms()
points = []
logs = []
duration = 0

# Запуск алгоритма при изменении любого параметра (Streamlit так работает автоматически)
try:
    start_time = time.perf_counter_ns()
    
    if alg_type == "Пошаговый":
        points, logs = algo.step_by_step(int(x0), int(y0), int(x1), int(y1))
    elif alg_type == "ЦДА (DDA)":
        points, logs = algo.dda(int(x0), int(y0), int(x1), int(y1))
    elif alg_type == "Брезенхем (Линия)":
        points, logs = algo.bresenham_line(int(x0), int(y0), int(x1), int(y1))
    elif alg_type == "Брезенхем (Окружность)":
        r = int(x1)
        if r <= 0:
            st.error("Радиус должен быть > 0")
        else:
            points, logs = algo.bresenham_circle(int(x0), int(y0), r)

    end_time = time.perf_counter_ns()
    duration = (end_time - start_time) / 1000.0  # микросекунды

except Exception as e:
    st.error(f"Ошибка вычислений: {e}")

# --- Отображение результатов ---

# 1. Метрики вверху
m1, m2 = st.columns(2)
m1.metric("Количество пикселей", len(points))
m2.metric("Время расчета", f"{duration:.3f} мкс")

# 2. График (Matplotlib)
fig, ax = plt.subplots(figsize=(8, 8))

# Настройка сетки
ax.grid(True, which='both', color='lightgray', linestyle='-', linewidth=0.5)
ax.axhline(y=0, color='k', linewidth=1) # Ось X
ax.axvline(x=0, color='k', linewidth=1) # Ось Y

# Установка пределов осей (чтобы сетка была красивой)
limit = view_range
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)

# Тики должны быть целочисленными (для визуализации клеток)
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

# Рисуем "пиксели"
# В matplotlib scatter маркер 's' - это квадрат.
# Размер s нужно подбирать.
if points:
    px, py = zip(*points)
    # Рисуем квадраты. s=... зависит от размера графика, примерно подбираем.
    ax.scatter(px, py, c='blue', marker='s', s=150, label='Пиксели', alpha=0.6, edgecolors='black')
    
    # Для наглядности рисуем идеальную линию (красным)
    if "Окружность" not in alg_type and len(points) > 0:
        ax.plot([x0, x1], [y0, y1], 'r--', alpha=0.5, linewidth=1, label='Идеал')

ax.legend()
ax.set_title(f"Визуализация: {alg_type}")
ax.set_xlabel("X")
ax.set_ylabel("Y")

# Вывод графика в Streamlit
st.pyplot(fig)

# 3. Логи и отчет
with st.expander("📋 Открыть лог вычислений (для отчета)"):
    st.text("\n".join(logs))
    st.caption("Скопируйте этот текст в отчет.")