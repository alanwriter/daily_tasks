import tkinter as tk
from tkinter import simpledialog, filedialog, messagebox
from datetime import datetime, date, timedelta
from task_add_window import TaskAddWindow
import json
import os

FONT = ("標楷體", 14)
FONT_BOLD = ("標楷體", 14, "bold")
BG_COLOR = "#1e1e1e"
FG_COLOR = "#ffffff"
FG_GRAY = "#777777"
TOPIC_COLOR = "#69c0ff"
EDIT_COLOR = "#ff5555"
DATA_FILE = "tasks.json"

DEFAULT_REPEAT_TASKS = [
    "刷牙洗臉", "形象檢查", "吃酵素", "HIIT30分", "健身房1HR",
    "處理房間垃圾", "處理房間灰塵", "閱讀Gmail", "收拾桌面", "洗衣服"
]

CATEGORIES = ["重複區", "突發區", "主線任務", "支線任務"]

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {
            "tasks": {
                "重複區": DEFAULT_REPEAT_TASKS.copy(),
                "突發區": {},
                "主線任務": {},
                "支線任務": {}
            },
            "completed": [],
            "last_reset": ""
        }

    # 使用早上 5:00 為換日基準
    now = datetime.now()
    switch_hour = 5
    if now.hour < switch_hour:
        effective_date = (now - timedelta(days=1)).date()
    else:
        effective_date = now.date()
    effective_date_str = str(effective_date)

    if data.get("last_reset") != effective_date_str:
        data["tasks"]["重複區"] = DEFAULT_REPEAT_TASKS.copy()
        data["completed"] = []
        data["last_reset"] = effective_date_str

    # 轉換 legacy 突發區格式
    def convert_legacy_tasks(tasklist):
        newlist = []
        for t in tasklist:
            if isinstance(t, str):
                newlist.append({"task": t, "created": str(effective_date)})
            else:
                newlist.append(t)
        return newlist

    for topic, tasks in data["tasks"].get("突發區", {}).items():
        data["tasks"]["突發區"][topic] = convert_legacy_tasks(tasks)

    save_data(data)
    return data

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class TaskApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🗓 每日任務管理器")
        self.root.configure(bg=BG_COLOR)
        self.root.geometry("1200x800")

        # 新增 Scrollable Frame 架構
        self.canvas = tk.Canvas(self.root, bg=BG_COLOR, highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.pack(fill="both", expand=True)

        # 綁定滑鼠滾輪
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.data = load_data()
        self.labels = []
        self.undo_stack = []
        self.edit_mode = False
        self.build_ui()
        self.root.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        for lbl in self.labels:
            parent_width = lbl.master.winfo_width()
            lbl.config(wraplength=min(parent_width - 40, 400))

    def build_action_buttons(self):
        container = tk.Frame(self.root, bg=BG_COLOR)
        container.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

        # 第一行（匯入／匯出／回復）靠右上
        top_row = tk.Frame(container, bg=BG_COLOR)
        top_row.pack(anchor="e")

        # 第二行（其他按鈕）靠右下
        bottom_row = tk.Frame(container, bg=BG_COLOR)
        bottom_row.pack(anchor="e")

        def create_btn(parent, text, cmd):
            btn = tk.Button(
                parent, text=text, command=cmd,
                font=("標楷體", 12),
                bg="#3a3a3a", fg="#ffffff",
                relief="flat", padx=6, pady=4,
                width=10, height=1
            )
            btn.is_action_button = True
            btn.pack(side="right")
            return btn

        # 上行（匯出、匯入、回復）←從右到左
        create_btn(top_row, "📤 匯出", self.export_tasks)
        create_btn(top_row, "📥 匯入", self.import_tasks)
        create_btn(top_row, "🔙　回復", self.undo_last_task)  # 新增這一行

        # 下行（其他）
        create_btn(bottom_row, "📊 回顧", self.show_weekly_summary)
        create_btn(bottom_row, "📝 編輯", self.toggle_edit_mode)
        create_btn(bottom_row, "✅ 紀錄", self.show_completed_tasks)
        create_btn(bottom_row, "➕ 任務", self.add_task_dialog)

    def build_ui(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.labels.clear()

        # 重複區
        for cat in ["重複區"]:
            self.add_section_title(cat)
            row = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
            row.pack(anchor="w", padx=30, pady=2)
            for task in self.data["tasks"].get(cat, []):
                label_text = task
                days_info = self.get_days_since_completed(task)
                if not self.edit_mode:
                    label_text += f"{days_info}"
                lbl = self.create_label(row, label_text, cat)
                lbl.pack(side="left", padx=8)

        # 突發區 / 主線 / 支線
        for cat in ["突發區", "主線任務", "支線任務"]:
            self.add_section_title(cat)
            groups = self.data["tasks"].get(cat, {})
            for topic, subtasks in groups.items():
                topic_row = tk.Frame(self.scrollable_frame, bg=BG_COLOR)
                topic_row.pack(anchor="w", padx=30, pady=4)
                topic_lbl = tk.Label(topic_row, text=f"{topic}：", font=FONT_BOLD, bg=BG_COLOR, fg=TOPIC_COLOR, cursor="hand2")
                topic_lbl.pack(side="left")
                topic_lbl.bind("<Button-1>", lambda e, t=topic, c=cat: self.handle_topic_click(t, c))

                for sub in subtasks:
                    name = sub["task"] if isinstance(sub, dict) else sub
                    lbl = self.create_label(topic_row, name, cat, t=topic)
                    lbl.pack(side="left", padx=8)
        self.build_action_buttons()

    def add_section_title(self, name):
        title = tk.Label(self.scrollable_frame, text=f"\n--- {name} ---", font=("標楷體", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR)
        title.pack(anchor="w", padx=20)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def create_label(self, parent, task, category, t=None):
        fg = EDIT_COLOR if self.edit_mode else FG_COLOR
        lbl = tk.Label(
            parent,
            text=task,
            font=FONT,
            bg=BG_COLOR,
            fg=fg,
            cursor="hand2",
            wraplength=1,     # 初始設最小，等待 on_resize 調整
            justify="left",
            anchor="w"
        )
        if self.edit_mode:
            lbl.bind("<Button-1>", lambda e: self.delete_task(task, category, t))
        else:
            lbl.bind("<Button-1>", lambda e: self.complete_task(task, category, lbl, t))
        self.labels.append(lbl)
        return lbl

    def get_days_since_completed(self, task):
        today = date.today()
        completed_dates = {
            date.fromisoformat(r["timestamp"][:10])
            for r in self.data["completed"]
            if r["task"] == task and r["category"] == "重複區"
        }

        # 🧊 若今天完成，不顯示任何提示
        if today in completed_dates:
            return ""

        # 🔍 若「從來沒完成過」這個任務 → 初始觀察期，不顯示括號
        if not completed_dates:
            return ""

        # 🧭 若昨天有完成 → 今天是第一天沒做，不顯示括號
        yesterday = today.fromordinal(today.toordinal() - 1)
        if yesterday in completed_dates:
            return ""

        # 🧮 否則從昨天開始向前累計連續未完成天數
        streak = 1
        for i in range(2, 100):  # i=2 是前天
            d = today.fromordinal(today.toordinal() - i)
            if d in completed_dates:
                break
            streak += 1

        return f"({streak})"

    def show_weekly_summary(self):
        top = tk.Toplevel(self.root)
        top.title("📆 本週任務回顧")
        top.geometry("800x600")
        top.configure(bg=BG_COLOR)
        title = tk.Label(top, text="--- 重複區本週未完成統計 ---", font=FONT_BOLD, bg=BG_COLOR, fg=TOPIC_COLOR)
        title.pack(anchor="w", padx=20, pady=10)
        today = date.today()
        for task in DEFAULT_REPEAT_TASKS:
            days_missed = 0
            for i in range(7):
                check_date = today.toordinal() - i
                found = any(r["task"] == task and r["category"] == "重複區" and date.fromisoformat(r["timestamp"][:10]).toordinal() == check_date for r in self.data["completed"])
                if not found:
                    days_missed += 1
            if days_missed:
                tk.Label(top, text=f"{task}：缺席 {days_missed} 天", font=FONT, bg=BG_COLOR, fg=FG_COLOR).pack(anchor="w", padx=30)

        tk.Label(top, text="\n--- 突發區超過一週未完成 ---", font=FONT_BOLD, bg=BG_COLOR, fg=TOPIC_COLOR).pack(anchor="w", padx=20, pady=10)
        one_week_ago = date.today().toordinal() - 7
        for topic, subtasks in self.data["tasks"].get("突發區", {}).items():
            old_tasks = []
            for sub in subtasks:
                if isinstance(sub, dict):
                    created = sub.get("created")
                    if created and date.fromisoformat(created).toordinal() <= one_week_ago:
                        old_tasks.append(sub.get("task"))
            if old_tasks:
                msg = f"{topic}：{', '.join(old_tasks)}"
                tk.Label(top, text=msg, font=FONT, bg=BG_COLOR, fg=FG_COLOR, wraplength=760).pack(anchor="w", padx=30, pady=4)

    def delete_task(self, task, category, topic=None):
        if topic:
            self.data["tasks"][category][topic] = [t for t in self.data["tasks"][category][topic] if (t.get("task") if isinstance(t, dict) else t) != task]
        else:
            self.data["tasks"][category] = [t for t in self.data["tasks"][category] if (t.get("task") if isinstance(t, dict) else t) != task]
        save_data(self.data)
        self.build_ui()

    def complete_task(self, task, category, label, topic=None):
        label.config(fg=FG_GRAY)
        self.undo_stack.append((task, category, topic))
        if topic:
            self.data["tasks"][category][topic] = [t for t in self.data["tasks"][category][topic] if (t.get("task") if isinstance(t, dict) else t) != task]
        else:
            self.data["tasks"][category] = [t for t in self.data["tasks"][category] if (t.get("task") if isinstance(t, dict) else t) != task]
        self.data["completed"].append({
            "task": task,
            "category": category,
            "topic": topic if topic else "",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        save_data(self.data)
        self.root.after(500, label.destroy)

    def undo_last_task(self):
        if not self.undo_stack:
            return
        task, category, topic = self.undo_stack.pop()
        if topic:
            self.data["tasks"][category].setdefault(topic, []).append(task)
        else:
            self.data["tasks"][category].append(task)
        self.data["completed"] = [c for c in self.data["completed"] if c.get("task") != task]
        save_data(self.data)
        self.build_ui()

    def add_task_dialog(self):
        def on_submit(category, topic, task):
            if category in ["主線任務", "支線任務", "突發區"]:
                self.data["tasks"][category].setdefault(topic or "未分類", []).append({
                    "task": task,
                    "created": str(date.today())
                })
            else:
                self.data["tasks"][category].append(task)
            save_data(self.data)
            self.build_ui()

        TaskAddWindow(
            self.root,
            existing_data=self.data["tasks"],
            on_submit=on_submit
        )

    def toggle_edit_mode(self):
        self.edit_mode = not self.edit_mode
        self.build_ui()

    def show_completed_tasks(self):
        top = tk.Toplevel(self.root)
        top.title("✅ 已完成任務")
        top.geometry("800x600")
        top.configure(bg=BG_COLOR)
        title = tk.Label(top, text="--- 已完成任務 ---", font=("標楷體", 16, "bold"), bg=BG_COLOR, fg=FG_COLOR)
        title.pack(anchor="w", padx=20, pady=10)
        for item in self.data["completed"]:
            cat = item.get("category", "?")
            top_name = item.get("topic", "")
            msg = f"{item.get('task', '?')} [{cat}{(' - ' + top_name) if top_name else ''}] 🕒 {item.get('timestamp', '')}"
            tk.Label(top, text=msg, font=("標楷體", 12), anchor="w", bg=BG_COLOR, fg=FG_COLOR, wraplength=760).pack(padx=20, pady=4)

    def handle_topic_click(self, topic, category):
        if self.edit_mode:
            del self.data["tasks"][category][topic]
            save_data(self.data)
            self.build_ui()
            return
        if not self.data["tasks"][category][topic]:
            del self.data["tasks"][category][topic]
            save_data(self.data)
            self.build_ui()

    def import_tasks(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                imported_data = json.load(f)
        except Exception as e:
            messagebox.showerror("錯誤", f"讀取檔案失敗: {e}")
            return

        def merge_lists(base_list, new_list):
            return base_list + [item for item in new_list if item not in base_list]

        def merge_dict_lists(base_dict, new_dict):
            for k, v in new_dict.items():
                if k in base_dict:
                    base_dict[k] = merge_lists(base_dict[k], v)
                else:
                    base_dict[k] = v

        self.data["tasks"]["重複區"] = merge_lists(self.data["tasks"].get("重複區", []), imported_data.get("tasks", {}).get("重複區", []))

        for cat in ["突發區", "主線任務", "支線任務"]:
            if cat not in self.data["tasks"]:
                self.data["tasks"][cat] = {}
            imported_cat = imported_data.get("tasks", {}).get(cat, {})
            if isinstance(imported_cat, dict):
                merge_dict_lists(self.data["tasks"][cat], imported_cat)
            else:
                self.data["tasks"][cat] = {"未分類": merge_lists(self.data["tasks"][cat].get("未分類", []), imported_cat)}

        existing_done = {(c.get("task"), c.get("timestamp")) for c in self.data.get("completed", [])}
        new_done = [c for c in imported_data.get("completed", []) if (c.get("task"), c.get("timestamp")) not in existing_done]
        self.data["completed"].extend(new_done)

        save_data(self.data)
        self.build_ui()
        messagebox.showinfo("導入成功", "任務資料已成功合併並更新。")

    def export_tasks(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if not file_path:
            return
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("導出成功", f"任務資料已匯出到：{file_path}")
        except Exception as e:
            messagebox.showerror("錯誤", f"寫入檔案失敗: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskApp(root)
    root.mainloop()
