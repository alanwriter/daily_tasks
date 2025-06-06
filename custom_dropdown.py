import tkinter as tk

class CustomDropdown(tk.Frame):
    def __init__(self, master, values=None, font=None, placeholder="", **kwargs):
        super().__init__(master, bg="#1e1e1e", **kwargs)
        self.values = values or []
        self.var = tk.StringVar()
        self.placeholder = placeholder
        self.font = font
        self.dropdown = None
        self.filtered = []
        self.listener_bound = False
        self.root = self.winfo_toplevel()

        self.entry = tk.Entry(self, textvariable=self.var, font=font,
                              bg="#2a2a2a", fg="#ffffff", insertbackground="#ffffff", relief="flat")
        self.entry.pack(fill="x", padx=1, pady=1)
        self.entry.insert(0, placeholder)

        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.check_focus_out)
        self.entry.bind("<KeyRelease>", self.filter_dropdown)
        self.entry.bind("<Button-1>", self.on_click)

    def on_click(self, event=None):
        if self.var.get() == self.placeholder:
            self.var.set("")
        self.show_dropdown()

    def on_focus_in(self, event=None):
        if self.var.get() == self.placeholder:
            self.var.set("")

    def check_focus_out(self, event=None):
        self.after(200, self.destroy_dropdown)

    def show_dropdown(self):
        if self.dropdown:
            self.dropdown.destroy()

        self.dropdown = tk.Toplevel(self)
        self.dropdown.wm_overrideredirect(True)
        self.dropdown.configure(bg="#2a2a2a")

        x = self.winfo_rootx()
        y = self.winfo_rooty() + self.winfo_height()
        self.dropdown.wm_geometry(f"{self.winfo_width()}x150+{x}+{y}")

        canvas = tk.Canvas(self.dropdown, bg="#2a2a2a", highlightthickness=0)
        frame = tk.Frame(canvas, bg="#2a2a2a")

        frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame, anchor="nw")

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<Enter>", lambda e: canvas.bind("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda e: canvas.unbind("<MouseWheel>"))


        canvas.pack(fill="both", expand=True)

        keyword = self.var.get().strip().lower()
        self.filtered = [v for v in self.values if keyword in v.lower()] if keyword else self.values
        for v in self.filtered:
            lbl = tk.Label(frame, text=v, font=self.font, bg="#2a2a2a", fg="#ffffff",
                           anchor="w", padx=6, pady=2, cursor="hand2")
            lbl.pack(fill="x")
            lbl.bind("<Button-1>", lambda e, val=v: self.select_value(val))

        if not self.listener_bound:
            self.root.bind("<Button-1>", self.check_click_outside, add="+")
            self.listener_bound = True

    def filter_dropdown(self, event=None):
        if self.dropdown:
            self.dropdown.destroy()
        self.show_dropdown()

    def select_value(self, value):
        self.var.set(value)
        self.destroy_dropdown()

    def check_click_outside(self, event):
        if not self.dropdown:
            return
        widget = event.widget
        if widget == self.entry or str(widget).startswith(str(self.dropdown)):
            return
        self.destroy_dropdown()

    def destroy_dropdown(self):
        if self.dropdown:
            self.dropdown.destroy()
            self.dropdown = None

        if self.listener_bound:
            print("🔓 解鎖主畫面點擊控制")
            self.root.unbind("<Button-1>", funcid=None)
            self.listener_bound = False

    def get(self):
        return self.var.get().strip()
