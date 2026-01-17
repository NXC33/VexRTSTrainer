import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import csv
import re
import subprocess
import sys


# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "images")
LABELS_FILE = os.path.join(BASE_DIR, "image_labels.csv")

IMAGE_PATTERN = re.compile(r"match_(\d+)\.(jpg|jpeg|png)", re.IGNORECASE)
# ----------------------------

# ---------- THEME ----------
BG_COLOR = "#0f1115"
PANEL_COLOR = "#161a22"
TEXT_COLOR = "#e6e6eb"
SUBTEXT_COLOR = "#a0a3ad"
ACCENT_COLOR = "#3b82f6"

FONT_MAIN = ("Segoe UI", 16)
FONT_LARGE = ("Segoe UI Semibold", 22)
FONT_MONO = ("Consolas", 18)
# ---------------------------


class LabelBuilder:
    def __init__(self, root):
        self.root = root
        self.root.title("Build Match Labels")
        self.root.configure(bg=BG_COLOR)
        self.root.state("zoomed")

        # ---------- UI ----------
        self.title_label = tk.Label(
            root,
            text="Match Label Builder",
            font=FONT_LARGE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.title_label.pack(pady=(16, 4))

        self.progress_label = tk.Label(
            root,
            font=FONT_MAIN,
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        )
        self.progress_label.pack(pady=(0, 12))

        self.image_frame = tk.Frame(root, bg=PANEL_COLOR, padx=6, pady=6)
        self.image_frame.pack(pady=10)

        self.image_label = tk.Label(self.image_frame, bg=PANEL_COLOR)
        self.image_label.pack()

        # ---------- Side Panel (Left) ----------
        self.side_panel = tk.Frame(root, bg=BG_COLOR)
        self.side_panel.place(relx=0.0, rely=0.5, anchor="w")

        self.back_button = tk.Button(
            self.side_panel,
            text="Back to Trainer",
            command=self.return_to_trainer,
            font=FONT_MAIN,
            fg=TEXT_COLOR,
            bg="#1b2030",
            activebackground=ACCENT_COLOR,
            activeforeground=TEXT_COLOR,
            relief="flat",
            width=18,
            padx=10,
            pady=8
        )
        self.back_button.pack()


        self.entry = tk.Entry(
            root,
            font=FONT_MONO,
            justify="center",
            width=12,
            fg=TEXT_COLOR,
            bg="#0b0d12",
            insertbackground=TEXT_COLOR,
            relief="solid",
            bd=2,
            highlightthickness=2,
            highlightbackground="#2a2f3a",
            highlightcolor=ACCENT_COLOR
        )
        self.entry.pack(pady=(12, 8))
        self.entry.bind("<Return>", self.save_label)

        self.status_label = tk.Label(
            root,
            text="Type: Red Blue  (example: 24 18)",
            font=FONT_MAIN,
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        )
        self.status_label.pack(pady=(0, 12))

        # ---------- Data ----------
        self.images = self.load_unlabeled_images()
        self.index = 0

        if not self.images:
            messagebox.showinfo("Done", "All images already have labels.")
            self.root.destroy()
            return

        self.show_current_image()

    # ---------- Data loading ----------
    def load_unlabeled_images(self):
        all_images = []
        labeled = set()

        # Read existing CSV
        if os.path.exists(LABELS_FILE):
            with open(LABELS_FILE, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    labeled.add(row["filename"])

        # Find all match_### images
        for file in os.listdir(IMAGE_FOLDER):
            if IMAGE_PATTERN.match(file):
                if file not in labeled:
                    all_images.append(file)

        # Sort numerically by match number
        def match_number(name):
            return int(IMAGE_PATTERN.match(name).group(1))

        all_images.sort(key=match_number)
        return all_images

    # ---------- Scaling ----------
    def get_scaled_size(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        usable_height = int(screen_h * 0.6)
        width = int(usable_height * 4 / 3)
        height = usable_height

        if width > int(screen_w * 0.95):
            width = int(screen_w * 0.95)
            height = int(width * 3 / 4)

        return (width, height)

    # ---------- UI logic ----------
    def show_current_image(self):
        self.entry.delete(0, tk.END)
        self.entry.focus_set()

        filename = self.images[self.index]
        path = os.path.join(IMAGE_FOLDER, filename)

        img = Image.open(path)
        img = img.resize(self.get_scaled_size())
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

        self.progress_label.config(
            text=f"Match {self.index + 1} / {len(self.images)}   ({filename})"
        )

    def save_label(self, event=None):
        user_input = self.entry.get().strip()

        if not re.match(r"^\d+\s+\d+$", user_input):
            messagebox.showwarning("Invalid input", "Use format: Red Blue")
            return

        red, blue = user_input.split()
        filename = self.images[self.index]

        file_exists = os.path.exists(LABELS_FILE)

        with open(LABELS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["filename", "red_score", "blue_score"])
            writer.writerow([filename, red, blue])

        self.index += 1

        if self.index >= len(self.images):
            messagebox.showinfo("Done", "All images labeled!")
            self.root.destroy()
            return

        self.show_current_image()
    def return_to_trainer(self):
        self.root.destroy()




if __name__ == "__main__":
    root = tk.Tk()
    app = LabelBuilder(root)
    root.mainloop()