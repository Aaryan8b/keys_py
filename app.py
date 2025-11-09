import tkinter as tk
from tkinter import ttk
import time
import json
from pathlib import Path
import numpy as np

from features import extract_features
from profile import build_profile, save_profile, load_profile
from score import standardized_manhattan

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

PHRASE = "neon-saffron-42"


class KeystrokeApp:
    def __init__(self, root):
        self.root = root
        root.title("Keystroke Dynamics Authentication")
        root.geometry("520x380")
        root.resizable(False, False)

        self.mode = tk.StringVar(value="enroll")
        self.user = tk.StringVar(value="alice")
        self.invalid = False
        self.allowed_keys = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-")

        # Header
        tk.Label(root, text="Keystroke Dynamics Auth", font=("Helvetica", 16, "bold")).pack(pady=10)
        tk.Label(root, text=f"Target phrase: {PHRASE}", font=("Helvetica", 11)).pack()

        # User + Mode
        user_frame = tk.Frame(root)
        user_frame.pack(pady=5)
        tk.Label(user_frame, text="User ID:").pack(side=tk.LEFT)
        tk.Entry(user_frame, textvariable=self.user, width=15).pack(side=tk.LEFT, padx=5)

        mode_frame = tk.Frame(root)
        mode_frame.pack()
        tk.Radiobutton(mode_frame, text="Enroll", variable=self.mode, value="enroll").pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(mode_frame, text="Verify", variable=self.mode, value="verify").pack(side=tk.LEFT, padx=10)

        # Typing box
        self.entry = tk.Entry(root, font=("Consolas", 14), width=30, justify="center")
        self.entry.pack(pady=20)
        self.entry.bind("<KeyPress>", self.on_keydown)
        self.entry.bind("<KeyRelease>", self.on_keyup)
        self.entry.bind("<Return>", self.on_submit)

        # Status + score bar
        self.status = tk.Label(root, text="Type the phrase and press Enter", font=("Helvetica", 10))
        self.status.pack(pady=5)

        # Configure green and red progress bar styles and set maximum to 3 (user-specified)
        style = ttk.Style()
        try:
            # Force the simpler 'default' theme so color settings are more likely to be honored
            style.theme_use('default')
        except Exception:
            pass

        # Green style (used for accepted scores)
        style.configure("Green.Horizontal.TProgressbar",
                        troughcolor="#f5f5f5",
                        background="#2ecc71",
                        bordercolor="#2ecc71",
                        lightcolor="#2ecc71",
                        darkcolor="#27ae60")
        style.map("Green.Horizontal.TProgressbar",
                  background=[('!disabled', '#2ecc71'), ('disabled', '#2ecc71')])

        # Red style (used for rejected scores)
        style.configure("Red.Horizontal.TProgressbar",
                        troughcolor="#f5f5f5",
                        background="#e74c3c",
                        bordercolor="#e74c3c",
                        lightcolor="#e74c3c",
                        darkcolor="#c0392b")
        style.map("Red.Horizontal.TProgressbar",
                  background=[('!disabled', '#e74c3c'), ('disabled', '#e74c3c')])

        # Start with green style by default
        self.score_bar = ttk.Progressbar(root, orient="horizontal", length=320, mode="determinate",
                                         maximum=3, style="Green.Horizontal.TProgressbar")
        self.score_bar.pack(pady=10)

        tk.Button(root, text="Reset", command=self.reset).pack(pady=5)

        # Internal key timing
        self.key_down_times = {}
        self.key_up_times = {}

    # -------------------------------
    # Handle key events
    # -------------------------------
    def on_keydown(self, event):
        key = event.keysym

        # Backspace = cancel sample immediately
        if key == "BackSpace":
            self.invalid = True
            self.status.config(text="⚠️ Backspace used — sample canceled.", fg="orange")
            self.reset_input()
            return

        # Record only allowed keys
        if len(key) == 1 and key in self.allowed_keys:
            self.key_down_times[key + str(time.time())] = time.time()

    def on_keyup(self, event):
        key = event.keysym
        if len(key) == 1 and key in self.allowed_keys:
            self.key_up_times[key + str(time.time())] = time.time()

    # -------------------------------
    # When Enter pressed → process sample
    # -------------------------------
    def on_submit(self, event=None):
        typed = self.entry.get().strip()

        # Cancel invalid typing
        if getattr(self, "invalid", False):
            self.status.config(text="⚠️ Typing correction detected — retry cleanly.", fg="orange")
            self.invalid = False
            self.reset_input()
            return

        # Wrong phrase
        if typed != PHRASE:
            self.status.config(text="❌ Incorrect phrase — type exactly.", fg="red")
            self.reset_input()
            return

        # Build ordered events
        events = []
        for k, t in self.key_down_times.items():
            events.append(("down", k, t))
        for k, t in self.key_up_times.items():
            events.append(("up", k, t))
        events.sort(key=lambda x: x[2])

        # If no typing detected
        if len(events) < 2:
            self.status.config(text="⚠️ No typing detected. Please type the phrase.", fg="orange")
            self.reset_input()
            return

        # Extract features safely
        features = extract_features(events, PHRASE)
        if features is None:
            self.status.config(text="⚠️ Invalid or incomplete sample. Please retype cleanly.", fg="orange")
            self.reset_input()
            return

        user = self.user.get().strip()
        if self.mode.get() == "enroll":
            self.handle_enroll(user, features)
        else:
            self.handle_verify(user, features)

        self.reset_input()

    # -------------------------------
    # Enrollment Logic
    # -------------------------------
    def handle_enroll(self, user, features):
        fpath = DATA_DIR / f"{user}_samples.json"
        samples = []
        if fpath.exists():
            try:
                content = fpath.read_text().strip()
                if content:
                    samples = json.loads(content)
                else:
                    samples = []
            except json.JSONDecodeError:
                print(f"[WARN] Corrupted {fpath}, resetting it.")
                samples = []

        # only add if same feature length
        if samples and len(features) != len(samples[0]):
            print(f"[SKIP] Mismatch feature len {len(features)} != {len(samples[0])}")
            self.status.config(text="⚠️ Sample skipped due to mismatch.", fg="orange")
            return

        samples.append(features)
        fpath.write_text(json.dumps(samples))

        profile = build_profile(samples)
        save_profile(user, profile)
        self.status.config(text=f"✅ Sample saved ({len(samples)} total)", fg="green")
        print(f"[ENROLL] user={user}, samples={len(samples)}")

    # -------------------------------
    # Verification Logic
    # -------------------------------
    def handle_verify(self, user, features):
        profile = load_profile(user)
        if not profile:
            self.status.config(text="❌ No profile found. Enroll first.", fg="red")
            return

        score = standardized_manhattan(features, profile['mu'], profile['sigma'])
        threshold = profile['threshold']
        accept = score <= threshold
        # clamp displayed score to the progress bar maximum (3)
        self.score_bar['value'] = min(score, 3)

        # switch bar color: green when accepted (score <= threshold), red otherwise
        self.score_bar.configure(style=("Green.Horizontal.TProgressbar" if accept else "Red.Horizontal.TProgressbar"))

        if accept:
            self.status.config(text=f"✅ Accepted (score={score:.1f})", fg="green")
        else:
            self.status.config(text=f"❌ Rejected (score={score:.1f})", fg="red")

        print(f"[VERIFY] user={user}, score={score:.2f}, accept={accept}")

    # -------------------------------
    # Reset Helpers
    # -------------------------------
    def reset_input(self):
        self.entry.delete(0, tk.END)
        self.key_down_times.clear()
        self.key_up_times.clear()
        self.invalid = False

    def reset(self):
        self.reset_input()
        self.status.config(text="Type the phrase and press Enter", fg="black")
        self.score_bar['value'] = 0


if __name__ == "__main__":
    root = tk.Tk()
    app = KeystrokeApp(root)
    root.mainloop()
