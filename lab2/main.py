import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import cv2
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

# Настройка темы (System подстраивается под ОС, Dark - принудительно темная)
ctk.set_appearance_mode("Dark")  
ctk.set_default_color_theme("blue")  # Темы: "blue", "green", "dark-blue"

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Настройки окна
        self.title("Lab 2 - Variant 12 (Modern UI)")
        self.geometry("1200x800")
        
        self.original_image = None
        self.processed_image = None
        self.preview_size = (500, 400) # Размер области просмотра

        # === СЕТКА (Layout) ===
        # Разделяем окно на 2 колонки: левая (меню) узкая, правая (картинки) широкая
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # === ЛЕВАЯ ПАНЕЛЬ (SIDEBAR) ===
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="Image Processor", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.pack(padx=20, pady=(20, 10))

        # Кнопка загрузки
        self.btn_load = ctk.CTkButton(self.sidebar, text="Загрузить изображение", command=self.load_image, 
                                      height=40, font=ctk.CTkFont(weight="bold"))
        self.btn_load.pack(padx=20, pady=10, fill="x")

        # Вкладки настроек
        self.tabview = ctk.CTkTabview(self.sidebar, width=250)
        self.tabview.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.setup_smoothing_tab()
        self.setup_threshold_tab()

        # Кнопка гистограммы внизу
        #self.btn_hist = ctk.CTkButton(self.sidebar, text="Показать гистограмму", command=self.show_histogram,
        #                              fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE"))
        #self.btn_hist.pack(padx=20, pady=20, side="bottom", fill="x")

        # === ПРАВАЯ ПАНЕЛЬ (ОСНОВНАЯ) ===
        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_area.columnconfigure(0, weight=1)
        self.main_area.columnconfigure(1, weight=1)

        # Заголовки
        ctk.CTkLabel(self.main_area, text="Исходное изображение", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, pady=10)
        ctk.CTkLabel(self.main_area, text="Результат обработки", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, pady=10)

        # Места для картинок
        self.lbl_orig = ctk.CTkLabel(self.main_area, text="Нет изображения\nЗагрузите файл", 
                                     fg_color=("white", "gray20"), corner_radius=10)
        self.lbl_orig.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.lbl_proc = ctk.CTkLabel(self.main_area, text="Ожидание...", 
                                     fg_color=("white", "gray20"), corner_radius=10)
        self.lbl_proc.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)

    # --- НАСТРОЙКА ВКЛАДОК ---
    def setup_smoothing_tab(self):
        tab = self.tabview.add("Сглаживание")
        
        ctk.CTkLabel(tab, text="Тип фильтра:").pack(pady=5)
        self.filter_type = ctk.CTkOptionMenu(tab, values=["Gaussian Blur", "Median Blur", "Box Blur"])
        self.filter_type.pack(fill="x", pady=5)

        ctk.CTkLabel(tab, text="Размер ядра:").pack(pady=(15, 0))
        self.lbl_kernel_val = ctk.CTkLabel(tab, text="5")
        self.lbl_kernel_val.pack()
        
        # Слайдер
        self.slider_kernel = ctk.CTkSlider(tab, from_=3, to=31, number_of_steps=14, command=self.update_kernel_label)
        self.slider_kernel.set(5)
        self.slider_kernel.pack(fill="x", pady=5)

        ctk.CTkButton(tab, text="Применить", command=self.apply_smoothing, fg_color="#2CC985", hover_color="#229966").pack(pady=20, fill="x")

    def setup_threshold_tab(self):
        tab = self.tabview.add("Порог")

        ctk.CTkLabel(tab, text="Метод:").pack(pady=5)
        self.thresh_type = ctk.CTkOptionMenu(tab, values=["Adaptive Gaussian", "Adaptive Mean"])
        self.thresh_type.pack(fill="x", pady=5)

        # Block Size
        ctk.CTkLabel(tab, text="Block Size (соседи):").pack(pady=(15,0))
        self.lbl_block_val = ctk.CTkLabel(tab, text="11")
        self.lbl_block_val.pack()
        self.slider_block = ctk.CTkSlider(tab, from_=3, to=51, number_of_steps=24, command=self.update_block_label)
        self.slider_block.set(11)
        self.slider_block.pack(fill="x")

        # Constant C
        ctk.CTkLabel(tab, text="Константа C:").pack(pady=(15,0))
        self.lbl_c_val = ctk.CTkLabel(tab, text="2")
        self.lbl_c_val.pack()
        self.slider_c = ctk.CTkSlider(tab, from_=-10, to=30, number_of_steps=40, command=self.update_c_label)
        self.slider_c.set(2)
        self.slider_c.pack(fill="x")

        ctk.CTkButton(tab, text="Применить", command=self.apply_threshold, fg_color="#E04F5F", hover_color="#B03E4B").pack(pady=20, fill="x")

    # --- ОБНОВЛЕНИЕ ЗНАЧЕНИЙ СЛАЙДЕРОВ ---
    def update_kernel_label(self, value):
        val = int(value)
        if val % 2 == 0: val += 1 # Всегда нечетное
        self.lbl_kernel_val.configure(text=str(val))

    def update_block_label(self, value):
        val = int(value)
        if val % 2 == 0: val += 1
        self.lbl_block_val.configure(text=str(val))

    def update_c_label(self, value):
        self.lbl_c_val.configure(text=str(int(value)))

    # --- ЛОГИКА ---
    def load_image(self):
        path = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")])
        if path:
            self.original_image = cv2.imread(path)
            self.processed_image = self.original_image.copy()
            self.update_display(self.lbl_orig, self.original_image)
            self.update_display(self.lbl_proc, self.processed_image)

    def update_display(self, label_widget, cv_img):
        # Конвертация BGR -> RGB
        if len(cv_img.shape) == 2:
            img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_GRAY2RGB)
        else:
            img_rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
            
        pil_image = Image.fromarray(img_rgb)
        
        # CustomTkinter Image (автоматически работает с HiDPI)
        # size - это желаемый размер отображения. 
        # Картинка будет масштабироваться под виджет, но сохраняя аспект, если мы используем правильный виджет.
        
        # Вычисляем аспект, чтобы картинка не сплющилась
        h, w = cv_img.shape[:2]
        ratio = min(self.preview_size[0]/w, self.preview_size[1]/h)
        new_w, new_h = int(w * ratio), int(h * ratio)

        ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(new_w, new_h))
        
        label_widget.configure(image=ctk_img, text="")
        label_widget.image = ctk_img  # Сохраняем ссылку, чтобы сборщик мусора не удалил

    def apply_smoothing(self):
        if self.original_image is None: return
        k = int(self.lbl_kernel_val.cget("text"))
        method = self.filter_type.get()

        if "Gaussian" in method:
            self.processed_image = cv2.GaussianBlur(self.original_image, (k, k), 0)
        elif "Median" in method:
            self.processed_image = cv2.medianBlur(self.original_image, k)
        else:
            self.processed_image = cv2.blur(self.original_image, (k, k))
        
        self.update_display(self.lbl_proc, self.processed_image)

    def apply_threshold(self):
        if self.original_image is None: return
        gray = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2GRAY)
        
        bs = int(self.lbl_block_val.cget("text"))
        c = int(self.lbl_c_val.cget("text"))
        method = self.thresh_type.get()

        algo = cv2.ADAPTIVE_THRESH_GAUSSIAN_C if "Gaussian" in method else cv2.ADAPTIVE_THRESH_MEAN_C
        
        self.processed_image = cv2.adaptiveThreshold(
            gray, 255, algo, cv2.THRESH_BINARY, bs, c
        )
        self.update_display(self.lbl_proc, self.processed_image)

   
if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()