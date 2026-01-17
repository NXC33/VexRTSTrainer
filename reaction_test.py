import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import random
import time
import os
import csv
import subprocess
import sys


# ---------- THEME ----------
BG_COLOR = "#0f1115"
PANEL_COLOR = "#161a22"
TEXT_COLOR = "#e6e6eb"
SUBTEXT_COLOR = "#a0a3ad"
ACCENT_COLOR = "#3b82f6"
ERROR_COLOR = "#ef4444"

FONT_MAIN = ("Segoe UI", 16)
FONT_LARGE = ("Segoe UI Semibold", 22)
FONT_MONO = ("Consolas", 18)
# ---------------------------

# ---------- CONFIG ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_FOLDER = os.path.join(BASE_DIR, "images")
LABELS_FILE = os.path.join(BASE_DIR, "image_labels.csv")
RESULTS_FILE = os.path.join(BASE_DIR, "reaction_results.csv")
# ----------------------------


class ReactionTest:
    def __init__(self, root):
        self.root = root
        self.root.title("VEX Score Recognition Trainer")
        self.root.configure(bg=BG_COLOR)
        self.root.state("zoomed")

        # Force sane defaults for ALL widgets (prevents black-on-black labels)
        self.root.option_add("*Background", BG_COLOR)
        self.root.option_add("*Foreground", TEXT_COLOR)
        self.root.option_add("*Font", FONT_MAIN)
        self.root.option_add("*Label.Background", BG_COLOR)
        self.root.option_add("*Label.Foreground", SUBTEXT_COLOR)

        # ---------- Header ----------
        self.title_label = tk.Label(
            root,
            text="Score Recognition Trainer",
            font=FONT_LARGE,
            fg=TEXT_COLOR,
            bg=BG_COLOR
        )
        self.title_label.pack(pady=(18, 6))

        self.info_label = tk.Label(
            root,
            text="Type the score as: Red Blue  (example: 24 18)  then press Enter",
            font=FONT_MAIN,
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        )
        self.info_label.pack(pady=(0, 12))

        # ---------- Image Panel ----------
        self.image_frame = tk.Frame(root, bg=PANEL_COLOR, padx=6, pady=6)
        self.image_frame.pack(pady=10)

        self.image_label = tk.Label(self.image_frame, bg=PANEL_COLOR)
        self.image_label.pack()

        # ---------- Side Panel ----------
        self.side_panel = tk.Frame(
            root,
            bg=BG_COLOR
        )
        self.side_panel.place(
            relx=0.0, rely=0.5,
            anchor="w"
        )


        button_style = {
            "font": FONT_MAIN,
            "fg": TEXT_COLOR,
            "bg": "#1b2030",
            "activebackground": ACCENT_COLOR,
            "activeforeground": TEXT_COLOR,
            "relief": "flat",
            "width": 18,
            "padx": 10,
            "pady": 8
        }

        self.rename_button = tk.Button(
            self.side_panel,
            text="Rename Images",
            command=self.run_rename_images,
            **button_style
        )
        self.rename_button.pack(pady=(0, 12))

        self.label_button = tk.Button(
            self.side_panel,
            text="Build Labels",
            command=self.run_label_builder,
            **button_style
        )
        self.label_button.pack()
        self.stats_button = tk.Button(
            self.side_panel,
            text="View Timing Stats",
            command=self.run_time_visualizer,
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
        self.stats_button.pack(pady=(12, 0))


        # ---------- Input ----------
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
            highlightbackground="#2a2f3a",   # idle border
            highlightcolor=ACCENT_COLOR      # focused border
        )
        self.entry.pack(pady=(12, 8))
        self.entry.bind("<Return>", self.check_answer)

        # Small status line (so you always have visible text even during testing)
        self.status_label = tk.Label(
            root,
            text="",
            font=("Segoe UI", 13),
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        )
        self.status_label.pack(pady=(0, 14))

        self.images = self.load_images()
        if not self.images:
            self.info_label.config(
                text="No labeled matches found.\nClick 'Build Labels' to create the CSV.",
                fg=SUBTEXT_COLOR
            )
            return

        self.start_time = None
        self.correct_answer = None
        self.current = None

        self.root.bind("<FocusIn>", self.on_focus)
        self.show_new_image()
        


    def reset_info_text(self):
        self.info_label.config(
            text="Type the score as: Red Blue  (example: 24 18)  then press Enter",
            fg=SUBTEXT_COLOR,
            bg=BG_COLOR
        )
    def reload_labels(self):
        self.images = self.load_images()

        if not self.images:
            self.info_label.config(
                text="No labeled matches found.\nClick 'Build Labels' to create the CSV.",
                fg=SUBTEXT_COLOR
            )
            self.entry.config(state="disabled")
            self.image_label.config(image="")
            return

        # Labels now exist
        self.entry.config(state="normal")
        self.show_new_image()

    def load_images(self):
        images = []

        try:
            with open(LABELS_FILE, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    image_path = os.path.join(IMAGE_FOLDER, row["filename"])
                    if os.path.exists(image_path):
                        images.append({
                            "path": image_path,
                            "red": row["red_score"],
                            "blue": row["blue_score"]
                        })
        except FileNotFoundError:
            messagebox.showerror("Error", f"Could not find {LABELS_FILE}")
            self.root.destroy()
            return []

        if not images:
            return []


        return images

    def get_scaled_size(self):
        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        usable_height = int(screen_h * 0.6)
        width = int(usable_height * 4 / 3)
        height = usable_height

        if width > int(screen_w * 0.90):
            width = int(screen_w * 0.90)
            height = int(width * 3 / 4)

        return (width, height)

    def show_new_image(self):
        self.entry.delete(0, tk.END)
        self.reset_info_text()

        self.current = random.choice(self.images)
        self.correct_answer = f"{self.current['red']} {self.current['blue']}"

        img = Image.open(self.current["path"])
        img = img.resize(self.get_scaled_size())
        self.tk_img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_img)

        self.start_time = time.time()
        self.status_label.config(text="")

        # Debug line you can remove later:
        # print("Label fg:", self.info_label.cget("fg"), "bg:", self.info_label.cget("bg"))

    def check_answer(self, event=None):
        user_input = self.entry.get().strip()

        if user_input != self.correct_answer:
            messagebox.showwarning(
                "Incorrect",
                f"Wrong.\n\nCorrect score was: {self.correct_answer}\nYou typed: {user_input or '(blank)'}"
            )
            self.entry.delete(0, tk.END)
            self.reset_info_text()
            self.show_new_image()
            return

        reaction_time = time.time() - self.start_time
        self.save_result(reaction_time)

        self.info_label.config(
            text=f"Correct • {reaction_time:.3f}s",
            fg=ACCENT_COLOR,
            bg=BG_COLOR
        )
        self.status_label.config(text=f"Saved: {reaction_time:.3f}s")

        self.entry.delete(0, tk.END)
        self.show_new_image()

    def save_result(self, reaction_time):
        file_exists = os.path.isfile(RESULTS_FILE)
        with open(RESULTS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "reaction_time"])
            writer.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), reaction_time])
    def run_rename_images(self):
        subprocess.Popen([sys.executable, "rename_images.py"])
    def run_time_visualizer(self):
        subprocess.Popen([sys.executable, "time_visualizer.py"])


    def run_label_builder(self):
        # Launch label builder
        self._label_proc = subprocess.Popen([sys.executable, "build_labels.py"])

        # Immediately start checking until it closes
        self.check_label_builder_closed()
    def check_label_builder_closed(self):
        if getattr(self, "_label_proc", None) is None:
            return

        # poll() returns None while still running
        if self._label_proc.poll() is None:
            self.root.after(200, self.check_label_builder_closed)
            return

        # Labeler is closed -> CSV is definitely written -> reload now
        self._label_proc = None
        self.reload_labels()

    def on_focus(self, event=None):
        # Delay reload slightly to allow CSV writes to finish
        self.root.after(300, self.reload_labels)




if __name__ == "__main__":
    root = tk.Tk()
    app = ReactionTest(root)
    root.mainloop()