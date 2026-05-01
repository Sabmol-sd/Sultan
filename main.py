import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import json
import os
from datetime import datetime

# глобальные данные и константы
DATA_FILE = "expenses.json"
CATEGORIES = ["еда", "транспорт", "развлечения", "жилье", "здоровье", "прочее"]
expenses = []

# параметры оформления
FONT_MAIN = ("Segoe UI", 10)
FONT_HEADER = ("Segoe UI", 11, "bold")
BG_COLOR = "#f0f4f8"
FRAME_BG = "#ffffff"
ACCENT = "#3b82f6"
ACCENT_HOVER = "#2563eb"
TEXT_COLOR = "#1e293b"
HEADING_BG = "#e2e8f0"

# настройка темы ttk
def apply_theme():
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TFrame", background=FRAME_BG)
    style.configure("TLabel", background=FRAME_BG, foreground=TEXT_COLOR, font=FONT_MAIN)
    style.configure("TButton", background=ACCENT, foreground="white", font=FONT_MAIN, borderwidth=0, focuscolor="none")
    style.map("TButton", background=[("active", ACCENT_HOVER), ("pressed", "#1d4ed8")])
    style.configure("TCombobox", background=FRAME_BG, foreground=TEXT_COLOR, font=FONT_MAIN)
    style.map("TCombobox", fieldbackground=[("readonly", FRAME_BG)])
    style.configure("Treeview", background=FRAME_BG, fieldbackground=FRAME_BG, foreground=TEXT_COLOR, font=FONT_MAIN, rowheight=26)
    style.configure("Treeview.Heading", background=HEADING_BG, foreground=TEXT_COLOR, font=FONT_HEADER, borderwidth=1)

# загрузка данных из файла
def load_data():
    global expenses
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    expenses = data
        except Exception as e:
            messagebox.showerror("ошибка загрузки", f"не удалось прочитать файл:\n{e}")
            expenses = []

# сохранение данных в файл
def save_data():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(expenses, f, ensure_ascii=False, indent=4)
    except Exception as e:
        messagebox.showerror("ошибка сохранения", f"не удалось записать файл:\n{e}")

# проверка корректности суммы
def get_valid_amount():
    raw = amount_entry.get().strip().replace(',', '.')
    if not raw:
        messagebox.showwarning("ввод", "поле суммы пустое.")
        return None
    try:
        val = float(raw)
        if val <= 0:
            messagebox.showerror("ошибка", "сумма должна быть больше нуля.")
            return None
        return round(val, 2)
    except ValueError:
        messagebox.showerror("ошибка", "сумма должна быть числом.")
        return None

# добавление новой записи
def add_expense():
    amount = get_valid_amount()
    if amount is None:
        return

    category = category_add_cb.get()
    if not category:
        messagebox.showwarning("ввод", "выберите категорию.")
        return

    date_str = date_add_picker.get_date().strftime("%d.%m.%Y")

    new_expense = {
        "id": len(expenses) + 1,
        "date": date_str,
        "category": category,
        "amount": amount
    }
    expenses.append(new_expense)
    save_data()
    refresh_table()
    amount_entry.delete(0, tk.END)
    date_add_picker.set_date(datetime.now())

# применение фильтров
def apply_filters():
    try:
        start_date = filter_start_picker.get_date()
        end_date = filter_end_picker.get_date()
        if start_date > end_date:
            messagebox.showwarning("фильтр", "дата начала не может быть позже окончания.")
            return
    except Exception as e:
        messagebox.showerror("ошибка", f"проблема с датами:\n{e}")
        return

    selected_cat = filter_cat_cb.get()
    filtered = []

    for exp in expenses:
        exp_date = datetime.strptime(exp["date"], "%d.%m.%Y").date()
        date_ok = start_date <= exp_date <= end_date
        cat_ok = (selected_cat == "Все") or (exp["category"] == selected_cat)

        if date_ok and cat_ok:
            filtered.append(exp)

    refresh_table(data=filtered)

# сброс фильтров
def reset_filters():
    today = datetime.now().date()
    first_day = today.replace(day=1)
    filter_start_picker.set_date(first_day)
    filter_end_picker.set_date(today)
    filter_cat_cb.current(0)
    refresh_table()

# обновление таблицы и подсчёт суммы
def refresh_table(data=None):
    for item in tree.get_children():
        tree.delete(item)

    display_data = data if data is not None else expenses

    # исправленная строка с полным названием переменной
    for exp in display_data:
        tree.insert("", tk.END, values=(
            exp["id"],
            exp["date"],
            exp["category"],
            f"{exp['amount']:.2f} ₽"
        ))

    total = sum(exp["amount"] for exp in display_data)
    sum_label.config(text=f"сумма за период: {total:.2f} ₽")

# создание интерфейса
def setup_ui():
    global amount_entry, category_add_cb, date_add_picker
    global filter_start_picker, filter_end_picker, filter_cat_cb
    global tree, sum_label

    apply_theme()

    root = tk.Tk()
    root.title("Expense Tracker")
    root.geometry("950x600")
    root.configure(bg=BG_COLOR)
    root.resizable(False, False)

    # левая панель
    left_frame = ttk.Frame(root, padding=15)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    left_frame.configure(style="TFrame")

    # блок добавления
    ttk.Label(left_frame, text="добавить расход", font=FONT_HEADER).pack(anchor="w", pady=(0, 10))
    frm_add = ttk.Frame(left_frame)
    frm_add.pack(fill=tk.X, pady=5)

    ttk.Label(frm_add, text="сумма:").grid(row=0, column=0, padx=5, sticky="e")
    amount_entry = ttk.Entry(frm_add, width=15, font=FONT_MAIN)
    amount_entry.grid(row=0, column=1, padx=5)

    ttk.Label(frm_add, text="категория:").grid(row=1, column=0, padx=5, sticky="e")
    category_add_cb = ttk.Combobox(frm_add, values=CATEGORIES, state="readonly", width=15, font=FONT_MAIN)
    category_add_cb.grid(row=1, column=1, padx=5)
    category_add_cb.current(0)

    ttk.Label(frm_add, text="дата:").grid(row=2, column=0, padx=5, sticky="e")
    date_add_picker = DateEntry(frm_add, width=12, background="white",
                                foreground=TEXT_COLOR, borderwidth=2, date_pattern="dd.mm.y", font=FONT_MAIN)
    date_add_picker.grid(row=2, column=1, padx=5)
    date_add_picker.set_date(datetime.now())

    ttk.Button(left_frame, text="добавить", command=add_expense, width=18).pack(pady=15)

    # блок фильтрации
    ttk.Label(left_frame, text="фильтрация", font=FONT_HEADER).pack(anchor="w", pady=(10, 10))

    ttk.Label(left_frame, text="период с:").pack(anchor="w")
    filter_start_picker = DateEntry(left_frame, width=12, background="white",
                                    foreground=TEXT_COLOR, borderwidth=2, date_pattern="dd.mm.y", font=FONT_MAIN)
    filter_start_picker.pack(pady=3)

    ttk.Label(left_frame, text="по:").pack(anchor="w")
    filter_end_picker = DateEntry(left_frame, width=12, background="white",
                                  foreground=TEXT_COLOR, borderwidth=2, date_pattern="dd.mm.y", font=FONT_MAIN)
    filter_end_picker.pack(pady=3)

    ttk.Label(left_frame, text="категория:").pack(anchor="w")
    filter_cat_cb = ttk.Combobox(left_frame, values=["Все"] + CATEGORIES, state="readonly", width=15, font=FONT_MAIN)
    filter_cat_cb.pack(pady=3)
    filter_cat_cb.current(0)

    btn_frame = ttk.Frame(left_frame)
    btn_frame.pack(pady=12)
    ttk.Button(btn_frame, text="применить", command=apply_filters).pack(side=tk.LEFT, padx=5)
    ttk.Button(btn_frame, text="сбросить", command=reset_filters).pack(side=tk.LEFT, padx=5)

    # правая панель
    right_frame = ttk.Frame(root, padding=15)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    right_frame.configure(style="TFrame")

    cols = ("ID", "Дата", "Категория", "Сумма")
    tree = ttk.Treeview(right_frame, columns=cols, show="headings", height=18)
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, anchor="center", minwidth=60)
    tree.column("ID", width=50)
    tree.column("Дата", width=110)
    tree.column("Категория", width=140)
    tree.column("Сумма", width=100)
    tree.pack(fill=tk.BOTH, expand=True)

    sum_label = ttk.Label(right_frame, text="сумма за период: 0.00 ₽", font=("Segoe UI", 14, "bold"), foreground=ACCENT)
    sum_label.pack(pady=15)

    return root

# запуск приложения
if __name__ == "__main__":
    load_data()
    app = setup_ui()
    refresh_table()
    app.mainloop()