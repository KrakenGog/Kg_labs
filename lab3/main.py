import tkinter as tk
from tkinter import ttk, messagebox
import time
import math

class RasterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная работа №3: Растровые алгоритмы")
        self.root.geometry("1000x700")

        # Параметры сетки
        self.scale = 20  # Размер клетки в пикселях
        self.offset_x = 0 # Смещение центра
        self.offset_y = 0

        # UI Layout
        self.setup_ui()
        
        # Инициализация холста
        self.draw_grid()

    def setup_ui(self):
        # Панель управления (слева)
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Ввод координат
        ttk.Label(control_frame, text="Начало (X0, Y0):").pack(pady=2)
        self.entry_x0 = ttk.Entry(control_frame, width=10)
        self.entry_x0.insert(0, "-5")
        self.entry_x0.pack()
        self.entry_y0 = ttk.Entry(control_frame, width=10)
        self.entry_y0.insert(0, "-2")
        self.entry_y0.pack()

        ttk.Label(control_frame, text="Конец (X1, Y1) / Радиус R:").pack(pady=5)
        self.entry_x1 = ttk.Entry(control_frame, width=10)
        self.entry_x1.insert(0, "8")
        self.entry_x1.pack()
        self.entry_y1 = ttk.Entry(control_frame, width=10)
        self.entry_y1.insert(0, "6")
        self.entry_y1.pack()
        ttk.Label(control_frame, text="(Для окружности Y1 игнорируется,\nX1 используется как Радиус)").pack(pady=0)

        # Кнопки алгоритмов
        ttk.Label(control_frame, text="Алгоритмы:").pack(pady=10)
        
        ttk.Button(control_frame, text="Пошаговый", command=lambda: self.run_algorithm("step")).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="ЦДА (DDA)", command=lambda: self.run_algorithm("dda")).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Брезенхем (Линия)", command=lambda: self.run_algorithm("bres_line")).pack(fill=tk.X, pady=2)
        ttk.Button(control_frame, text="Брезенхем (Окружность)", command=lambda: self.run_algorithm("bres_circle")).pack(fill=tk.X, pady=2)

        # Управление масштабом
        ttk.Label(control_frame, text="Масштаб сетки:").pack(pady=10)
        self.scale_var = tk.DoubleVar(value=20)
        scale_slider = ttk.Scale(control_frame, from_=5, to=50, variable=self.scale_var, command=self.update_scale)
        scale_slider.pack(fill=tk.X)

        ttk.Button(control_frame, text="Очистить", command=self.clear_canvas).pack(pady=20, fill=tk.X)

        # Текстовое поле для логов (для отчета)
        ttk.Label(control_frame, text="Лог вычислений (см. консоль тоже):").pack(pady=5)
        self.log_text = tk.Text(control_frame, height=15, width=30, font=("Consolas", 8))
        self.log_text.pack()

        # Холст (справа)
        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", lambda e: self.draw_grid())

    def update_scale(self, val):
        self.scale = int(float(val))
        self.draw_grid()

    def clear_canvas(self):
        self.log_text.delete(1.0, tk.END)
        self.draw_grid()

    def log(self, message):
        """Вывод логов в интерфейс и в консоль"""
        print(message)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    # --- Рисование сетки ---
    def draw_grid(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        
        cw, ch = w // 2, h // 2 # Центр экрана

        # Рисуем вертикальные линии
        for i in range(0, w // 2 + self.scale, self.scale):
            # Вправо от центра
            self.canvas.create_line(cw + i, 0, cw + i, h, fill="#ddd")
            # Влево от центра
            self.canvas.create_line(cw - i, 0, cw - i, h, fill="#ddd")

        # Рисуем горизонтальные линии
        for i in range(0, h // 2 + self.scale, self.scale):
            # Вниз от центра
            self.canvas.create_line(0, ch + i, w, ch + i, fill="#ddd")
            # Вверх от центра
            self.canvas.create_line(0, ch - i, w, ch - i, fill="#ddd")

        # Оси координат
        self.canvas.create_line(cw, 0, cw, h, fill="black", width=2) # Y
        self.canvas.create_line(0, ch, w, ch, fill="black", width=2) # X
        
        # Подписи осей
        self.canvas.create_text(w-10, ch+15, text="X", fill="red")
        self.canvas.create_text(cw+15, 10, text="Y", fill="red")

    def plot_pixel(self, x, y, color="blue"):
        """
        Закрашивает 'пиксель' (клетку сетки) по логическим координатам.
        Логические координаты (0,0) - центр экрана.
        Y направлен вверх.
        """
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cw, ch = w // 2, h // 2

        # Преобразование логических координат в экранные (верхний левый угол клетки)
        # X: cw + x * scale
        # Y: ch - y * scale (минус, т.к. на экране Y растет вниз, а в математике вверх)
        # Но нужно учесть, что координаты клетки начинаются с top-left, поэтому для Y нужно сместить на scale вверх для корректного отображения (или вниз, зависит от привязки).
        # Давайте условимся: клетка (0,0) - это квадрат в 1 четверти, примыкающий к осям.
        
        screen_x = cw + x * self.scale
        screen_y = ch - y * self.scale
        
        # Рисуем квадрат. Y на экране растет вниз. 
        # Если y=0, то screen_y = ch. Квадрат должен быть от ch-scale до ch? Или от ch до ch+scale?
        # Обычно (0,0) рисуют прямо на пересечении. Давайте центрировать пиксель на пересечении линий сетки для наглядности (как точки).
        # Либо заполнять клетку, где точка (x,y) является левым нижним углом.
        # В компьютерной графике пиксели дискретны. Пусть (0,0) это клетка справа-вверху от пересечения осей (или центрированная).
        # Для простоты: центрируем квадрат относительно математической точки пересечения.
        
        half = self.scale // 2
        # Корректируем screen_y, так как ось Y перевернута.
        # Если хотим рисовать именно в узлах сетки:
        self.canvas.create_rectangle(
            screen_x - half, screen_y - half,
            screen_x + half, screen_y + half,
            fill=color, outline="gray"
        )
        # Подпись координат (опционально, если масштаб крупный)
        if self.scale > 25:
            self.canvas.create_text(screen_x, screen_y, text=f"{x},{y}", font=("Arial", 7), fill="white")

    # --- Алгоритмы ---

    def run_algorithm(self, alg_type):
        try:
            x0 = int(self.entry_x0.get())
            y0 = int(self.entry_y0.get())
            x1 = int(self.entry_x1.get())
            
            # Для окружности y1 не нужен, но считаем его для линий
            try:
                y1 = int(self.entry_y1.get())
            except:
                y1 = 0

            self.draw_grid() # Очистить старое
            self.log(f"--- Запуск: {alg_type.upper()} ---")

            points = []
            start_time = time.perf_counter_ns()

            if alg_type == "step":
                points = self.algo_step_by_step(x0, y0, x1, y1)
            elif alg_type == "dda":
                points = self.algo_dda(x0, y0, x1, y1)
            elif alg_type == "bres_line":
                points = self.algo_bresenham_line(x0, y0, x1, y1)
            elif alg_type == "bres_circle":
                # x1 используем как радиус
                r = x1
                if r <= 0: raise ValueError("Радиус должен быть > 0")
                points = self.algo_bresenham_circle(x0, y0, r)

            end_time = time.perf_counter_ns()
            duration_us = (end_time - start_time) / 1000.0
            
            self.log(f"Время выполнения (расчет): {duration_us:.3f} мкс")
            self.log(f"Количество пикселей: {len(points)}")

            # Отрисовка
            for p in points:
                self.plot_pixel(p[0], p[1])

        except ValueError as e:
            messagebox.showerror("Ошибка", f"Проверьте входные данные!\n{e}")

    # 1. Пошаговый алгоритм (y = kx + b)
    def algo_step_by_step(self, x0, y0, x1, y1):
        points = []
        if x0 == x1 and y0 == y1:
            return [(x0, y0)]
        
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx), abs(dy))
        
        self.log(f"dx={dx}, dy={dy}, steps={steps}")

        # Если линия более вертикальная, чем горизонтальная, меняем логику (идем по Y)
        if abs(dx) >= abs(dy):
            k = dy / dx if dx != 0 else 0
            b = y0 - k * x0
            self.log(f"Основная ось X. k={k:.2f}, b={b:.2f}")
            
            step = 1 if x1 > x0 else -1
            for x in range(x0, x1 + step, step):
                y = k * x + b
                points.append((x, round(y)))
                self.log(f"x={x}, y_real={y:.2f} -> y_int={round(y)}")
        else:
            # Выражаем x через y: x = (y - b) / k -> или просто меняем местами роли
            # x = my + c
            m = dx / dy
            c = x0 - m * y0
            self.log(f"Основная ось Y. m={m:.2f}, c={c:.2f}")
            
            step = 1 if y1 > y0 else -1
            for y in range(y0, y1 + step, step):
                x = m * y + c
                points.append((round(x), y))
                self.log(f"y={y}, x_real={x:.2f} -> x_int={round(x)}")
                
        return points

    # 2. Алгоритм ЦДА (DDA)
    def algo_dda(self, x0, y0, x1, y1):
        points = []
        dx = x1 - x0
        dy = y1 - y0
        
        steps = max(abs(dx), abs(dy))
        if steps == 0: return [(x0, y0)]

        x_inc = dx / steps
        y_inc = dy / steps

        self.log(f"Steps={steps}, X_inc={x_inc:.2f}, Y_inc={y_inc:.2f}")

        x = x0
        y = y0
        
        for i in range(steps + 1):
            points.append((round(x), round(y)))
            # self.log(f"Шаг {i}: x={x:.2f}, y={y:.2f} -> ({round(x)}, {round(y)})")
            x += x_inc
            y += y_inc
            
        return points

    # 3. Алгоритм Брезенхема (Отрезок)
    def algo_bresenham_line(self, x0, y0, x1, y1):
        points = []
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        
        err = dx - dy
        self.log(f"Init Error={err}, dx={dx}, dy={dy}")
        
        while True:
            points.append((x0, y0))
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
                
        return points

    # 4. Алгоритм Брезенхема (Окружность)
    def algo_bresenham_circle(self, xc, yc, r):
        points = []
        x = 0
        y = r
        d = 3 - 2 * r
        
        self.log(f"Start Circle: R={r}, Init d={d}")

        def plot_circle_points(cx, cy, x, y):
            # Отражаем точку в 8 октантов
            pts = [
                (cx + x, cy + y), (cx - x, cy + y),
                (cx + x, cy - y), (cx - x, cy - y),
                (cx + y, cy + x), (cx - y, cy + x),
                (cx + y, cy - x), (cx - y, cy - x)
            ]
            return pts

        while y >= x:
            # Добавляем точки всех 8 симметричных частей
            points.extend(plot_circle_points(xc, yc, x, y))
            
            x += 1
            if d > 0:
                y -= 1
                d = d + 4 * (x - y) + 10
            else:
                d = d + 4 * x + 6
            # self.log(f"x={x}, y={y}, d={d}")
                
        return points

if __name__ == "__main__":
    root = tk.Tk()
    app = RasterApp(root)
    root.mainloop()