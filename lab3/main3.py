import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import numpy as np  # Нужно для генерации сетки
import time

# --- Конфигурация страницы ---
st.set_page_config(page_title="Лаб 3: Растровые алгоритмы", layout="wide")

# --- Логика алгоритмов (БЕЗ ИЗМЕНЕНИЙ) ---
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
st.title("🖥️ Растровые алгоритмы (Pixel Perfect)")

with st.sidebar:
    st.header("Настройки")
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
        st.info("ℹ️ X1 = Радиус. Y1 игнорируется.")
    
    st.divider()
    view_range = st.slider("Масштаб (Range)", 5, 50, 15)

# --- Расчет ---
algo = Algorithms()
points = []
logs = []
duration = 0

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
        if r <= 0: st.error("Радиус > 0")
        else: points, logs = algo.bresenham_circle(int(x0), int(y0), r)
    duration = (time.perf_counter_ns() - start_time) / 1000.0
except Exception as e:
    st.error(f"Ошибка: {e}")

# --- ВИЗУАЛИЗАЦИЯ (ИЗМЕНЕНА) ---
m1, m2 = st.columns(2)
m1.metric("Пикселей", len(points))
m2.metric("Время", f"{duration:.3f} мкс")

fig, ax = plt.subplots(figsize=(8, 8))

# 1. Настраиваем пределы отображения
limit = view_range
ax.set_xlim(-limit - 0.5, limit + 0.5) # Добавляем 0.5, чтобы крайние клетки влезли
ax.set_ylim(-limit - 0.5, limit + 0.5)

# 2. Настраиваем СЕТКУ
# Основные тики (Major) ставим на целые числа (там будут подписи: 0, 1, 2)
ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
ax.yaxis.set_major_locator(ticker.MultipleLocator(1))

# Вспомогательные тики (Minor) ставим на половинки (0.5, 1.5...) - там будут ЛИНИИ сетки
minor_locator_x = np.arange(-limit - 1, limit + 2) + 0.5
minor_locator_y = np.arange(-limit - 1, limit + 2) + 0.5
ax.set_xticks(minor_locator_x, minor=True)
ax.set_yticks(minor_locator_y, minor=True)

# Рисуем сетку только по Minor тикам (чтобы линии шли между числами)
ax.grid(which='minor', color='gray', linestyle='-', linewidth=0.5)
ax.grid(which='major', color='gray', alpha=0) # Скрываем сетку на самих числах

# Рисуем жирные оси X и Y (они проходят через 0)
ax.axhline(y=0, color='black', linewidth=1.5)
ax.axvline(x=0, color='black', linewidth=1.5)

# 3. Рисуем ПИКСЕЛИ как КВАДРАТЫ (Rectangles)
if points:
    for p in points:
        px, py = p
        # Квадрат рисуется от левого нижнего угла.
        # Если центр пикселя (px, py), то левый нижний угол (px-0.5, py-0.5)
        # Размеры квадрата 1x1
        rect = patches.Rectangle(
            (px - 0.5, py - 0.5), 1, 1, 
            linewidth=0.5, edgecolor='black', facecolor='#4169E1' # Королевский синий
        )
        ax.add_patch(rect)
    
    # Идеальная линия (для сравнения)
    if "Окружность" not in alg_type and len(points) > 0:
        ax.plot([x0, x1], [y0, y1], 'r--', alpha=0.5, linewidth=1, label='Идеал')

ax.set_title(f"Визуализация: {alg_type}")
# Уменьшаем размер шрифта подписей осей, чтобы не нагромождались
ax.tick_params(axis='both', which='major', labelsize=8)

st.pyplot(fig)

with st.expander("📋 Открыть лог вычислений"):
    st.text("\n".join(logs))