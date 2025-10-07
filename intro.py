import tkinter as tk
import pygame
import subprocess
import os

class IntroApp:
    def __init__(self, root):
        self.root = root
        self.root.configure(bg="#6f0094")
        self.root.geometry("550x450")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        # --- Center the window ---
        w, h = 550, 450
        x = (self.root.winfo_screenwidth() // 2) - (w // 2)
        y = (self.root.winfo_screenheight() // 2) - (h // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

        # === 🎵 Init pygame mixer for sound ===
        pygame.mixer.init()
        pygame.mixer.music.load("BGG.mp3")   # your background music file
        pygame.mixer.music.play()  # loop forever

        # Optional: load click sound (short wav/mp3)
        if os.path.exists("click.wav"):
            self.click_sound = pygame.mixer.Sound("click.wav")
        else:
            self.click_sound = None

        # Load character images
        self.char_open = tk.PhotoImage(file="105.png")
        self.char_close = tk.PhotoImage(file="101.png")

        # Character label in the center
        self.character_label = tk.Label(self.root, image=self.char_close, bg="#df7fff")
        self.character_label.place(relx=0.5, rely=0.4, anchor="center")

        # Intro lines
        self.intro_lines = [
            "Hi! I'm your guide for the Deadlock Simulator.",
            "Deadlocks happen when processes wait forever for resources.",
            "I’ll show you how to detect and recover from deadlocks.",
            "Let’s explore together!"
        ]
        self.current_line = 0

        # Text label below character (centered)
        self.text_label = tk.Label(
            self.root,
            text=self.intro_lines[self.current_line],
            font=("Consolas", 14),
            fg="White",
            bg="#6f0094",
            wraplength=500,
            justify="center"
        )
        self.text_label.place(relx=0.5, rely=0.7, anchor="center")

        # Navigation buttons (below text, centered)
        self.left_btn = tk.Button(
            self.root, text="◀", command=self.prev_line,
            font=("Consolas", 12), bg="#df7fff"
        )
        self.left_btn.place(relx=0.4, rely=0.85, anchor="center")

        self.right_btn = tk.Button(
            self.root, text="▶", command=self.next_line,
            font=("Consolas", 12), bg="#df7fff"
        )
        self.right_btn.place(relx=0.6, rely=0.85, anchor="center")

        # Start mouth animation
        self.mouth_open = False
        self.animate_mouth()

    def animate_mouth(self):
        if self.mouth_open:
            self.character_label.config(image=self.char_close)
        else:
            self.character_label.config(image=self.char_open)
        self.mouth_open = not self.mouth_open
        self.root.after(400, self.animate_mouth)

    def update_text(self):
        self.text_label.config(text=self.intro_lines[self.current_line])

    def next_line(self):
        if self.click_sound:
            self.click_sound.play()  # 🔊 play click on right button
        if self.current_line < len(self.intro_lines) - 1:
            self.current_line += 1
            self.update_text()
        else:
            # End of intro → stop music, close, and move to simulator
            pygame.mixer.music.stop()
            self.root.destroy()
            subprocess.run(["python", "Moko.py"])

    def prev_line(self):
        if self.click_sound:
            self.click_sound.play()  # 🔊 play click on left button
        if self.current_line > 0:
            self.current_line -= 1
            self.update_text()



if __name__ == "__main__":
    root = tk.Tk()
    app = IntroApp(root)
    root.mainloop()
