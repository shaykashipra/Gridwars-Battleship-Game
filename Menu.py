import tkinter as tk
import subprocess
import sys

def open_pygame(button_label):
    root.destroy()  

    print(f"Launching BattleShip_GUI.py with {button_label}...")



    subprocess.Popen([sys.executable, "BattleShip_GUI.py", button_label])
    print("Subprocess started.")
root = tk.Tk()
root.title("Menu Window")
root.geometry("800x600")

# Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
DARK_GRAY = "#282828"
LIGHT_BLUE = "#ADD8E6"
LIGHT_GREEN = "#90EE90"
GRAY = "#C8C8C8"

# Set the background color
root.configure(bg=DARK_GRAY)

# Fonts
font_title = ("Helvetica", 36)
font_button = ("Helvetica", 18)
font_label = ("Helvetica", 24)

# Title
title_label = tk.Label(root, text=" Gridwars BattleShip", font=font_title, bg=DARK_GRAY, fg=WHITE)
title_label.pack(pady=20)

# Frame to contain buttons in two columns
frame = tk.Frame(root, bg=DARK_GRAY)
frame.pack(pady=20)

# Column headings
level_label = tk.Label(frame, text="Level", font=font_label, bg=DARK_GRAY, fg=WHITE)
level_label.grid(row=0, column=0, padx=20, pady=10)
gameplay_label = tk.Label(frame, text="GamePlay", font=font_label, bg=DARK_GRAY, fg=WHITE)
gameplay_label.grid(row=0, column=1, padx=20, pady=10)

# Create buttons data
buttons_data = [
    ("Easy", "1", WHITE, 1, 0),
    ("Medium", "2", LIGHT_BLUE, 2, 0),
    ("Hard", "3", LIGHT_GREEN, 3, 0),
    ("Battle1-hvf", "4", LIGHT_BLUE, 1, 1),
    ("Battle2-hvm", "5", LIGHT_GREEN, 2, 1),
    ("Battle3-fvm", "6", WHITE, 3, 1)
]

def create_button(text, command, color):
    return tk.Button(frame, text=text, font=font_button, bg=color, fg=BLACK, command=command, width=12, height=2)

# Create button widgets and place them in the grid
for text, label, color, row, column in buttons_data:
    button = create_button(text, lambda l=label: open_pygame(l), color)
    button.grid(row=row, column=column, padx=20, pady=10)

root.mainloop()