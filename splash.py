#------------------------------------------Priyancy-Loading------------------------------------------#
import tkinter as tk
from itertools import cycle
import subprocess

class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Loading Deadlock Simulator")
        self.geometry("500x400")
        self.configure(bg="#e6b3f7")
        self.resizable(False, False)
        self.overrideredirect(True)  # Hide window decorations

        # Center window
        self.update_idletasks()
        w = 500
        h = 400
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Title
        self.label_title = tk.Label(
            self,
            text="DEADLOCK\nSIMULATOR",
            font=("Consolas", 32, "bold"),
            fg="black",
            bg="#e6b3f7",
            justify="center"
        )
        self.label_title.pack(pady=(70, 10))

        # Loading spinner (dots)
        self.spinner_frames = [
            "■ □ □ □ □ □ □ □",
            "□ ■ □ □ □ □ □ □",
            "□ □ ■ □ □ □ □ □",
            "□ □ □ ■ □ □ □ □",
            "□ □ □ □ ■ □ □ □",
            "□ □ □ □ □ ■ □ □",
            "□ □ □ □ □ □ ■ □",
            "□ □ □ □ □ □ □ ■",
        ]
        self.spinner_cycle = cycle(self.spinner_frames)
        self.label_spinner = tk.Label(self, text="", font=("Consolas", 22), bg="#e6b3f7")
        self.label_spinner.pack(pady=(0, 10))

        # Animated dots
        self.dot_states = ["Loading.", "Loading..", "Loading..."]
        self.dot_cycle = cycle(self.dot_states)
        self.label_dots = tk.Label(self, text="", font=("Consolas", 20, "bold"), bg="#e6b3f7")
        self.label_dots.pack(pady=(10, 0))

        self.after(0, self.animate)
        # Launch intro after 3.6 seconds
        self.after(3600, lambda: self.start_intro())

    def animate(self):
        self.label_spinner.config(text=next(self.spinner_cycle))
        self.label_dots.config(text=next(self.dot_cycle))
        self.after(250, self.animate)

    def start_intro(self):
        self.destroy()  # close splash
        subprocess.run(["python", "intro.py"])  # run intro

if __name__ == "__main__":
    splash = SplashScreen()
    splash.mainloop()
