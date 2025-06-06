import tkinter as tk
from custom_dropdown import CustomDropdown

class TaskAddWindow(tk.Toplevel):
    def __init__(self, master, existing_data, on_submit):
        super().__init__(master)
        self.title("➕ 新增任務")
        self.configure(bg="#1e1e1e")
        self.geometry("600x420")
        self.resizable(False, False)

        self.existing_data = existing_data
        self.on_submit = on_submit
        self.selected_category = None

        self.build_ui()

    def build_ui(self):
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
        self.series_dropdown = CustomDropdown(self.series_frame, font=("標楷體", 12), placeholder="可輸入或選擇")

        self.series_label.pack(side="left")
        self.series_dropdown.pack(side="left", fill="x", expand=True)
        self.series_frame.pack(pady=10, fill="x", padx=30)
        self.task_frame = tk.Frame(self, bg="#1e1e1e")
        self.task_label = tk.Label(self.task_frame, text="任務內容：", font=("標楷體", 14), bg="#1e1e1e", fg="#ffffff")
        self.task_dropdown = CustomDropdown(self.task_frame, font=("標楷體", 12), placeholder="可輸入或選擇")

        self.task_label.pack(side="left")
        self.task_dropdown.pack(side="left", fill="x", expand=True)
        self.task_frame.pack(pady=10, fill="x", padx=30)

        btn_frame = tk.Frame(self, bg="#1e1e1e")
        btn_frame.pack(pady=30, side="bottom", anchor="s", fill="x")

        confirm_btn = tk.Button(btn_frame, text="✅ 確定", font=("標楷體", 12), command=self.submit,
                                width=10, bg="#1e1e1e", fg="#30C930", activebackground="#1e6b1e")
        cancel_btn = tk.Button(btn_frame, text="❌ 取消", font=("標楷體", 12), command=self.destroy,
                               width=10, bg="#1e1e1e", fg="#DD0000", activebackground="#600000")
        confirm_btn.pack(side="left", expand=True, padx=40)
        cancel_btn.pack(side="right", expand=True, padx=40)

        self.series_frame.pack_forget()

    def select_category(self, category):
        self.selected_category = category
        for cat, btn in self.category_buttons.items():
            btn.config(fg="#69c0ff" if cat == category else "#ffffff")

        all_tasks = []
        if category == "重複區":
            self.series_frame.pack_forget()
            all_tasks = self.existing_data.get("重複區", [])
        else:
            self.series_frame.pack(pady=10, fill="x", padx=30)
            topics = list(self.existing_data.get(category, {}).keys())
            self.series_dropdown.values = topics

            for tasklist in self.existing_data.get(category, {}).values():
                for item in tasklist:
                    if isinstance(item, dict) and "task" in item:
                        all_tasks.append(item["task"])
                    elif isinstance(item, str):
                        all_tasks.append(item)

        self.task_dropdown.values = list({t for t in all_tasks if t})

    def submit(self):
        task = self.task_dropdown.get()
        topic = self.series_dropdown.get()
        if not self.selected_category or not task:
            return
        self.on_submit(self.selected_category, topic, task)
        self.destroy()

    def destroy(self):
        print("🛑 新增任務視窗關閉，嘗試解除主畫面滑鼠鎖定")
        try:
            self.master.unbind("<Button-1>", funcid=None)
            print("✅ 成功解除主畫面滑鼠鎖定")
        except Exception as e:
            print("⚠️ 無法解除主畫面滑鼠鎖定:", e)
        super().destroy()
