
import tkinter as tk
from tkinter import ttk

class TaskAddWindow(tk.Toplevel):
    def __init__(self, master, existing_data, on_submit):
        super().__init__(master)
        self.title("➕ 新增任務")
        self.configure(bg="#1e1e1e")
        self.geometry("600x400")
        self.resizable(False, False)

        self.existing_data = existing_data
        self.on_submit = on_submit
        self.selected_category = None

        self.build_ui()

    def build_ui(self):
        # 任務分類選擇
        title = tk.Label(self, text="請選擇任務分類", font=("標楷體", 16), bg="#1e1e1e", fg="#ffffff")
        title.pack(pady=10)

        self.category_frame = tk.Frame(self, bg="#1e1e1e")
        self.category_frame.pack(pady=10)

        self.category_buttons = {}
        categories = ["重複區", "突發區", "主線任務", "支線任務"]
        for cat in categories:
            btn = tk.Label(self.category_frame, text=cat, font=("標楷體", 14), bg="#1e1e1e", fg="#ffffff", padx=10, pady=5, cursor="hand2", relief="ridge")
            btn.pack(side="left", padx=10)
            btn.bind("<Button-1>", lambda e, c=cat: self.select_category(c))
            self.category_buttons[cat] = btn

        self.series_frame = tk.Frame(self, bg="#1e1e1e")
        self.series_label = tk.Label(self.series_frame, text="系列主題：", font=("標楷體", 14), bg="#1e1e1e", fg="#ffffff")
        self.series_combobox = ttk.Combobox(self.series_frame, font=("標楷體", 12))
        self.series_label.pack(side="left")
        self.series_combobox.pack(side="left", fill="x", expand=True)
        self.series_frame.pack(pady=10, fill="x", padx=30)

        self.task_frame = tk.Frame(self, bg="#1e1e1e")
        self.task_label = tk.Label(self.task_frame, text="任務內容：", font=("標楷體", 14), bg="#1e1e1e", fg="#ffffff")
        self.task_entry = ttk.Combobox(self.task_frame, font=("標楷體", 12))
        self.task_label.pack(side="left")
        self.task_entry.pack(side="left", fill="x", expand=True)
        self.task_frame.pack(pady=10, fill="x", padx=30)

        # 確定/取消
        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(pady=20)

        confirm_btn = tk.Button(btn_frame, text="✅ 確定", font=("標楷體", 12), command=self.submit, width=10)
        cancel_btn = tk.Button(btn_frame, text="❌ 取消", font=("標楷體", 12), command=self.destroy, width=10)
        confirm_btn.pack(side="left", padx=20)
        cancel_btn.pack(side="left", padx=20)

        # 初始隱藏系列欄
        self.series_frame.pack_forget()

    def select_category(self, category):
        self.selected_category = category
        for cat, btn in self.category_buttons.items():
            btn.config(fg="#69c0ff" if cat == category else "#ffffff")
        if category == "重複區":
            self.series_frame.pack_forget()
        else:
            self.series_frame.pack(pady=10, fill="x", padx=30)
            existing_topics = list(self.existing_data.get(category, {}).keys())
            self.series_combobox["values"] = existing_topics

    def submit(self):
        task = self.task_entry.get().strip()
        topic = self.series_combobox.get().strip()
        if not self.selected_category or not task:
            return
        self.on_submit(self.selected_category, topic, task)
        self.destroy()
