import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import os

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary")
        self.root.geometry("800x600")

        # Данные о погоде
        self.weather_records = []
        self.load_data()

        self.setup_ui()

    def setup_ui(self):
        """Настройка интерфейса"""
        # Фрейм для ввода данных
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=10)

        # Поле даты
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        # Поле температуры
        ttk.Label(input_frame, text="Температура (°C):").grid(row=0, column=2, padx=5, sticky="w")
        self.temp_entry = ttk.Entry(input_frame, width=10)
        self.temp_entry.grid(row=0, column=3, padx=5)

        # Поле описания погоды
        ttk.Label(input_frame, text="Описание:").grid(row=0, column=4, padx=5, sticky="w")
        self.desc_entry = ttk.Entry(input_frame, width=20)
        self.desc_entry.grid(row=0, column=5, padx=5)

        # Поле осадков (да/нет)
        ttk.Label(input_frame, text="Осадки:").grid(row=0, column=6, padx=5, sticky="w")
        self.precip_combo = ttk.Combobox(
            input_frame,
            values=["Да", "Нет"],
            width=8,
            state="readonly" # Запрещаем ручной ввод
        )
        self.precip_combo.current(1) # По умолчанию "Нет"
        self.precip_combo.grid(row=0, column=7, padx=5)

        # Кнопка добавления записи
        add_button = ttk.Button(input_frame, text="Добавить запись", command=self.add_record)
        add_button.grid(row=0, column=8, padx=10)

        # Таблица для отображения записей
        columns = ("ID", "Дата", "Температура (°C)", "Описание", "Осадки")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Описание":
                self.tree.column(col, width=200)
            elif col == "Дата":
                self.tree.column(col, width=120)
            else:
                self.tree.column(col, width=100)

        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

        # Фрейм для фильтрации
        filter_frame = ttk.Frame(self.root)
        filter_frame.pack(pady=10)

        # Фильтрация по дате
        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)

        # Фильтрация по температуре
        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=0, column=2, padx=5)
        self.min_temp_entry = ttk.Entry(filter_frame, width=10)
        self.min_temp_entry.insert(0, "-50")
        self.min_temp_entry.grid(row=0, column=3, padx=5)

        # Кнопки фильтрации
        filter_button = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_button.grid(row=0, column=4, padx=5)

        clear_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_button.grid(row=0, column=5, padx=5)

    def validate_input(self, date_str, temp_str, description):
         """Проверка корректности ввода"""
         if not description.strip():
             messagebox.showerror("Ошибка", "Описание погоды не может быть пустым")
             return False

         try:
             datetime.strptime(date_str, "%Y-%m-%d")
         except ValueError:
             messagebox.showerror("Ошибка", "Некорректный формат даты (используйте ГГГГ-ММ-ДД)")
             return False

         try:
             float(temp_str)
         except ValueError:
             messagebox.showerror("Ошибка", "Температура должна быть числом")
             return False

         return True

    def add_record(self):
         """Добавление новой записи о погоде"""
         date_str = self.date_entry.get().strip()
         temp_str = self.temp_entry.get().strip()
         description = self.desc_entry.get().strip()
         precipitation = self.precip_combo.get().strip()

         if not precipitation:
             messagebox.showerror("Ошибка", "Выберите наличие осадков")
             return

         if not self.validate_input(date_str, temp_str, description):
             return

         record = {
             "id": len(self.weather_records) + 1,
             "date": date_str,
             "temperature": float(temp_str),
             "description": description,
             "precipitation": precipitation
         }

         self.weather_records.append(record)
         self.save_data()
         self.refresh_table()
         self.clear_input()

    def clear_input(self):
         """Очистка полей ввода"""
         self.date_entry.delete(0, tk.END)
         self.temp_entry.delete(0, tk.END)
         self.desc_entry.delete(0, tk.END)
         self.precip_combo.set("") # Сбрасываем выбор осадков

    def refresh_table(self, data=None):
         """Обновление таблицы с записями о погоде"""
         for item in self.tree.get_children():
             self.tree.delete(item)

         display_data = data if data is not None else self.weather_records

         for record in display_data:
             self.tree.insert("", "end", values=(
                 record["id"],
                 record["date"],
                 f"{record['temperature']:.1f}",
                 record["description"],
                 record["precipitation"]
             ))

    def apply_filter(self):
         """Применение фильтров"""
         filtered = self.weather_records.copy() # Работаем с копией списка

         # Фильтр по дате
         filter_date = self.filter_date_entry.get().strip()
         if filter_date:
             try:
                 datetime.strptime(filter_date, "%Y-%m-%d")
                 filtered = [r for r in filtered if r["date"] == filter_date]
             except ValueError:
                 messagebox.showerror("Ошибка", "Некорректный формат даты для фильтра")
                 return

         # Фильтр по температуре
         min_temp_str = self.min_temp_entry.get().strip()
         if min_temp_str:
             try:
                 min_temp = float(min_temp_str)
                 filtered = [r for r in filtered if r["temperature"] >= min_temp]
             except ValueError:
                 messagebox.showerror("Ошибка", "Некорректный формат минимальной температуры")
                 return

         self.refresh_table(filtered)

    def clear_filter(self):
         """Сброс фильтров и обновление таблицы"""
         self.filter_date_entry.delete(0, tk.END)
         self.min_temp_entry.delete(0, tk.END)
         self.min_temp_entry.insert(0, "-50")
         self.refresh_table() # Исправлен вызов: добавлены скобки

    def save_data(self):
          """Сохранение данных в JSON-файл"""
          try:
              with open("weather_records.json", "w", encoding="utf-8") as f:
                  json.dump(self.weather_records, f, ensure_ascii=False, indent=4)
          except Exception as e:
              messagebox.showerror("Ошибка", f"Ошибка сохранения: {e}")

    def load_data(self):
          """Загрузка данных из JSON-файла"""
          if os.path.exists("weather_records.json"):
              try:
                  with open("weather_records.json", "r", encoding="utf-8") as f:
                      self.weather_records = json.load(f)
              except Exception as e:
                  messagebox.showerror("Ошибка", f"Ошибка загрузки: {e}")
                  self.weather_records = []
          else:
              self.weather_records = []

# Запуск приложения
if __name__ == "__main__":
     root = tk.Tk()
     app = WeatherDiary(root)
     root.mainloop()
     