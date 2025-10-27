import os
import sys
import subprocess
import tkinter as tk
from PIL import Image, ImageTk
from lists import item_images, orte
from tkinter import messagebox as mb

ROWS = 18  # number of rows per side
LEFT_NAME_COL = 0
RIGHT_NAME_COL = 6
LEFT_GOSSIP_COLS = range(2, 6)   # 2,3,4,5
RIGHT_GOSSIP_COLS = range(7, 11) # 7,8,9,10
GOSSIP_SIZE = (20, 20)


class LocationTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ishizakis Location Tracker")
        self.root.configure(bg="black")
        self.root.resizable(False, False)
        self.base_path = os.path.join(os.path.dirname(__file__), "images")

        self._load_gossip_image()
        self._create_menu()
        self.main_frame = tk.Frame(self.root, bg="black")
        # kein Rand mehr: kein padx/pady hier
        self.main_frame.pack(fill="both", expand=True)

        self._create_name_columns()
        self._create_gossip_grids()
        self._enable_preselected_dragging()

        # Fenstergröße automatisch an den Inhalt anpassen, damit kein Rand entsteht
        self.root.update_idletasks()
        w = self.main_frame.winfo_reqwidth()
        h = self.main_frame.winfo_reqheight()
        # setze geometry exakt auf benötigte Größe
        self.root.geometry(f"{w}x{h}")

    def _load_gossip_image(self):
        path = os.path.join(self.base_path, "Miscellaneous", "Gossip-Stone.png")
        img = Image.open(path).resize(GOSSIP_SIZE, Image.LANCZOS)
        self.gossip_photo = ImageTk.PhotoImage(img)

    def _create_menu(self):
        menubar = tk.Menu(self.root)
        program_menu = tk.Menu(menubar, tearoff=0)

        def _do_restart():
            try:
                subprocess.Popen([sys.executable] + sys.argv)
                self.root.quit()
            except Exception as e:
                mb.showerror("Restart failed", f"Could not restart application:\n{e}")

        def _confirm_restart():
            if mb.askyesno("Restart", "Restart application? Unsaved changes will be lost."):
                _do_restart()

        program_menu.add_command(label="Restart", accelerator="Ctrl+R", command=_confirm_restart)
        program_menu.add_separator()
        program_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.root.quit)
        menubar.add_cascade(label="Program", menu=program_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=lambda: mb.showinfo("About", "Ishizakis Location Tracker"))
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        # Global shortcuts
        self.root.bind_all("<Control-r>", lambda e: _confirm_restart())
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())

    def _create_name_columns(self):
        # left names (first ROWS entries)
        for i, name in enumerate(orte[:ROWS]):
            lbl = tk.Label(self.main_frame, text=name, font=("Helvetica", 12), bg="black", fg="white")
            lbl.grid(row=i, column=LEFT_NAME_COL, padx=1, pady=5)

        # right names (next entries, preserve original slicing up to index 35)
        right_slice = orte[ROWS:35]
        for i, name in enumerate(right_slice):
            lbl = tk.Label(self.main_frame, text=name, font=("Helvetica", 12), bg="black", fg="white")
            lbl.grid(row=i, column=RIGHT_NAME_COL, padx=1, pady=5)

    def _create_gossip_grids(self):
        # helper to create gossip cells and bind selector
        def make_gossip_cell(r, c):
            lbl = tk.Label(self.main_frame, image=self.gossip_photo, bg="black", cursor="hand2")
            lbl.image = self.gossip_photo  # prevent GC
            lbl.is_gossip = True
            lbl.grid(row=r, column=c, padx=1, pady=1)
            lbl.bind("<Double-Button-1>", lambda e, target=lbl: self._open_selector(target))
            return lbl

        # left side grids (rows 0..ROWS-1, cols LEFT_GOSSIP_COLS)
        for r in range(ROWS):
            for c in LEFT_GOSSIP_COLS:
                make_gossip_cell(r, c)

        # right side grids (rows 0..ROWS-1, cols RIGHT_GOSSIP_COLS)
        for r in range(ROWS):
            for c in RIGHT_GOSSIP_COLS:
                make_gossip_cell(r, c)

    def _open_selector(self, target_label):
        sel = tk.Toplevel(self.root)
        sel.title("Select Item")
        sel.configure(bg="black")
        sel.resizable(False, False)
        sel.transient(self.root)
        sel.grab_set()
        sel.focus_set()

        cols = 4
        row = col = 0
        for item, image_path in item_images.items():
            img = Image.open(image_path).resize(GOSSIP_SIZE, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            item_lbl = tk.Label(sel, image=photo, bg="black", cursor="hand2")
            item_lbl.image = photo
            item_lbl.grid(row=row, column=col, padx=4, pady=4)

            def choose(e, chosen_photo=photo, target=target_label):
                target.config(image=chosen_photo)
                target.image = chosen_photo
                # mark as non-gossip and enable dragging
                target.is_gossip = False
                target.bind("<Button-1>", self._on_drag_start)
                target.bind("<B1-Motion>", self._on_drag_motion)
                sel.destroy()

            item_lbl.bind("<Button-1>", choose)

            col += 1
            if col >= cols:
                col = 0
                row += 1

    # Dragging helpers
    def _on_drag_start(self, event):
        widget = event.widget
        widget._drag_data = {"x": event.x, "y": event.y}

    def _on_drag_motion(self, event):
        widget = event.widget
        dx = event.x - widget._drag_data["x"]
        dy = event.y - widget._drag_data["y"]
        x = widget.winfo_x() + dx
        y = widget.winfo_y() + dy
        # use place geometry to move freely over the main frame
        widget.place(in_=self.main_frame, x=x, y=y)

    def _enable_preselected_dragging(self):
        # Initially only enable dragging for non-gossip image labels (if any)
        for w in self.main_frame.winfo_children():
            if isinstance(w, tk.Label):
                # image labels will have an 'image' attribute; gossip labels have is_gossip True
                if getattr(w, "is_gossip", False):
                    continue
                if w.cget("image"):
                    w.bind("<Button-1>", self._on_drag_start)
                    w.bind("<B1-Motion>", self._on_drag_motion)


if __name__ == "__main__":
    root = tk.Tk()
    app = LocationTrackerApp(root)
    root.mainloop()
